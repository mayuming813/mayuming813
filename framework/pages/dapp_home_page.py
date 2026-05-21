#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : dapp_home_page.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from framework.pages.base_page import BasePage


class DAppHomePage(BasePage):
    """DApp 主页"""

    # 选择器定义
    CONNECT_WALLET_BTN = "button:has-text('Connect Wallet')"
    WALLET_ADDRESS = "[data-testid='wallet-address']"
    BALANCE = "[data-testid='balance']"

    def connect_wallet(self):
        """连接钱包"""
        self.click(self.CONNECT_WALLET_BTN)

    def get_wallet_address(self) -> str:
        """获取已连接的钱包地址"""
        return self.get_text(self.WALLET_ADDRESS)

    def get_balance(self) -> str:
        """获取余额"""
        return self.get_text(self.BALANCE)

    def is_wallet_connected(self) -> bool:
        """检查钱包是否已连接"""
        return self.is_visible(self.WALLET_ADDRESS)