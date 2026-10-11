"""Current daily practice UI; answer only explicit official highlighted hints."""
import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pdlearn.mydriver import Mydriver
from pdlearn.score import get_score, task_progress, format_score


def normal_text(text):
    return re.sub(r'\s+', '', text).strip('，。；,.;')


def hints_from_html(html):
    soup = BeautifulSoup(html, 'lxml')
    hints = []
    for element in soup.select('font[color], [style]'):
        style = element.get('color', '') + element.get('style', '')
        if re.search(r'red|#ff0000|#f00\b|rgb\(255,\s*0,\s*0\)', style, re.I):
            text = normal_text(element.get_text())
            if text and text not in hints:
                hints.append(text)
    return hints


def match_options(options, hints, multiple=False, question=''):
    # Exact matching avoids confusing 是/不是 or embedded partial answers.
    texts = [normal_text(re.sub(r'^[A-Z][.．、]', '', option.strip())) for option in options]
    chosen = [i for i, text in enumerate(texts) if text in hints]
    # A true/false statement can be the exact quoted official rule rather than
    # the literal word "正确". Only accept a full statement match, not keywords.
    if not chosen and not multiple and set(texts) == {'正确', '错误'}:
        stem = re.split(r'\n\s*来源\s*[:：]', question, maxsplit=1)[0]
        statement = re.sub(r'[（(]\s*[）)]\s*[。.]?$', '', stem.strip())
        statement = re.sub(r'^(根据|依据)《[^》]+》[，,]\s*', '', statement)
        if any(len(hint) >= 20 and normal_text(statement) == hint for hint in hints):
            chosen = [texts.index('正确')]
    if not chosen or (not multiple and len(chosen) != 1):
        return []
    if multiple and len(chosen) < 2:
        return []
    return chosen


def practice(cookies, scores, driver_default=None, max_questions=10):
    current, target = task_progress(scores, 'daily')
    if not target or current >= target:
        print('每日答题任务不存在或积分已满，跳过。')
        return True
    browser = driver_default
    try:
        if browser is None:
            browser = Mydriver()
        browser.set_cookies(cookies)
        browser.get_url('https://pc.xuexi.cn/points/exam-practice.html')
        wait = WebDriverWait(browser.driver, 20)
        wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, '.question, .practice-result'))
        for number in range(max_questions):
            if browser.driver.find_elements(By.CSS_SELECTOR, '.practice-result'):
                break
            if any(e.is_displayed() for e in browser.driver.find_elements(
                    By.CSS_SELECTOR, '.nc-mask-display, .nc-container')):
                raise RuntimeError('网站要求手动安全验证，停止自动答题。')
            question = browser.driver.find_element(By.CSS_SELECTOR, '.question .q-body').text
            category = browser.driver.find_element(By.CSS_SELECTOR, '.question .q-header').text
            tips = browser.driver.find_elements(By.CSS_SELECTOR, '.question .tips')
            if not tips:
                raise RuntimeError('未找到官方提示，停止；不会默认选 A 或全选。')
            tips[0].click()
            tip = wait.until(lambda d: next((e for e in d.find_elements(
                By.CSS_SELECTOR, '.ant-popover:not(.ant-popover-hidden) .line-feed')
                if e.is_displayed()), False))
            hints = hints_from_html(tip.get_attribute('innerHTML'))
            tips[0].click()
            choices = browser.driver.find_elements(By.CSS_SELECTOR, '.question .choosable')
            inputs = browser.driver.find_elements(By.CSS_SELECTOR, '.question input[type="text"]')
            if '填空' in category:
                if not hints or len(hints) != len(inputs):
                    raise RuntimeError('提示与填空数量不一致，需要手动答题。')
                for field, hint in zip(inputs, hints):
                    field.clear()
                    field.send_keys(hint)
            else:
                selected = match_options([e.text for e in choices], hints,
                                         multiple='多选' in category, question=question)
                if not selected:
                    print('题目：' + question)
                    print('选项：', [e.text for e in choices], '官方高亮提示：', hints)
                    raise RuntimeError('无法从官方提示唯一确定答案，需要手动答题。')
                for index in selected:
                    choices[index].click()
            buttons = browser.driver.find_elements(By.CSS_SELECTOR, '.action-row button')
            if not buttons:
                raise RuntimeError('未找到当前题目的提交按钮。')
            buttons[-1].click()
            time.sleep(1)
            # A correct-answer confirmation can precede the next question.
            next_buttons = browser.driver.find_elements(By.CSS_SELECTOR, '.action-row button')
            next_button = next((b for b in next_buttons if '下一题' in b.text or '交卷' in b.text), None)
            if next_button:
                next_button.click()
            wait.until(lambda d: bool(d.find_elements(By.CSS_SELECTOR, '.practice-result')) or
                       (d.find_elements(By.CSS_SELECTOR, '.question .q-body') and
                        d.find_element(By.CSS_SELECTOR, '.question .q-body').text != question))
            print('每日练习：已处理第 {} 题。'.format(number + 1), flush=True)
        time.sleep(3)
        _, total, latest, _ = get_score(cookies, browser=browser)
        print(format_score(total, latest, colorful=False), flush=True)
        current, target = task_progress(latest, 'daily')
        if current >= target:
            print('每日答题积分已由网站确认完成。')
            return True
        print('每日答题未取得满分，本轮停止，请在官方页面手动核对。')
        return False
    except Exception as exc:
        print('每日答题停止：' + str(exc))
        return False
    finally:
        if browser is not None and driver_default is None:
            browser.quit()
