"""Read-only diagnostics; never print Cookie values or account identifiers."""
import base64
import json
from pathlib import Path
import pickle
import sys
try:
    import requests
except ImportError:
    from pip._vendor import requests

ROOT = Path(__file__).resolve().parents[1]
COOKIE_FILE = ROOT / 'SourcePackages/user/cookies.json'

def cookies_local():
    stored = json.loads(COOKIE_FILE.read_text(encoding='utf-8'))
    return pickle.loads(base64.b64decode(next(iter(stored.values()))))

if __name__ == '__main__':
    cookies = cookies_local()
    print('COOKIE_METADATA:', json.dumps([
        {k: c.get(k) for k in ('name', 'domain', 'path', 'secure', 'sameSite')}
        for c in cookies], ensure_ascii=False))
    if '--score' in sys.argv:
        jar = requests.cookies.RequestsCookieJar()
        for c in cookies:
            jar.set(c['name'], c['value'], domain=c.get('domain', '.xuexi.cn'), path=c.get('path', '/'))
        response = requests.get(
            'https://pc-proxy-api.xuexi.cn/delegate/score/days/listScoreProgress?sence=score&deviceType=2',
            cookies=jar, timeout=20)
        print('SCORE_HTTP:', response.status_code)
        response.raise_for_status()
        data = response.json().get('data', {})
        print('SCORE_KEYS:', list(data))
        print('SCORE_TASKS:', json.dumps(data.get('taskProgress'), ensure_ascii=False))
    if '--public' in sys.argv:
        for feed in ('1ap1igfgdn2', '1jscb6pu1n2', '3o3ufqgl8rsn', '1742g60067k'):
            response = requests.get('https://www.xuexi.cn/lgdata/' + feed + '.json', timeout=30)
            print('PUBLIC_HTTP:', feed, response.status_code)
            response.raise_for_status()
            rows = response.json()
            print('PUBLIC_SHAPE:', feed, type(rows).__name__, len(rows))
            print('PUBLIC_SAMPLE:', json.dumps({k:rows[0].get(k) for k in
                ('title','url','static_page_url','publishTime','itemType','type','videoId','video','content')
                if k in rows[0]}, ensure_ascii=False)[:2000])
