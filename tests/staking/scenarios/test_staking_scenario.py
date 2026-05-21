#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_staking_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : Staking 场景测试
"""

import pytest
import allure
import time
from framework.core.logger import logger


@allure.feature("Staking")
@allure.story("质押场景")
class TestStakingScenario:
    """质押场景测试"""

    def test_basic_staking_scenario(
        self,
        staking_api,
        staking_token_api,
        reward_token_api,
        tokens_minted,
        staking_approved,
        reward_deposited,
        user1,
        web3_client
    ):
        """场景：基础质押流程"""
        stake_amount = web3_client.to_wei(1000, 'ether')

        with allure.step("质押代币"):
            tx_hash = staking_api.stake(stake_amount, user1)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "质押交易失败"

        with allure.step("验证质押余额"):
            staked = staking_api.staked_balance(user1.address)
            assert staked == stake_amount, f"质押余额不正确: {staked}"

        with allure.step("验证总质押量"):
            total_staked = staking_api.total_staked()
            assert total_staked == stake_amount, f"总质押量不正确: {total_staked}"

        with allure.step("验证代币转移"):
            user_balance = staking_token_api.balance_of(user1.address)
            expected_balance = tokens_minted['staking_amount'] - stake_amount
            assert user_balance == expected_balance, f"用户余额不正确: {user_balance}"

        logger.info(f"✅ 基础质押场景测试通过")

    def test_reward_calculation_scenario(
        self,
        staking_api,
        user_staked,
        web3_client,
        rpc_client
    ):
        """场景：奖励计算"""
        stake_amount = user_staked['amount']
        reward_rate = staking_api.reward_rate()

        with allure.step("等待一段时间累积奖励"):
            time.sleep(5)
            rpc_client.mine_blocks(5)

        with allure.step("查询已赚取的奖励"):
            earned = staking_api.earned(user_staked['user'])
            assert earned > 0, "奖励应该大于 0"

        with allure.step("验证奖励计算逻辑"):
            # 奖励 = 质押量 * 奖励速率 * 时间
            # 由于时间不精确，只验证奖励在合理范围内
            min_expected = reward_rate * 5  # 至少 5 秒的奖励
            assert earned >= min_expected, f"奖励过低: {earned} < {min_expected}"

        logger.info(f"✅ 奖励计算场景测试通过，累积奖励: {web3_client.from_wei(earned, 'ether')} RWD")

    def test_withdraw_scenario(
        self,
        staking_api,
        staking_token_api,
        user_staked,
        user1,
        web3_client,
        rpc_client
    ):
        """场景：解押代币"""
        stake_amount = user_staked['amount']
        withdraw_amount = web3_client.to_wei(500, 'ether')

        with allure.step("等待锁定期结束"):
            lock_duration = staking_api.lock_duration()
            # 快进时间
            rpc_client.increase_time(lock_duration + 1)
            rpc_client.mine_blocks(1)

        with allure.step("记录解押前余额"):
            balance_before = staking_token_api.balance_of(user1.address)

        with allure.step("解押部分代币"):
            tx_hash = staking_api.withdraw(withdraw_amount, user1)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "解押交易失败"

        with allure.step("验证质押余额"):
            staked = staking_api.staked_balance(user1.address)
            expected_staked = stake_amount - withdraw_amount
            assert staked == expected_staked, f"质押余额不正确: {staked}"

        with allure.step("验证代币返还"):
            balance_after = staking_token_api.balance_of(user1.address)
            assert balance_after == balance_before + withdraw_amount, "代币返还不正确"

        logger.info(f"✅ 解押场景测试通过")

    def test_lock_duration_enforcement_scenario(
        self,
        staking_api,
        user_staked,
        user1,
        web3_client
    ):
        """场景：锁定期限制"""
        withdraw_amount = web3_client.to_wei(100, 'ether')

        with allure.step("尝试在锁定期内解押"):
            with pytest.raises(Exception) as exc_info:
                tx_hash = staking_api.withdraw(withdraw_amount, user1)
                web3_client.wait_for_transaction_receipt(tx_hash)

            assert "Tokens are locked" in str(exc_info.value) or "revert" in str(exc_info.value).lower(), \
                "应该因为锁定期而失败"

        with allure.step("验证质押余额未变"):
            staked = staking_api.staked_balance(user1.address)
            assert staked == user_staked['amount'], "质押余额不应该改变"

        logger.info(f"✅ 锁定期限制场景测试通过")

    def test_claim_reward_scenario(
        self,
        staking_api,
        reward_token_api,
        user_staked,
        user1,
        web3_client,
        rpc_client
    ):
        """场景：领取奖励"""
        with allure.step("等待累积奖励"):
            time.sleep(3)
            rpc_client.mine_blocks(3)

        with allure.step("查询可领取奖励"):
            earned_before = staking_api.earned(user1.address)
            assert earned_before > 0, "应该有可领取的奖励"

        with allure.step("记录领取前余额"):
            balance_before = reward_token_api.balance_of(user1.address)

        with allure.step("领取奖励"):
            tx_hash = staking_api.get_reward(user1)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "领取奖励交易失败"

        with allure.step("验证奖励已领取"):
            balance_after = reward_token_api.balance_of(user1.address)
            reward_received = balance_after - balance_before
            assert reward_received > 0, "应该收到奖励代币"
            assert reward_received >= earned_before * 0.9, "收到的奖励应该接近查询的数量"

        with allure.step("验证已领取奖励清零"):
            earned_after = staking_api.earned(user1.address)
            assert earned_after == 0, "领取后奖励应该清零"

        logger.info(f"✅ 领取奖励场景测试通过，领取: {web3_client.from_wei(reward_received, 'ether')} RWD")

    def test_exit_scenario(
        self,
        staking_api,
        staking_token_api,
        reward_token_api,
        user_staked,
        user1,
        web3_client,
        rpc_client
    ):
        """场景：退出（解押 + 领取奖励）"""
        stake_amount = user_staked['amount']

        with allure.step("等待锁定期结束并累积奖励"):
            lock_duration = staking_api.lock_duration()
            rpc_client.increase_time(lock_duration + 1)
            rpc_client.mine_blocks(5)

        with allure.step("记录退出前余额"):
            staking_balance_before = staking_token_api.balance_of(user1.address)
            reward_balance_before = reward_token_api.balance_of(user1.address)
            earned = staking_api.earned(user1.address)

        with allure.step("执行退出"):
            tx_hash = staking_api.exit(user1)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "退出交易失败"

        with allure.step("验证质押已清空"):
            staked = staking_api.staked_balance(user1.address)
            assert staked == 0, "质押余额应该为 0"

        with allure.step("验证质押代币已返还"):
            staking_balance_after = staking_token_api.balance_of(user1.address)
            assert staking_balance_after == staking_balance_before + stake_amount, "质押代币未正确返还"

        with allure.step("验证奖励已领取"):
            reward_balance_after = reward_token_api.balance_of(user1.address)
            reward_received = reward_balance_after - reward_balance_before
            assert reward_received > 0, "应该收到奖励"
            assert reward_received >= earned * 0.9, "收到的奖励应该接近查询的数量"

        logger.info(f"✅ 退出场景测试通过")

    def test_multiple_users_staking_scenario(
        self,
        staking_api,
        multiple_users_staked,
        web3_client
    ):
        """场景：多用户质押"""
        user1_data = multiple_users_staked['user1']
        user2_data = multiple_users_staked['user2']

        with allure.step("验证用户 1 质押"):
            staked1 = staking_api.staked_balance(user1_data['user'])
            assert staked1 == user1_data['amount'], "用户 1 质押余额不正确"

        with allure.step("验证用户 2 质押"):
            staked2 = staking_api.staked_balance(user2_data['user'])
            assert staked2 == user2_data['amount'], "用户 2 质押余额不正确"

        with allure.step("验证总质押量"):
            total_staked = staking_api.total_staked()
            expected_total = user1_data['amount'] + user2_data['amount']
            assert total_staked == expected_total, f"总质押量不正确: {total_staked}"

        logger.info(f"✅ 多用户质押场景测试通过")

    def test_owner_set_reward_rate_scenario(
        self,
        staking_api,
        owner,
        web3_client
    ):
        """场景：Owner 设置奖励速率"""
        new_rate = web3_client.to_wei(0.2, 'ether')

        with allure.step("设置新的奖励速率"):
            tx_hash = staking_api.set_reward_rate(new_rate, owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "设置奖励速率交易失败"

        with allure.step("验证奖励速率已更新"):
            current_rate = staking_api.reward_rate()
            assert current_rate == new_rate, f"奖励速率未正确更新: {current_rate}"

        logger.info(f"✅ 设置奖励速率场景测试通过")

    def test_owner_set_lock_duration_scenario(
        self,
        staking_api,
        owner,
        web3_client
    ):
        """场景：Owner 设置锁定时间"""
        new_duration = 172800  # 2 天

        with allure.step("设置新的锁定时间"):
            tx_hash = staking_api.set_lock_duration(new_duration, owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "设置锁定时间交易失败"

        with allure.step("验证锁定时间已更新"):
            current_duration = staking_api.lock_duration()
            assert current_duration == new_duration, f"锁定时间未正确更新: {current_duration}"

        logger.info(f"✅ 设置锁定时间场景测试通过")

    def test_get_staking_info_scenario(
        self,
        staking_api,
        user_staked,
        rpc_client
    ):
        """场景：查询质押信息"""
        with allure.step("等待累积奖励"):
            time.sleep(2)
            rpc_client.mine_blocks(2)

        with allure.step("查询质押信息"):
            info = staking_api.get_staking_info(user_staked['user'])

        with allure.step("验证质押信息"):
            assert info['staked'] == user_staked['amount'], "质押量不正确"
            assert info['earned_rewards'] > 0, "应该有累积奖励"
            assert info['lock_time_remaining'] > 0, "应该还在锁定期内"

        logger.info(f"✅ 查询质押信息场景测试通过")

    def test_unauthorized_owner_operation_scenario(
        self,
        staking_api,
        user1,
        web3_client
    ):
        """场景：非 Owner 尝试管理操作"""
        new_rate = web3_client.to_wei(0.5, 'ether')

        with allure.step("非 Owner 尝试设置奖励速率"):
            with pytest.raises(Exception) as exc_info:
                tx_hash = staking_api.set_reward_rate(new_rate, user1)
                web3_client.wait_for_transaction_receipt(tx_hash)

            assert "Ownable" in str(exc_info.value) or "revert" in str(exc_info.value).lower(), \
                "应该因为权限不足而失败"

        logger.info(f"✅ 非授权操作场景测试通过")

