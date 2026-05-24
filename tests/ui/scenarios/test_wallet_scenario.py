#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_wallet_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from tests.ui.fixtures.ui_fixtures import attach_screenshot, attach_page_info


@allure.feature("DApp UI")
@allure.story("钱包连接")
class TestWalletConnectionScenario:
    """钱包连接场景测试"""

    @allure.title("场景：连接 MetaMask 钱包")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("用户连接 MetaMask 钱包到 DApp")
    def test_connect_wallet(self, connected_wallet):
        """
        场景：连接钱包
        使用 fixture：connected_wallet
        """
        dapp_page = connected_wallet['dapp_page']
        wallet_address = connected_wallet['wallet_address']

        # fixture 已完成连接，这里做额外验证
        with allure.step("验证钱包地址格式"):
            assert wallet_address.startswith('0x'), "钱包地址格式错误"
            assert len(wallet_address) == 42, "钱包地址长度错误"

        attach_screenshot(dapp_page.page, "钱包连接成功")

    @allure.title("场景：连接钱包→查看余额")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("连接钱包后查看余额")
    def test_connect_and_view_balance(self, wallet_with_balance):
        """
        场景：连接钱包→查看余额
        使用 fixture：wallet_with_balance
        """
        dapp_page = wallet_with_balance['dapp_page']
        balance = wallet_with_balance['balance']

        with allure.step("验证余额显示"):
            assert balance is not None, "余额未显示"
            attach_page_info(dapp_page.page, f"当前余额: {balance}")

    @allure.title("场景：断开钱包连接")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("断开已连接的钱包")
    def test_disconnect_wallet(self, connected_wallet):
        """
        场景：断开钱包连接
        组装：connected_wallet + 单操作
        """
        dapp_page = connected_wallet['dapp_page']

        with allure.step("断开钱包连接"):
            dapp_page.click_disconnect()
            attach_screenshot(dapp_page.page, "点击断开连接")

        with allure.step("验证钱包已断开"):
            # 等待地址消失
            dapp_page.page.wait_for_timeout(2000)
            assert not dapp_page.is_wallet_connected(), "钱包未断开"

        attach_screenshot(dapp_page.page, "钱包已断开")
