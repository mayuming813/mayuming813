#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_user_transfer_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from tests.unit.fixtures.unit_fixtures import attach_user_action, attach_balance_info


@allure.feature("Token 合约")
@allure.story("用户转账")
class TestUserTransferScenario:
    """用户转账场景测试 - 从用户角度测试转账功能"""

    @allure.title("场景：Alice 转账给 Bob")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("用户场景：Alice 想要转账 10 个代币给 Bob")
    def test_alice_transfer_to_bob(self, alice_and_bob):
        """
        用户场景：Alice 转账给 Bob

        作为 Alice，我想要转账 10 个代币给 Bob
        以便 Bob 可以使用这些代币
        """
        token = alice_and_bob['token']
        alice = alice_and_bob['alice']
        bob = alice_and_bob['bob']
        alice_balance_before = alice_and_bob['alice_balance']
        bob_balance_before = alice_and_bob['bob_balance']

        transfer_amount = 10.0

        # 步骤1：Alice 查看自己的余额（确认有足够的代币）
        with allure.step("Alice 确认自己有足够的代币"):
            assert alice_balance_before >= transfer_amount, \
                f"Alice 余额不足，当前余额: {alice_balance_before}"

        # 步骤2：Alice 发起转账
        with allure.step(f"Alice 转账 {transfer_amount} 代币给 Bob"):
            result = token.user_transfer_to(alice, bob, transfer_amount)
            attach_user_action("转账", **result)

            assert result['status'] == 'success', "转账失败"

        # 步骤3：Alice 和 Bob 查看转账后的余额
        with allure.step("Alice 和 Bob 查看转账后的余额"):
            alice_balance_after = token.user_check_balance(alice)
            bob_balance_after = token.user_check_balance(bob)

            attach_balance_info("Alice（转账后）", alice_balance_after)
            attach_balance_info("Bob（转账后）", bob_balance_after)

        # 步骤4：验证余额变化符合预期
        with allure.step("验证余额变化"):
            # Alice 余额应该减少
            assert alice_balance_after['balance'] == alice_balance_before - transfer_amount, \
                f"Alice 余额变化不正确，期望: {alice_balance_before - transfer_amount}, 实际: {alice_balance_after['balance']}"

            # Bob 余额应该增加
            assert bob_balance_after['balance'] == bob_balance_before + transfer_amount, \
                f"Bob 余额变化不正确，期望: {bob_balance_before + transfer_amount}, 实际: {bob_balance_after['balance']}"

    @allure.title("场景：Alice 转账全部余额给 Bob")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("用户场景：Alice 想要把所有代币都转给 Bob")
    def test_alice_transfer_all_to_bob(self, alice_and_bob):
        """
        用户场景：Alice 转账全部余额

        作为 Alice，我想要把所有代币都转给 Bob
        转账后我的余额应该为 0
        """
        token = alice_and_bob['token']
        alice = alice_and_bob['alice']
        bob = alice_and_bob['bob']
        alice_balance_before = alice_and_bob['alice_balance']
        bob_balance_before = alice_and_bob['bob_balance']

        with allure.step(f"Alice 转账全部余额 {alice_balance_before} 给 Bob"):
            result = token.user_transfer_to(alice, bob, alice_balance_before)
            attach_user_action("转账全部余额", **result)

            assert result['status'] == 'success', "转账失败"

        with allure.step("验证 Alice 余额为 0"):
            alice_balance_after = token.user_check_balance(alice)
            attach_balance_info("Alice（转账后）", alice_balance_after)

            assert alice_balance_after['balance'] == 0, \
                f"Alice 应该没有余额了，实际: {alice_balance_after['balance']}"

        with allure.step("验证 Bob 收到了所有代币"):
            bob_balance_after = token.user_check_balance(bob)
            attach_balance_info("Bob（转账后）", bob_balance_after)

            assert bob_balance_after['balance'] == bob_balance_before + alice_balance_before, \
                "Bob 收到的金额不正确"

    @allure.title("场景：Alice 尝试转账超过余额的金额")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("用户场景：Alice 尝试转账超过自己余额的金额，应该失败")
    def test_alice_transfer_more_than_balance(self, alice_and_bob):
        """
        用户场景：转账金额超过余额

        作为 Alice，当我尝试转账超过余额的金额时
        系统应该拒绝这笔交易
        """
        token = alice_and_bob['token']
        alice = alice_and_bob['alice']
        bob = alice_and_bob['bob']
        alice_balance = alice_and_bob['alice_balance']

        # 尝试转账超过余额的金额
        excessive_amount = alice_balance + 100.0

        with allure.step(f"Alice 尝试转账 {excessive_amount}（超过余额 {alice_balance}）"):
            with pytest.raises(Exception) as exc_info:
                token.user_transfer_to(alice, bob, excessive_amount)

            attach_user_action("转账失败", error=str(exc_info.value))

        with allure.step("验证余额未变化"):
            alice_balance_after = token.user_check_balance(alice)
            assert alice_balance_after['balance'] == alice_balance, \
                "余额不应该变化"


