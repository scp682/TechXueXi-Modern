"""Bounded browsing, with real playback and server-side progress checks."""
import time
from selenium.webdriver.support.ui import WebDriverWait
from pdlearn import user, color, get_links
from pdlearn.mydriver import Mydriver
from pdlearn.score import get_score, task_progress, format_score


def media_state(browser):
    return browser.driver.execute_script('''
        const v = document.querySelector('video');
        return v ? {ready:v.readyState, paused:v.paused, ended:v.ended,
                    time:v.currentTime, duration:Number.isFinite(v.duration)?v.duration:0,
                    error:v.error ? v.error.code : 0} : null;
    ''')


def prepare_content(browser, kind):
    if kind == 'video':
        WebDriverWait(browser.driver, 25).until(lambda d: media_state(browser))
        browser.go_js('''
            const v = document.querySelector('video');
            v.muted = true;
            v.play().catch(() => {});
            v.scrollIntoView({block:'center'});
        ''')
        state = WebDriverWait(browser.driver, 25).until(
            lambda d: (lambda s: s if s and s['ready'] >= 2 and
                       not s['paused'] and s['time'] > 0 else False)(media_state(browser)))
        return state
    WebDriverWait(browser.driver, 25).until(lambda d: d.execute_script('''
        const text = document.body.innerText;
        return text.length > 200 && !/页面不存在|访问异常|验证码|安全验证/.test(text);
    '''))
    return None


def browse_once(browser, kind, seconds=75):
    state = prepare_content(browser, kind)
    previous_time = state['time'] if state else 0
    stalled = 0
    for tick in range(seconds):
        if tick % 15 == 0:
            print('{}：已浏览 {} 秒（计时不代表积分已增加）'.format(
                '文章' if kind == 'article' else '视频', tick), flush=True)
        if kind == 'article':
            if tick % 10 == 0:
                browser.go_js('window.scrollBy(0, 200)')
        else:
            state = media_state(browser)
            if not state or state['error']:
                raise RuntimeError('视频播放器加载失败，不能把等待时间当作观看时间。')
            if state['ended']:
                break
            if state['time'] <= previous_time:
                stalled += 1
            else:
                stalled = 0
            if stalled >= 15:
                raise RuntimeError('视频连续 15 秒没有播放进度，已停止。')
            previous_time = state['time']
        time.sleep(1)


def learn_content(kind, user_id, cookies, pointer, scores,
                  max_items=24, max_no_progress=3):
    current, target = task_progress(scores, kind)
    label = '文章' if kind == 'article' else '视频'
    if not target or current >= target:
        print(label + '任务不存在或积分已满，跳过。')
        return True
    browser = None
    try:
        # Honor the selected UI mode. Do not force all learning to headless.
        browser = Mydriver()
        browser.set_cookies(cookies)
        browser.get_url('https://www.xuexi.cn/')
        loader = get_links.get_article_links if kind == 'article' else get_links.get_video_links
        links = loader(browser)
        pointer = max(0, int(pointer)) % len(links)
        no_progress = 0
        for attempt in range(min(max_items, len(links))):
            browser.get_url(links[pointer])
            browse_once(browser, kind)
            # The site may report after navigation or a short settling delay.
            browser.get_url('https://pc.xuexi.cn/points/my-points.html')
            time.sleep(5)
            _, total, scores, _ = get_score(cookies, browser=browser)
            new_current, target = task_progress(scores, kind)
            print(format_score(total, scores, colorful=False), flush=True)
            pointer = (pointer + 1) % len(links)
            saver = user.save_article_index if kind == 'article' else user.save_video_index
            saver(user_id, pointer)
            if new_current >= target:
                print(label + '任务已由网站确认完成。')
                return True
            no_progress = 0 if new_current > current else no_progress + 1
            current = new_current
            if no_progress >= max_no_progress:
                print(color.red(label + '连续 {} 次没有积分变化，停止自动浏览。'
                      '请在官方 APP/网页核对当前计分规则；不能保证网页浏览仍计分。'.format(no_progress)))
                return False
        print(label + '达到本轮浏览上限，尚未取得满分，不再无限重试。')
        return False
    except Exception as exc:
        print(color.red(label + '检测到异常：' + str(exc)))
        return False
    finally:
        if browser is not None:
            browser.quit()


def article(userId, cookies, article_pointer, scores):
    return learn_content('article', userId, cookies, article_pointer, scores)


def video(userId, cookies, video_pointer, scores):
    return learn_content('video', userId, cookies, video_pointer, scores)
