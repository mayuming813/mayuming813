#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : dapp_page.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from framework.pages.base_page import BasePage


class DAppPage(BasePage):
    """DApp 页面对象 - 只负责元素定位和基础操作"""

    # 元素定位器
    CONNECT_WALLET_BTN = "[data-testid='connect-wallet']"
    WALLET_ADDRESS = "[data-testid='wallet-address']"
    WALLET_BALANCE = "[data-testid='wallet-balance']"
    DISCONNECT_BTN = "[data-testid='disconnect']"

    # 转账表单
    RECIPIENT_INPUT = "[data-testid='recipient-address']"
    AMOUNT_INPUT = "[data-testid='amount']"
    SEND_BTN = "[data-testid='send-button']"

    # 状态提示
    TX_SUCCESS_MSG = "[data-testid='transaction-success']"
    TX_PENDING_MSG = "[data-testid='transaction-pending']"
    TX_FAILED_MSG = "[data-testid='transaction-failed']"

    # 错误提示
    ADDRESS_ERROR = "[data-testid='address-error']"
    AMOUNT_ERROR = "[data-testid='amount-error']"
    INSUFFICIENT_BALANCE_ERROR = "[data-testid='insufficient-balance-error']"
    NETWORK_ERROR = "[data-testid='network-error']"

    def __init__(self, page, assert_mode=None):
        super().__init__(page, assert_mode)

    # ==================== 单操作方法 ====================

    def click_connect_wallet(self):
        """点击连接钱包按钮"""
        self.click(self.CONNECT_WALLET_BTN)

    def click_disconnect(self):
        """点击断开连接"""
        self.click(self.DISCONNECT_BTN)

    def get_wallet_address(self) -> str:
        """获取钱包地址"""
        return self.get_text(self.WALLET_ADDRESS)

    def get_balance(self) -> str:
        """获取余额"""
        return self.get_text(self.WALLET_BALANCE)

    def is_wallet_connected(self) -> bool:
        """检查钱包是否已连接"""
        return self.is_visible(self.WALLET_ADDRESS)

    def fill_recipient(self, address: str):
        """填写收款地址"""
        self.fill(self.RECIPIENT_INPUT, address)

    def fill_amount(self, amount: str):
        """填写转账金额"""
        self.fill(self.AMOUNT_INPUT, amount)

    def get_recipient_value(self) -> str:
        """获取收款地址输入值"""
        return self.get_value(self.RECIPIENT_INPUT)

    def get_amount_value(self) -> str:
        """获取金额输入值"""
        return self.get_value(self.AMOUNT_INPUT)

    def click_send(self):
        """点击发送按钮"""
        self.click(self.SEND_BTN)

    def is_tx_success_visible(self) -> bool:
        """检查交易成功提示是否可见"""
        return self.is_visible(self.TX_SUCCESS_MSG)

    def is_tx_pending_visible(self) -> bool:
        """检查交易待确认提示是否可见"""
        return self.is_visible(self.TX_PENDING_MSG)

    def is_tx_failed_visible(self) -> bool:
        """检查交易失败提示是否可见"""
        return self.is_visible(self.TX_FAILED_MSG)

    def get_tx_success_message(self) -> str:
        """获取交易成功消息"""
        return self.get_text(self.TX_SUCCESS_MSG)

    def is_address_error_visible(self) -> bool:
        """检查地址错误提示是否可见"""
        return self.is_visible(self.ADDRESS_ERROR)

    def is_amount_error_visible(self) -> bool:
        """检查金额错误提示是否可见"""
        return self.is_visible(self.AMOUNT_ERROR)

    def is_insufficient_balance_error_visible(self) -> bool:
        """检查余额不足提示是否可见"""
        return self.is_visible(self.INSUFFICIENT_BALANCE_ERROR)

    def is_network_error_visible(self) -> bool:
        """检查网络错误提示是否可见"""
        return self.is_visible(self.NETWORK_ERROR)

    def wait_for_tx_success(self, timeout: int = 60000):
        """等待交易成功"""
        self.wait_for_selector(self.TX_SUCCESS_MSG, timeout=timeout)
