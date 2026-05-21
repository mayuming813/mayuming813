#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : base_page.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page, expect
from framework.core.logger import Logger
from framework.utils.smart_assert import SmartAssert, AssertMode


class BasePage:
    """页面对象基类"""

    def __init__(self, page: Page, assert_mode: str = AssertMode.STRICT):
        self.page = page
        self.logger = Logger.get_logger(self.__class__.__name__)
        self.assert_helper = SmartAssert(mode=assert_mode)

    def goto(self, url: str):
        """导航到指定 URL"""
        self.logger.info(f"导航到: {url}")
        self.page.goto(url)

    def click(self, selector: str, timeout: int = 30000):
        """点击元素"""
        self.logger.info(f"点击: {selector}")
        self.page.click(selector, timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = 30000):
        """填充输入框"""
        self.logger.info(f"填充 {selector}: {value}")
        self.page.fill(selector, value, timeout=timeout)

    def wait_for_selector(self, selector: str, timeout: int = 30000):
        """等待元素出现"""
        self.logger.info(f"等待元素: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_url(self, url: str, timeout: int = 30000):
        """等待 URL 变化"""
        self.logger.info(f"等待 URL: {url}")
        self.page.wait_for_url(url, timeout=timeout)

    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        return self.page.locator(selector).inner_text()

    def get_value(self, selector: str) -> str:
        """获取输入框的值"""
        return self.page.locator(selector).input_value()

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """检查元素是否可见"""
        try:
            return self.page.locator(selector).is_visible(timeout=timeout)
        except:
            return False

    def is_enabled(self, selector: str) -> bool:
        """检查元素是否可用"""
        return self.page.locator(selector).is_enabled()

    def screenshot(self, name: str = None, full_page: bool = True):
        """截图"""
        screenshot_dir = Path(__file__).parent.parent.parent / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)

        if name is None:
            name = f"{self.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        path = screenshot_dir / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=full_page)
        self.logger.info(f"截图保存: {path}")
        return str(path)

    def scroll_to(self, selector: str):
        """滚动到元素"""
        self.logger.info(f"滚动到: {selector}")
        self.page.locator(selector).scroll_into_view_if_needed()

    def hover(self, selector: str):
        """悬停在元素上"""
        self.logger.info(f"悬停: {selector}")
        self.page.hover(selector)

    def select_option(self, selector: str, value: str):
        """选择下拉框选项"""
        self.logger.info(f"选择 {selector}: {value}")
        self.page.select_option(selector, value)

    def check(self, selector: str):
        """勾选复选框"""
        self.logger.info(f"勾选: {selector}")
        self.page.check(selector)

    def uncheck(self, selector: str):
        """取消勾选复选框"""
        self.logger.info(f"取消勾选: {selector}")
        self.page.uncheck(selector)

    def press(self, selector: str, key: str):
        """按键"""
        self.logger.info(f"在 {selector} 按下: {key}")
        self.page.press(selector, key)

    def wait_for_load_state(self, state: str = "load", timeout: int = 30000):
        """等待页面加载状态"""
        self.logger.info(f"等待页面状态: {state}")
        self.page.wait_for_load_state(state, timeout=timeout)

    def reload(self):
        """刷新页面"""
        self.logger.info("刷新页面")
        self.page.reload()

    def go_back(self):
        """后退"""
        self.logger.info("后退")
        self.page.go_back()

    def go_forward(self):
        """前进"""
        self.logger.info("前进")
        self.page.go_forward()

    def get_attribute(self, selector: str, attribute: str) -> str:
        """获取元素属性"""
        return self.page.locator(selector).get_attribute(attribute)

    def count(self, selector: str) -> int:
        """获取元素数量"""
        return self.page.locator(selector).count()

    def execute_script(self, script: str, *args):
        """执行 JavaScript"""
        self.logger.info(f"执行脚本: {script}")
        return self.page.evaluate(script, *args)

