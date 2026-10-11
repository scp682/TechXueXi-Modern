"""Inspect the public login page without signing in or saving cookies."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "SourcePackages"
sys.path.insert(0, str(APP))
sys.argv[0] = str(APP / "pandalearning.py")
import pandalearning as app
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

mode = sys.argv[1] if len(sys.argv) > 1 else "project"
out = ROOT / "output" / "playwright"
out.mkdir(parents=True, exist_ok=True)
wrapper = None
if mode == "clean":
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1200,900")
    driver = webdriver.Chrome(executable_path=str(APP / "chrome" / "chromedriver.exe"), options=options)
else:
    app.gl.nohead = mode != "project-headed"
    wrapper = app.Mydriver()
    driver = wrapper.driver
driver.set_page_load_timeout(40)
try:
    driver.get("https://pc.xuexi.cn/points/login.html")
    try:
        WebDriverWait(driver, 20).until(lambda d: d.find_elements_by_id("ddlogin-iframe"))
    except Exception as exc:
        print("IFRAME_WAIT:", type(exc).__name__)
    print("PAGE:", json.dumps({"title": driver.title, "version": driver.capabilities.get("browserVersion"),
          "ua": driver.execute_script("return navigator.userAgent"), "html_length":len(driver.page_source),
          "body_length":len(driver.find_element_by_tag_name("body").text)}, ensure_ascii=False))
    for entry in driver.get_log("browser"):
        print("CONSOLE:", entry["level"], entry["message"].split("?")[0][:350])
    if wrapper is not None and hasattr(wrapper, "prepare_login_page"):
        qr = wrapper.prepare_login_page(timeout=30)
        print("QR_READY:", bool(qr))
        from pdlearn.mydriver import decode_img
        print("QR_DECODE_OK:", decode_img(qr).startswith('https://login.xuexi.cn/'))
        frames = driver.find_elements_by_id('ddlogin-iframe')
        print("QR_IN_VIEWPORT:", driver.execute_script(
            'const r=arguments[0].getBoundingClientRect(); return r.top>=0 && r.left>=0 && r.bottom<=innerHeight && r.right<=innerWidth;', frames[0]))
    else:
        frames=driver.find_elements_by_id("ddlogin-iframe")
        if frames:
            driver.switch_to.frame(frames[0])
            try:
                WebDriverWait(driver, 20).until(lambda d: d.find_elements_by_tag_name("img"))
                print("QR_IMAGES:", [(i.get_attribute("naturalWidth"), i.get_attribute("naturalHeight"))
                       for i in driver.find_elements_by_tag_name("img")])
            finally:
                driver.switch_to.default_content()
    driver.save_screenshot(str(out / (mode + "-login.png")))
finally:
    driver.quit()
