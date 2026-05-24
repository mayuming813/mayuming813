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
    """MetaMask 钱包页面对象"""

    # 选择器定义
    IMPORT_WALLET_BTN = "text=Import an existing wallet"
    SEED_PHRASE_INPUT = "input[placeholder*='Seed phrase']"
    PASSWORD_INPUT = "input[type='password']"
    CONFIRM_PASSWORD_INPUT = "input[type='password']:nth-of-type(2)"
    TERMS_CHECKBOX = "input[type='checkbox']"
    IMPORT_BTN = "button:has-text('Import')"
    CONNECT_BTN = "button:has-text('Connect')"
    APPROVE_BTN = "button:has-text('Approve')"
    CONFIRM_BTN = "button:has-text('Confirm')"
    SIGN_BTN = "button:has-text('Sign')"

    def import_wallet(self, seed_phrase: str, password: str):
        """导入钱包"""
        self.logger.info("开始导入 MetaMask 钱包")
        self.click(self.IMPORT_WALLET_BTN)
        self.fill(self.SEED_PHRASE_INPUT, seed_phrase)
        self.fill(self.PASSWORD_INPUT, password)
        self.fill(self.CONFIRM_PASSWORD_INPUT, password)
        self.click(self.TERMS_CHECKBOX)
        self.click(self.IMPORT_BTN)
        self.logger.info("MetaMask 钱包导入完成")

    def connect_wallet(self):
        """连接钱包到 DApp"""
        self.logger.info("连接 MetaMask 到 DApp")
        # 切换到 MetaMask 弹窗
        with self.page.context.expect_page() as popup_info:
            self.click(self.CONNECT_BTN)
        popup = popup_info.value
        popup.click(self.CONNECT_BTN)
        popup.wait_for_close()
        self.logger.info("钱包连接成功")

    def approve_transaction(self):
        """批准交易"""
        self.logger.info("批准交易")
        with self.page.context.expect_page() as popup_info:
            pass
        popup = popup_info.value
        popup.click(self.APPROVE_BTN)
        popup.wait_for_close()
        self.logger.info("交易已批准")

    def sign_message(self):
        """签名消息"""
        self.logger.info("签名消息")
        with self.page.context.expect_page() as popup_info:
            pass
        popup = popup_info.value
        popup.click(self.SIGN_BTN)
        popup.wait_for_close()
        self.logger.info("消息已签名")
