#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_transfer_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from tests.ui.fixtures.ui_fixtures import attach_screenshot, attach_page_info


@allure.feature("DApp UI")
@allure.story("代币转账")
class TestTransferScenario:
    """代币转账场景测试"""

    @allure.title("场景：填写转账表单")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("填写转账表单并验证输入")
    def test_fill_transfer_form(self, transfer_form_filled):
        """
        场景：填写转账表单
        使用 fixture：transfer_form_filled
        """
        dapp_page = transfer_form_filled['dapp_page']
        recipient = transfer_form_filled['recipient']
        amount = transfer_form_filled['amount']

        # fixture 已完成填写和验证
        attach_page_info(dapp_page.page, f"转账: {amount} -> {recipient}")

    @allure.title("场景：完整转账流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("连接钱包→填写表单→发送交易→确认")
    def test_full_transfer_flow(self, transfer_form_filled):
        """
        场景：完整转账流程
        组装：transfer_form_filled + 单操作
        """
        dapp_page = transfer_form_filled['dapp_page']
        metamask_page = transfer_form_filled['metamask_page']
        balance_before = transfer_form_filled['balance']

        # 步骤1：点击发送
        with allure.step("点击发送按钮"):
            dapp_page.click_send()
            attach_screenshot(dapp_page.page, "点击发送")

        # 步骤2：MetaMask 确认
        with allure.step("MetaMask 确认交易"):
            metamask_page.click_confirm()
            attach_screenshot(metamask_page.page, "确认交易")

        # 步骤3：等待交易完成
        with allure.step("等待交易完成"):
            try:
                dapp_page.wait_for_tx_success(timeout=60000)
                assert dapp_page.is_tx_success_visible(), "未显示交易成功"
                attach_screenshot(dapp_page.page, "交易成功")
            except Exception as e:
                attach_screenshot(dapp_page.page, "交易失败")
                raise

        # 步骤4：验证余额变化
        with allure.step("验证余额变化"):
            balance_after = dapp_page.get_balance()
            assert balance_after != balance_before, "余额未变化"
            attach_page_info(dapp_page.page, f"余额变化: {balance_before} -> {balance_after}")

    @allure.title("场景：表单验证 - 无效地址")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试无效地址的表单验证")
    def test_invalid_address_validation(self, wallet_with_balance):
        """
        场景：表单验证 - 无效地址
        组装：wallet_with_balance + 单操作
        """
        dapp_page = wallet_with_balance['dapp_page']

        with allure.step("输入无效地址"):
            dapp_page.fill_recipient("invalid_address")
            dapp_page.fill_amount("1")
            dapp_page.click_send()
            attach_screenshot(dapp_page.page, "输入无效地址")

        with allure.step("验证错误提示"):
            assert dapp_page.is_address_error_visible(), "未显示地址错误提示"
            attach_screenshot(dapp_page.page, "地址错误提示")

    @allure.title("场景：表单验证 - 余额不足")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试余额不足的表单验证")
    def test_insufficient_balance_validation(self, wallet_with_balance, test_data):
        """
        场景：表单验证 - 余额不足
        组装：wallet_with_balance + 单操作
        """
        dapp_page = wallet_with_balance['dapp_page']

        with allure.step("输入超额金额"):
            dapp_page.fill_recipient(test_data.unique_wallet_address())
            dapp_page.fill_amount("999999999")
            dapp_page.click_send()
            attach_screenshot(dapp_page.page, "输入超额金额")

        with allure.step("验证余额不足提示"):
            assert dapp_page.is_insufficient_balance_error_visible(), "未显示余额不足提示"
            attach_screenshot(dapp_page.page, "余额不足提示")