@allure.feature("Token 合约")
@allure.story("用户授权")
class TestUserAuthorizationScenario:
    """用户授权场景测试 - 从用户角度测试授权功能"""

    @allure.title("场景：Alice 授权 Bob 使用她的代币")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("用户场景：Alice 授权 Bob 可以使用她的 100 个代币")
    def test_alice_authorize_bob(self, alice_and_bob):
        """
        用户场景：Alice 授权 Bob

        作为 Alice，我想要授权 Bob 可以使用我的 100 个代币
        以便 Bob 可以帮我进行某些操作
        """
        token = alice_and_bob['token']
        alice = alice_and_bob['alice']
        bob = alice_and_bob['bob']

        authorize_amount = 100.0

        # 步骤1：Alice 授权 Bob
        with allure.step(f"Alice 授权 Bob 使用 {authorize_amount} 代币"):
            result = token.user_authorize_spender(alice, bob, authorize_amount)
            attach_user_action("授权", **result)

            assert result['status'] == 'success', "授权失败"

        # 步骤2：Bob 查看授权额度
        with allure.step("Bob 查看 Alice 给他的授权额度"):
            allowance = token.user_check_allowance(alice, bob)
            attach_user_action("查看授权额度", **allowance)

            assert allowance['allowance'] == authorize_amount, \
                f"授权额度不正确，期望: {authorize_amount}, 实际: {allowance['allowance']}"

    @allure.title("场景：Bob 使用 Alice 的授权额度转账")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("用户场景：Bob 使用 Alice 授权的额度，从 Alice 账户转账给 Charlie")
    def test_bob_use_alice_allowance(self, alice_authorized_bob, test_accounts):
        """
        用户场景：Bob 使用授权额度

        作为 Bob，我已经获得了 Alice 的授权
        我想要使用这个授权，从 Alice 的账户转账 50 个代币给 Charlie
        """
        token = alice_authorized_bob['token']
        alice = alice_authorized_bob['alice']
        bob = alice_authorized_bob['bob']
        charlie = test_accounts['charlie']
        allowance = alice_authorized_bob['allowance']

        transfer_amount = 50.0

        # 步骤1：Bob 确认有足够的授权额度
        with allure.step("Bob 确认授权额度足够"):
            assert allowance >= transfer_amount, \
                f"授权额度不足，当前额度: {allowance}"

        # 步骤2：Bob 使用授权额度转账
        with allure.step(f"Bob 使用授权，从 Alice 账户转账 {transfer_amount} 给 Charlie"):
            alice_balance_before = token.user_check_balance(alice)
            charlie_balance_before = token.user_check_balance(charlie)

            result = token.user_spend_allowance(bob, alice, charlie, transfer_amount)
            attach_user_action("使用授权转账", **result)

            assert result['status'] == 'success', "转账失败"

        # 步骤3：验证余额变化
        with allure.step("验证余额变化"):
            alice_balance_after = token.user_check_balance(alice)
            charlie_balance_after = token.user_check_balance(charlie)

            # Alice 余额减少
            assert alice_balance_after['balance'] == alice_balance_before['balance'] - transfer_amount, \
                "Alice 余额变化不正确"

            # Charlie 余额增加
            assert charlie_balance_after['balance'] == charlie_balance_before['balance'] + transfer_amount, \
                "Charlie 余额变化不正确"

        # 步骤4：验证授权额度减少
        with allure.step("验证授权额度减少"):
            allowance_after = token.user_check_allowance(alice, bob)
            assert allowance_after['allowance'] == allowance - transfer_amount, \
                "授权额度变化不正确"


