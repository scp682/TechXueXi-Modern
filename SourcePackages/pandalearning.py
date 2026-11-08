import math
import time
from sys import argv

from pdlearn import boot

boot.check_environment()
try:
    # 在此处导入所有 pdlearn 内的模块
    from pdlearn import globalvar as gl
    from pdlearn import color, score, threads, user
    from pdlearn.answer_question import daily, weekly, zhuanxiang
    from pdlearn.article_video import article, video
    from pdlearn.config import cfg_get
    from pdlearn.mydriver import Mydriver
    from pdlearn.score import show_score, show_scorePush
except ImportError as e:
    boot.try_pip_install(exception=e)


def get_argv():
    if gl.is_init != True:
        gl.init_global()
        if len(argv) > 2:
            if argv[2] == "hidden":
                gl.nohead = True
            elif argv[2] == "show":
                gl.nohead = False
        if len(argv) > 3:
            if argv[3] == "single":
                gl.lock = True
            elif argv[3] == "multithread":
                gl.lock = False
        if len(argv) > 4:
            if argv[4].isdigit():
                gl.stime = argv[4]
    return gl.nohead, gl.lock, gl.stime, gl.single


def get_run_mode(nohead):
    if nohead == True:
        return "3"
    return str(cfg_get("base.ModeType", 3))


def start_learn(uid, name):
    start_time = time.time()
    nohead, _, stime, _ = get_argv()
    TechXueXi_mode = get_run_mode(nohead)
    cookies = user.get_cookie(uid)

    if not name:
        user_fullname = user.get_fullname(uid)
        name = user_fullname.split('_', 1)[1]

    if not cookies or TechXueXi_mode == "0":
        if name == "新用户":
            msg = "[登录] 请使用学习强国 App 扫码添加账号。"
        else:
            msg = f"[登录] {name}：请扫码登录。"
        gl.pushprint(msg, chat_id=uid)
        if gl.pushmode == "6":
            gl.pushprint("[登录] 网页控制台模式，请在控制台点击添加账号。", chat_id=uid)
            print(color.yellow("如需启动网页控制台，请运行 webserverListener.py。"))
            return
        driver_login = Mydriver()
        cookies = driver_login.login()
        driver_login.quit()
        if not cookies:
            print(color.red("[登录] 扫码超时。"))
            return
        user.save_cookies(cookies)
        uid = user.get_userId(cookies)
        user_fullname = user.get_fullname(uid)
        name = user_fullname.split('_', 1)[1]
        user.update_last_user(uid)
    output = f"[运行] {name}：已登录，开始执行模式 {TechXueXi_mode}。"

    article_index = user.get_article_index(uid)
    video_index = user.get_video_index(uid)

    total, scores = show_score(cookies)
    gl.pushprint(output, chat_id=uid)
    if TechXueXi_mode in ["1", "3"]:

        # One active learning page per account avoids competing heartbeats.
        article(uid, cookies, article_index, scores)
        total, scores = show_score(cookies)
        video(uid, cookies, video_index, scores)
        total, scores = show_score(cookies)
    if TechXueXi_mode in ["2", "3"]:
        if score.task_target(scores, 'daily'):
            print('开始每日答题……')
            daily(cookies, scores)
        if score.task_target(scores, 'weekly'):
            print('开始每周答题……')
            weekly(cookies, scores)
        if score.task_target(scores, 'zhuanxiang') and (nohead != True or gl.zhuanxiang == True):
            print('开始专项答题……')
            zhuanxiang(cookies, scores)

    if TechXueXi_mode == "4":
        user.select_user()
    if TechXueXi_mode == "5":
        user.refresh_all_cookies(display_score=True)
    if TechXueXi_mode == "6":
        user.refresh_all_cookies(live_time=11.90)

    seconds_used = int(time.time() - start_time)
    gl.pushprint(name+" 总计用时 " + str(math.floor(seconds_used / 60)) +
                 " 分 " + str(seconds_used % 60) + " 秒", chat_id=uid)
    show_scorePush(cookies, chat_id=uid)
    try:
        user.shutdown(stime)
    except Exception as e:
        pass


def start(nick_name=None):
    nohead, _, _, single = get_argv()
    browser_mode = "无头" if nohead == True else "有窗口"
    print(f"[运行] 当前模式 {get_run_mode(nohead)}  |  浏览器：{browser_mode}")
    user_list = user.list_user(printing=False)
    user.refresh_all_cookies()
    if len(user_list) == 0:
        user_list.append(["", "新用户"])
    for i in range(len(user_list)):
        try:
            if nick_name is None or nick_name == user_list[i][1] or nick_name == user_list[i][0]:
                _learn = threads.MyThread(
                    user_list[i][1], start_learn, user_list[i][0], user_list[i][1], lock=single)
                _learn.start()
        except:
            gl.pushprint("学习页面崩溃，学习终止")


def get_my_score(uid):
    get_argv()
    user.refresh_all_cookies()
    cookies = user.get_cookie(uid)
    if not cookies:
        return False
    show_scorePush(cookies, chat_id=uid)
    return True


def get_user_list():
    get_argv()
    dic = user.refresh_all_cookies(display_score=True)
    values = dic.values()
    msg = ""
    for v in values:
        msg += v+"\n"
    if msg == "":
        msg = "cookie全部过期，请重新登录"
    return msg


def get_all_user_name():
    user_list = user.list_user(printing=False)
    names = []
    for i in range(len(user_list)):
        names.append(user_list[i][1])
    return names


def add_user(chat_id=None):
    get_argv()
    gl.pushprint("[登录] 请使用学习强国 App 扫码添加账号。", chat_id=chat_id)
    driver_login = Mydriver()
    cookies = driver_login.login(chat_id)
    driver_login.quit()
    # cookies = login(chat_id=chat_id)
    if not cookies:
        gl.pushprint("登录超时。", chat_id=chat_id)
        return
    user.save_cookies(cookies)
    uid = user.get_userId(cookies)
    user_fullname = user.get_fullname(uid)
    user.update_last_user(uid)
    gl.pushprint(user_fullname+"登录成功", chat_id=chat_id)


def main():
    print("TechXueXi-Modern")
    print("-" * 46)
    print("可用模式")
    mode_text = cfg_get('base.ModeText', "")
    print(mode_text.strip("\r\n").replace("\r\n", "\n"))
    print("  在 user/settings.conf 中设置 base.ModeType。")
    print("  答题时请留意浏览器。")
    print("\n运行状态")
    start()


if __name__ == '__main__':
    main()
