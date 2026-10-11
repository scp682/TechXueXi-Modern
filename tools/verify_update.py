"""Browser integration check. No secrets or account identifiers in output."""
from pathlib import Path
import sys
import time
from inspect_current_site import cookies_local

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'SourcePackages'
LIVE = '--live' in sys.argv
QUIZ = '--quiz' in sys.argv
HEADED = '--headed' in sys.argv
QUIZ_RUN = '--quiz-run' in sys.argv
VIDEO_ONLY = '--video-only' in sys.argv
VIDEO_INDEX = int(next((v.split('=', 1)[1] for v in sys.argv if v.startswith('--video-index=')), '0'))
REQUESTS_CHECK = '--requests-check' in sys.argv
sys.path.insert(0, str(APP))
sys.argv[0] = str(APP / 'pandalearning.py')
import pandalearning
from pdlearn.mydriver import Mydriver
from pdlearn import get_links
from pdlearn.score import DAY_URL, parse_tasks, task_progress, get_score
from pdlearn.article_video import prepare_content, browse_once

def read_scores(browser):
    return parse_tasks(browser.get_json(DAY_URL)['data'])

if __name__ == '__main__':
    browser = Mydriver(nohead=not HEADED)
    try:
        cookies = cookies_local()
        print('COOKIES_APPLIED:', browser.set_cookies(cookies), flush=True)
        browser.get_url('https://www.xuexi.cn/')
        before = read_scores(browser)
        print('TASKS:', [(t['title'], t['current'], t['target']) for t in before['_tasks']], flush=True)
        _, total, full_scores, _ = get_score(cookies, browser=browser)
        print('FULL_SCORE_CHECK:', full_scores['today'], flush=True)
        if REQUESTS_CHECK:
            _, _, standard_scores, _ = get_score(cookies)
            print('STANDARD_SCORE_CHECK:', standard_scores['today'], flush=True)
        if QUIZ_RUN:
            from pdlearn.daily_practice import practice
            print('PRACTICE_RESULT:', practice(cookies, before, driver_default=browser), flush=True)
        elif QUIZ:
            browser.get_url('https://pc.xuexi.cn/points/exam-practice.html')
            time.sleep(8)
            print('PRACTICE_PAGE:', browser.driver.title, flush=True)
            print('PRACTICE_DOM:', browser.driver.execute_script('''
                return {buttons:Array.from(document.querySelectorAll('button')).map(e=>e.innerText),
                  types:Array.from(document.querySelectorAll('[class]')).filter(e=>
                    /q-|practice|question|category/.test(e.className)).slice(0,30)
                    .map(e=>({tag:e.tagName,cls:e.className})),
                  iframes:Array.from(document.querySelectorAll('iframe')).map(e=>e.src.split('?')[0])};
            '''), flush=True)
            print('QUESTION_DOM:', browser.driver.execute_script(
                "return document.querySelector('.question')?.outerHTML.slice(0,12000)"), flush=True)
        else:
            articles = get_links.get_article_links(browser)
            videos = get_links.get_video_links(browser)
            print('CURRENT_CONTENT:', len(articles), len(videos), flush=True)
            browser.get_url(videos[VIDEO_INDEX])
            print('VIDEO_URL:', videos[VIDEO_INDEX], flush=True)
            print('VIDEO_READY:', prepare_content(browser, 'video'), flush=True)
        if LIVE:
            sequence = [('video', videos)] if VIDEO_ONLY else [('video', videos), ('article', articles)]
            for kind, links in sequence:
                browser.get_url(links[VIDEO_INDEX if kind == 'video' else 0])
                print('LIVE_START:', kind, flush=True)
                browse_once(browser, kind)
                browser.get_url('https://pc.xuexi.cn/points/my-points.html')
                time.sleep(5)
                after = read_scores(browser)
                print('LIVE_PROGRESS:', kind, task_progress(before, kind),
                      task_progress(after, kind), 'TODAY:', before['today'], after['today'], flush=True)
                before = after
        print('BROWSER_CHECK_OK', flush=True)
    finally:
        browser.quit()
