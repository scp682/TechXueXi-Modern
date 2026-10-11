from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from contextlib import ExitStack

APP = Path(__file__).resolve().parents[1] / 'SourcePackages'
sys.path.insert(0, str(APP))
sys.argv[0] = str(APP / 'pandalearning.py')
import pandalearning
from pdlearn.mydriver import Mydriver
from pdlearn.score import parse_tasks, task_progress, task_target, format_score
from pdlearn.get_links import links_from_feed, get_video_links
from pdlearn.article_video import learn_content
from pdlearn.daily_practice import hints_from_html, match_options


def fixture_scores(article=0, video=0):
    return parse_tasks({'totalScore': 1 + article + video, 'taskProgress': [
        {'title':'文章', 'taskCode':['1','1002'], 'currentScore':article,'dayMaxScore':12},
        {'title':'视频', 'taskCode':['2','1003'], 'currentScore':video,'dayMaxScore':12},
        {'title':'登录', 'taskCode':['9'], 'currentScore':1,'dayMaxScore':1},
        {'title':'每日答题', 'taskCode':['6'], 'currentScore':0,'dayMaxScore':5}]})


class CurrentSiteTests(unittest.TestCase):
    def test_combined_scores_are_not_divided(self):
        scores = fixture_scores(article=3)
        self.assertEqual(task_progress(scores, 'article'), (3, 12))
        self.assertIsNone(scores['article_num'])
        self.assertIsNone(scores['article_time'])
        self.assertEqual(task_target(scores, 'weekly'), 0)
        self.assertNotIn('每周', format_score(4, scores, colorful=False))

    def test_task_code_is_exact_not_substring(self):
        scores = parse_tasks({'taskProgress':[{'title':'时长', 'taskCode':'1002',
                             'currentScore':2, 'dayMaxScore':6}]})
        self.assertEqual(scores['article_time'], 2)
        self.assertEqual(scores['article_num'], 0)
        self.assertEqual(task_progress(scores, 'article'), (2, 6))

    def test_verification_required_stops(self):
        for flag in ('inBlackList', 'needFaceRecognition'):
            with self.assertRaises(RuntimeError):
                parse_tasks({flag:True, 'taskProgress':[]})

    def test_invalid_structure_stops(self):
        with self.assertRaises(RuntimeError):
            parse_tasks({'taskProgress':None})

    def test_cookie_domains_preserved_without_navigation(self):
        browser = Mydriver.__new__(Mydriver)
        browser.driver = Mock()
        browser.driver.execute_cdp_cmd.return_value = {'success':True}
        cookies = [{'name':'token', 'value':'fixture','domain':'.xuexi.cn','expiry':9999999999},
                   {'name':'host','value':'fixture','domain':'pc.xuexi.cn','path':'/points'},
                   {'name':'bad','value':'fixture','domain':'xuexi.cn.example.org'},
                   {'name':'expired','value':'fixture','domain':'.xuexi.cn','expiry':1}]
        self.assertEqual(browser.set_cookies(cookies), 2)
        calls = browser.driver.execute_cdp_cmd.call_args_list
        self.assertEqual(calls[0][0][1]['domain'], '.xuexi.cn')
        self.assertEqual(calls[1][0][1]['domain'], 'pc.xuexi.cn')
        self.assertIn('expires', calls[0][0][1])
        self.assertNotIn('expires', cookies[0])
        browser.driver.get.assert_not_called()
        browser.driver.add_cookie.assert_not_called()

    def test_cookie_failure_is_not_silently_ignored(self):
        browser = Mydriver.__new__(Mydriver)
        browser.driver = Mock()
        browser.driver.execute_cdp_cmd.return_value = {'success':False}
        with self.assertRaises(RuntimeError):
            browser.set_cookies([{'domain':'.xuexi.cn','name':'token','value':'fixture'}])

    def test_newest_deduplicated_feed_filters_non_videos_and_offsite(self):
        rows = [
            {'url':'https://www.xuexi.cn/old','publishTime':'2025','itemType':'kPureVideo'},
            {'url':'https://evil.org/bad','publishTime':'2027','itemType':'kPureVideo'},
            {'url':'https://www.xuexi.cn/news','publishTime':'2027','itemType':'kNews'},
            {'url':'https://www.xuexi.cn/new','publishTime':'2026','itemType':'kVideo'},
            {'url':'https://www.xuexi.cn/new','publishTime':'2026','itemType':'kVideo'}]
        self.assertEqual(links_from_feed(rows, video=True),
                         ['https://www.xuexi.cn/new','https://www.xuexi.cn/old'])

    def test_feed_failure_is_bounded_and_falls_back(self):
        with patch('pdlearn.get_links.public_feed', side_effect=[ValueError('HTML'),
                  [{'url':'https://www.xuexi.cn/video','itemType':'kPureVideo'}]]) as feed:
            self.assertEqual(get_video_links(), ['https://www.xuexi.cn/video'])
            self.assertEqual(feed.call_count, 2)

    def test_no_progress_is_bounded_and_browser_always_closed(self):
        scores = fixture_scores()
        browser = Mock()
        with patch('pdlearn.article_video.Mydriver', return_value=browser), \
             patch('pdlearn.article_video.get_links.get_article_links', return_value=[
                 'https://www.xuexi.cn/a','https://www.xuexi.cn/b','https://www.xuexi.cn/c']), \
             patch('pdlearn.article_video.browse_once') as browse, \
             patch('pdlearn.article_video.get_score', return_value=('fixture',1,scores,'')), \
             patch('pdlearn.article_video.user.save_article_index'), \
             patch('pdlearn.article_video.time.sleep'):
            self.assertFalse(learn_content('article','fixture',[],999,scores))
            self.assertEqual(browse.call_count, 3)
        browser.quit.assert_called_once()

    def test_error_closes_browser(self):
        browser = Mock()
        with patch('pdlearn.article_video.Mydriver', return_value=browser), \
             patch('pdlearn.article_video.get_links.get_article_links', side_effect=RuntimeError('fixture')):
            self.assertFalse(learn_content('article','fixture',[],0,fixture_scores()))
        browser.quit.assert_called_once()

    def test_missing_or_completed_task_does_not_start_browser(self):
        with patch('pdlearn.article_video.Mydriver') as driver:
            self.assertTrue(learn_content('article','fixture',[],0,fixture_scores(article=12)))
            driver.assert_not_called()

    def test_hint_matching_does_not_confuse_negated_option(self):
        hints = hints_from_html('<div>海平面<font color="red">不是</font>平的。</div>')
        self.assertEqual(hints, ['不是'])
        self.assertEqual(match_options(['A. 是','B. 不是'], hints), [1])
        self.assertEqual(match_options(['A. 不是','B. 不是'], hints), [])
        self.assertEqual(match_options(['A. 是','B. 不是'], []), [])

    def test_multi_select_requires_explicit_multiple_matches(self):
        self.assertEqual(match_options(['A. 苹果','B. 香蕉','C. 橙子'], ['苹果','香蕉'], True), [0,1])
        self.assertEqual(match_options(['A. 苹果','B. 香蕉'], ['苹果'], True), [])

    def test_true_false_requires_full_quoted_statement(self):
        statement = '经营者应当按照法律法规和食品安全标准采取相应措施保证食品安全'
        question = '根据《测试规定》，' + statement + '。（）'
        self.assertEqual(match_options(['A. 正确','B. 错误'], [statement], question=question), [0])
        self.assertEqual(match_options(['A. 正确','B. 错误'], [statement],
                         question=question+'\n来源：测试书籍'), [0])
        self.assertEqual(match_options(['A. 正确','B. 错误'], ['保证食品安全'], question=question), [])

    def test_tls_failure_uses_browser_and_always_closes_it(self):
        from pdlearn import score
        import requests
        browser = Mock()
        expected = ('fixture', 1, fixture_scores(), '')
        with patch('pdlearn.score._get_score', side_effect=[requests.exceptions.SSLError(), expected]), \
             patch('pdlearn.mydriver.Mydriver', return_value=browser):
            self.assertEqual(score.get_score([{'fixture':True}]), expected)
        browser.set_cookies.assert_called_once()
        browser.quit.assert_called_once()

    def test_start_uses_current_daily_task_and_skips_removed_quizzes(self):
        scores = fixture_scores()
        order = []
        replacements = {
            'get_argv': Mock(return_value=(False,False,None,False)),
            'cfg_get': Mock(return_value=3),
            'user.get_cookie': Mock(return_value=[{'fixture':True}]),
            'user.get_article_index': Mock(return_value=0),
            'user.get_video_index': Mock(return_value=0),
            'show_score': Mock(return_value=(1,scores)),
            'show_scorePush': Mock(return_value=(1,scores)),
            'gl.pushprint': Mock(), 'user.shutdown': Mock(),
            'article': Mock(side_effect=lambda *a:order.append('article')),
            'video': Mock(side_effect=lambda *a:order.append('video')),
            'daily': Mock(side_effect=lambda *a:order.append('daily')),
            'weekly': Mock(), 'zhuanxiang': Mock()}
        with ExitStack() as stack:
            for name, value in replacements.items():
                stack.enter_context(patch('pandalearning.'+name, value))
            pandalearning.start_learn('fixture','fixture')
        self.assertEqual(order, ['article','video','daily'])
        replacements['weekly'].assert_not_called()
        replacements['zhuanxiang'].assert_not_called()


if __name__ == '__main__':
    unittest.main()
