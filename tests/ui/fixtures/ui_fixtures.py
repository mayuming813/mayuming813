#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : ui_fixtures.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from tests.ui.pages.dapp_page import DAppPage
from tests.ui.pages.metamask_page import MetaMaskPage
from framework.fixtures.ui import *  # 导入基础UI fixtures (page, context等)
from framework.utils.smart_assert import AssertMode


# ==================== Allure 报告增强 ====================

def attach_screenshot(page, name: str):
    """附加截图到 Allure 报告"""
    screenshot_bytes = page.screenshot(full_page=True)
    allure.attach(
        screenshot_bytes,
        name=name,
        attachment_type=allure.attachment_type.PNG
    )


def attach_page_info(page, step_name: str):
    """附加页面信息到 Allure 报告"""
    page_info = {
        'url': page.url,
        'title': page.title()
    }
    allure.attach(
        str(page_info),
        name=f"📄 {step_name}",
        attachment_type=allure.attachment_type.TEXT
    )


# ==================== 基础 Fixtures ====================

@pytest.fixture(scope="function")
def dapp_page(page):
    """DApp 页面对象 fixture"""
    return DAppPage(page, assert_mode=AssertMode.STRICT)


@pytest.fixture(scope="function")
def dapp_page_soft(page):
    """DApp 页面对象 fixture（软断言）"""
    return DAppPage(page, assert_mode=AssertMode.SOFT)


@pytest.fixture(scope="function")
def metamask_page(page):
    """MetaMask 页面对象 fixture"""
    return MetaMaskPage(page)


# ==================== 场景 Fixtures ====================

@pytest.fixture(scope="function")
def connected_wallet(dapp_page, metamask_page):
    """
    场景模块：连接钱包
    返回：DApp页面对象和钱包地址
    """
    with allure.step("连接 MetaMask 钱包"):
        # 点击连接钱包
        dapp_page.click_connect_wallet()
        attach_screenshot(dapp_page.page, "点击连接钱包")

        # MetaMask 确认连接
        metamask_page.click_next()
        metamask_page.click_connect()
        attach_screenshot(metamask_page.page, "MetaMask 确认连接")

        # 等待连接完成
        dapp_page.wait_for_selector(dapp_page.WALLET_ADDRESS, timeout=10000)

        # 验证连接成功
        assert dapp_page.is_wallet_connected(), "钱包连接失败"

        wallet_address = dapp_page.get_wallet_address()
        attach_page_info(dapp_page.page, f"钱包已连接: {wallet_address}")

    return {
        'dapp_page': dapp_page,
        'metamask_page': metamask_page,
        'wallet_address': wallet_address
    }


@pytest.fixture(scope="function")
def wallet_with_balance(connected_wallet):
    """
    场景模块：连接钱包并获取余额
    依赖：connected_wallet
    返回：钱包信息和余额
    """
    dapp_page = connected_wallet['dapp_page']

    with allure.step("获取钱包余额"):
        balance = dapp_page.get_balance()
        attach_page_info(dapp_page.page, f"余额: {balance}")

    return {
        **connected_wallet,
        'balance': balance
    }


@pytest.fixture(scope="function")
def transfer_form_filled(wallet_with_balance, test_data):
    """
    场景模块：填写转账表单
    依赖：wallet_with_balance
    返回：表单数据
    """
    dapp_page = wallet_with_balance['dapp_page']
    recipient = test_data.unique_wallet_address()
    amount = "0.1"

    with allure.step("填写转账表单"):
        dapp_page.fill_recipient(recipient)
        dapp_page.fill_amount(amount)

        # 验证输入
        assert dapp_page.get_recipient_value() == recipient, "收款地址输入错误"
        assert dapp_page.get_amount_value() == amount, "金额输入错误"

        attach_screenshot(dapp_page.page, "转账表单已填写")

    return {
        **wallet_with_balance,
        'recipient': recipient,
        'amount': amount
    }


# ==================== 数据准备 Fixtures ====================

@pytest.fixture(scope="function")
def test_data():
    """测试数据工厂 fixture"""
    from framework.utils.test_data_factory import TestDataFactory
    return TestDataFactory()