@allure.feature("Token 合约")
@allure.story("用户查询")
class TestUserQueryScenario:
    """用户查询场景测试 - 从用户角度测试查询功能"""

    @allure.title("场景：用户查看代币基本信息")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("用户场景：用户想要了解这个代币的基本信息")
    def test_user_check_token_info(self, token_contract):
        """
        用户场景：查看代币信息

        作为一个用户，我想要了解这个代币的基本信息
        包括名称、符号、精度、总供应量等
        """
        with allure.step("用户查看代币基本信息"):
            token_info = token_contract.user_check_token_info()
            attach_user_action("查看代币信息", **token_info)

            # 验证基本信息存在
            assert token_info['name'], "代币名称不应为空"
            assert token_info['symbol'], "代币符号不应为空"
            assert token_info['decimals'] >= 0, "代币精度应该是非负数"
            assert token_info['total_supply'] > 0, "总供应量应该大于 0"

    @allure.title("场景：用户查看自己的余额")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("用户场景：用户想要查看自己有多少代币")
    def test_user_check_own_balance(self, alice_with_tokens):
        """
        用户场景：查看自己的余额

        作为 Alice，我想要查看我有多少代币
        """
        token = alice_with_tokens['token']
        alice = alice_with_tokens['alice']

        with allure.step("Alice 查看自己的余额"):
            balance_info = token.user_check_balance(alice)
            attach_balance_info("Alice", balance_info)

            # 验证余额信息完整
            assert 'balance' in balance_info, "应该包含余额信息"
            assert 'decimals' in balance_info, "应该包含精度信息"
            assert balance_info['balance'] >= 0, "余额应该是非负数"


@allure.feature("Token 合约")
@allure.story("边界场景")
class TestUserEdgeCaseScenario:
    """用户边界场景测试 - 测试边界情况"""

    @allure.title("场景：用户转账 0 个代币")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("用户场景：用户尝试转账 0 个代币")
    def test_user_transfer_zero_amount(self, alice_and_bob):
        """
        用户场景：转账 0 个代币

        作为 Alice，当我尝试转账 0 个代币时
        系统的行为应该是明确的（允许或拒绝）
        """
        token = alice_and_bob['token']
        alice = alice_and_bob['alice']
        bob = alice_and_bob['bob']

        with allure.step("Alice 尝试转账 0 个代币给 Bob"):
            try:
                result = token.user_transfer_to(alice, bob, 0.0)
                attach_user_action("转账 0 代币", **result)

                # 如果允许，验证余额未变化
                alice_balance = token.user_check_balance(alice)
                bob_balance = token.user_check_balance(bob)

                assert alice_balance['balance'] == alice_and_bob['alice_balance'], \
                    "Alice 余额不应该变化"
                assert bob_balance['balance'] == alice_and_bob['bob_balance'], \
                    "Bob 余额不应该变化"

            except Exception as e:
                # 如果拒绝，记录错误
                attach_user_action("转账 0 代币被拒绝", error=str(e))

    @allure.title("场景：用户授权 0 额度")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("用户场景：用户授权 0 额度（取消授权）")
    def test_user_authorize_zero_amount(self, alice_authorized_bob):
        """
        用户场景：授权 0 额度（取消授权）

        作为 Alice，我想要取消之前给 Bob 的授权
        我可以通过授权 0 额度来实现
        """
        token = alice_authorized_bob['token']
        alice = alice_authorized_bob['alice']
        bob = alice_authorized_bob['bob']

        with allure.step("Alice 授权 Bob 0 额度（取消授权）"):
            result = token.user_authorize_spender(alice, bob, 0.0)
            attach_user_action("取消授权", **result)

        with allure.step("验证授权额度为 0"):
            allowance = token.user_check_allowance(alice, bob)
            assert allowance['allowance'] == 0, "授权额度应该为 0"
