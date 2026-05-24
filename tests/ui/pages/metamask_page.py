#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : metamask_page.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from framework.pages.base_page import BasePage


class MetaMaskPage(BasePage):
    """MetaMask 页面对象 - 只负责元素定位和基础操作"""

    # 连接钱包
    NEXT_BTN = "button:has-text('Next')"
    CONNECT_BTN = "button:has-text('Connect')"

    # 交易确认
    CONFIRM_BTN = "button:has-text('Confirm')"
    REJECT_BTN = "button:has-text('Reject')"

    # Gas 设置
    GAS_EDIT_BTN = "[data-testid='edit-gas-fee-icon']"
    MAX_FEE_INPUT = "[data-testid='max-fee-input']"
    PRIORITY_FEE_INPUT = "[data-testid='priority-fee-input']"
    SAVE_GAS_BTN = "button:has-text('Save')"

    def __init__(self, page, assert_mode=None):
        super().__init__(page, assert_mode)

    # ==================== 单操作方法 ====================

    def click_next(self):
        """点击 Next 按钮"""
        self.click(self.NEXT_BTN)

    def click_connect(self):
        """点击 Connect 按钮"""
        self.click(self.CONNECT_BTN)

    def click_confirm(self):
        """点击 Confirm 按钮"""
        self.click(self.CONFIRM_BTN)

    def click_reject(self):
        """点击 Reject 按钮"""
        self.click(self.REJECT_BTN)

    def click_edit_gas(self):
        """点击编辑 Gas 按钮"""
        self.click(self.GAS_EDIT_BTN)

    def set_max_fee(self, fee: str):
        """设置最大费用"""
        self.fill(self.MAX_FEE_INPUT, fee)

    def set_priority_fee(self, fee: str):
        """设置优先费用"""
        self.fill(self.PRIORITY_FEE_INPUT, fee)

    def click_save_gas(self):
        """保存 Gas 设置"""
        self.click(self.SAVE_GAS_BTN)

    def is_confirm_visible(self) -> bool:
        """检查确认按钮是否可见"""
        return self.is_visible(self.CONFIRM_BTN)
