"""Use the server's current task definitions, never invent split scores."""
import time
import requests
from pdlearn import globalvar, color, file

RULE_KEYS = {'1':'article_num', '2':'video_num', '9':'login',
             '1002':'article_time', '1003':'video_time', '6':'daily',
             '5':'weekly', '4':'zhuanxiang'}
GROUP_CODES = {'article': {'1', '1002'}, 'video': {'2', '1003'}}
DAY_URL = 'https://pc-proxy-api.xuexi.cn/delegate/score/days/listScoreProgress?sence=score&deviceType=2'


def parse_tasks(data):
    if not isinstance(data, dict) or not isinstance(data.get('taskProgress'), list):
        raise RuntimeError('积分接口结构发生变化，请检查网站，不能继续按旧规则运行。')
    if data.get('inBlackList') or data.get('needFaceRecognition'):
        raise RuntimeError('网站要求账号验证或限制访问，请在官方页面手动处理。')
    scores = {key: 0 for key in RULE_KEYS.values()}
    scores.update(today=int(data.get('totalScore', 0)), _tasks=[], _targets={})
    for task in data['taskProgress']:
        codes = task.get('taskCode', [])
        if isinstance(codes, (str, int)):
            codes = [codes]
        codes = [str(code) for code in codes]
        current, target = int(task['currentScore']), int(task['dayMaxScore'])
        scores['_tasks'].append({'codes': codes, 'title': task.get('title', '/'.join(codes)),
                                 'current': current, 'target': target,
                                 'url': task.get('guideUrl', '')})
        for code in codes:
            key = RULE_KEYS.get(code)
            if key:
                # A combined 12-point task does not expose individual 6-point
                # counters. None makes that lack of information explicit.
                scores[key] = current if len(codes) == 1 else None
                scores['_targets'][key] = target if len(codes) == 1 else None
    return scores


def task_progress(scores, kind):
    codes = GROUP_CODES.get(kind, {code for code, key in RULE_KEYS.items() if key == kind})
    matching = [t for t in scores['_tasks'] if codes.intersection(t['codes'])]
    return (sum(t['current'] for t in matching), sum(t['target'] for t in matching))


def task_target(scores, kind):
    return task_progress(scores, kind)[1]


def handle_score_color(score, full_score, colorful=True):
    text = str(score)
    if score < full_score and colorful:
        text = color.red(text)
    return text + ' / ' + str(full_score)


def format_score(total, scores, name='', colorful=True):
    header = '{} 当前总积分：{} 今日得分：{}'.format(name, total, scores['today'])
    return header + '\n' + '，'.join('{}：{}'.format(
        t['title'], handle_score_color(t['current'], t['target'], colorful))
        for t in scores['_tasks'])


def show_score(cookies, browser=None):
    _, total, scores, name = get_score(cookies, browser=browser)
    print(format_score(total, scores, name))
    return total, scores


def show_scorePush(cookies, chat_id=None):
    _, total, scores, name = get_score(cookies)
    globalvar.pushprint(format_score(total, scores, name, False), chat_id)
    return total, scores


def get_score(cookies, browser=None):
    if browser is not None:
        return _get_score(cookies, browser)
    try:
        return _get_score(cookies)
    except (requests.exceptions.SSLError, requests.exceptions.ProxyError,
            requests.exceptions.ConnectionError):
        # Keep normal system networking and certificate verification intact.
        # Legacy Python TLS can fail while installed Chrome works correctly.
        from pdlearn.mydriver import Mydriver
        native = Mydriver(nohead=True)
        try:
            native.set_cookies(cookies)
            native.get_url('https://pc.xuexi.cn/points/my-points.html')
            return _get_score(cookies, native)
        finally:
            native.quit()


def _get_score(cookies, browser=None):
    jar = requests.cookies.RequestsCookieJar()
    for cookie in cookies:
        jar.set(cookie['name'], cookie['value'],
                domain=cookie.get('domain', '.xuexi.cn'), path=cookie.get('path', '/'))

    def fetch(url):
        if browser is not None:
            result = browser.get_json(url)
        else:
            response = requests.get(url, cookies=jar, timeout=20,
                                    headers={'Cache-Control':'no-cache'})
            response.raise_for_status()
            try:
                result = response.json()
            except ValueError:
                raise RuntimeError('积分接口没有返回 JSON，请检查登录和网络。') from None
        if not isinstance(result, dict) or not isinstance(result.get('data'), dict):
            raise RuntimeError('积分接口未返回有效账号数据，请检查登录；不会自动删除 Cookie。')
        return result['data']

    total_data = fetch('https://pc-proxy-api.xuexi.cn/delegate/score/get?_t=' + str(int(time.time()*1000)))
    info = fetch('https://pc-api.xuexi.cn/open/api/user/info')
    scores = parse_tasks(fetch(DAY_URL))
    return info['uid'], int(total_data['score']), scores, info.get('nick', '')


def remove_cookie(uid):
    # Keep compatibility for explicit user-management actions only.
    cookies = file.get_json_data('user/cookies.json', '{}')
    cookies.pop(str(uid), None)
    file.save_json_data('user/cookies.json', cookies)
