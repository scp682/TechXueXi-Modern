from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

APP = Path(__file__).resolve().parents[1] / 'SourcePackages'
sys.path.insert(0, str(APP))
sys.argv[0] = str(APP / 'pandalearning.py')
import pandalearning
from pdlearn.mydriver import Mydriver
from selenium.common.exceptions import StaleElementReferenceException


class LoginBrowserTests(unittest.TestCase):
    def qr_driver(self, images):
        wrapper = Mydriver.__new__(Mydriver)
        wrapper.driver = Mock()
        wrapper.driver.find_elements.side_effect = [[Mock()], images, []]
        return wrapper

    def test_incomplete_image_is_not_a_ready_qr(self):
        img = Mock()
        img.is_displayed.return_value = True
        img.get_attribute.return_value = '0'
        wrapper = self.qr_driver([img])
        self.assertFalse(wrapper._qr_image_once())
        self.assertEqual(wrapper.driver.switch_to.default_content.call_count, 2)

    def test_loaded_image_is_read_and_frame_is_restored(self):
        img = Mock()
        img.is_displayed.return_value = True
        img.get_attribute.side_effect = lambda name: {
            'naturalWidth': '210', 'naturalHeight': '210',
            'src': 'data:image/png;base64,fixture'}[name]
        wrapper = self.qr_driver([img])
        self.assertEqual(wrapper._qr_image_once(), 'data:image/png;base64,fixture')
        self.assertEqual(wrapper.driver.switch_to.default_content.call_count, 2)

    def test_frame_reload_is_retryable_and_restores_main_document(self):
        wrapper = self.qr_driver([])
        wrapper.driver.switch_to.frame.side_effect = StaleElementReferenceException()
        self.assertFalse(wrapper._qr_image_once())
        self.assertEqual(wrapper.driver.switch_to.default_content.call_count, 2)

    def test_visible_login_uses_native_renderer_and_explicit_mode(self):
        with patch('pdlearn.mydriver.webdriver.Chrome') as chrome:
            wrapper = Mydriver(nohead=False)
        args = wrapper.options.arguments
        self.assertIn('--window-size=1200,900', args)
        self.assertFalse(any(a.startswith('--headless') for a in args))
        self.assertFalse(any(a.startswith('--user-agent') for a in args))
        self.assertNotIn('--disable-gpu', args)
        self.assertNotIn('--disable-software-rasterizer', args)
        self.assertNotIn('--proxy-bypass-list=*', args)
        self.assertTrue(chrome.called)


if __name__ == '__main__':
    unittest.main()
