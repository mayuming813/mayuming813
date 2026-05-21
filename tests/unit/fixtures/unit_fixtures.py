#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : unit_fixtures.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from web3 import Web3
from tests.unit.business.token_business import TokenBusiness
from framework.core.web3_manager import Web3Manager
from framework.utils.test_data_factory import TestDataFactory
from framework.core.config import config


# ==================== Allure 报告增强 ====================

def attach_user_action(action: str, **data):
    """附加用户行为信息"""
    import json
    action_info = {
        'action': action,
        **data
    }
    allure.attach(
        json.dumps(action_info, indent=2, ensure_ascii=False),
        name=f"👤 用户行为: {action}",
        attachment_type=allure.attachment_type.JSON
    )


def attach_balance_info(user: str, balance_info: dict):
    """附加余额信息"""
    import json
    allure.attach(
        json.dumps({
            'user': user,
            **balance_info
        }, indent=2, ensure_ascii=False),
        name=f"💰 余额信息",
        attachment_type=allure.attachment_type.JSON
    )


# ==================== 基础 Fixtures ====================

@pytest.fixture(scope="session")
def web3_manager():
    """Web3Manager fixture（session级别）"""
    manager = Web3Manager()
    yield manager


@pytest.fixture(scope="function")
def test_data():
    """测试数据工厂 fixture"""
    return TestDataFactory()


@pytest.fixture(scope="function")
def test_accounts(web3_manager):
    """
    测试账户 fixture（用户视角）
    返回模拟的用户账户
    """
    w3 = web3_manager.w3
    accounts = w3.eth.accounts[:5]

    return {
        'alice': accounts[0],  # 用户 Alice
        'bob': accounts[1],    # 用户 Bob
        'charlie': accounts[2], # 用户 Charlie
        'dave': accounts[3],   # 用户 Dave
        'admin': accounts[4]   # 管理员
    }


# ==================== 业务场景 Fixtures ====================

@pytest.fixture(scope="function")
def token_contract(web3_manager, test_accounts):
    """
    场景模块：部署 Token 合约
    返回：TokenBusiness 实例
    """
    with allure.step("部署 Token 合约"):
        # 简化：假设合约已部署
        contract_address = config.get('token_contract_address', '0x' + '0' * 40)
        token = TokenBusiness(contract_address, web3_manager)

        # 获取代币信息
        token_info = token.user_check_token_info()
        attach_user_action("查看代币信息", **token_info)

    return token


@pytest.fixture(scope="function")
def alice_with_tokens(token_contract, test_accounts):
    """
    场景模块：Alice 拥有代币
    用户场景：Alice 是一个拥有代币的用户
    """
    alice = test_accounts['alice']

    with allure.step("Alice 查看自己的余额"):
        balance_info = token_contract.user_check_balance(alice)
        attach_balance_info("Alice", balance_info)

    return {
        'token': token_contract,
        'alice': alice,
        'alice_balance': balance_info['balance']
    }


@pytest.fixture(scope="function")
def alice_and_bob(token_contract, test_accounts):
    """
    场景模块：Alice 和 Bob 两个用户
    用户场景：两个用户准备进行交互
    """
    alice = test_accounts['alice']
    bob = test_accounts['bob']

    with allure.step("Alice 和 Bob 查看各自余额"):
        alice_balance = token_contract.user_check_balance(alice)
        bob_balance = token_contract.user_check_balance(bob)

        attach_balance_info("Alice", alice_balance)
        attach_balance_info("Bob", bob_balance)

    return {
        'token': token_contract,
        'alice': alice,
        'bob': bob,
        'alice_balance': alice_balance['balance'],
        'bob_balance': bob_balance['balance']
    }


@pytest.fixture(scope="function")
def alice_authorized_bob(alice_and_bob):
    """
    场景模块：Alice 授权 Bob
    用户场景：Alice 授权 Bob 可以使用她的代币
    """
    token = alice_and_bob['token']
    alice = alice_and_bob['alice']
    bob = alice_and_bob['bob']

    with allure.step("Alice 授权 Bob 使用 100 代币"):
        result = token.user_authorize_spender(alice, bob, 100.0)
        attach_user_action("授权", **result)

    with allure.step("Bob 查看授权额度"):
        allowance = token.user_check_allowance(alice, bob)
        attach_user_action("查看授权额度", **allowance)

    return {
        **alice_and_bob,
        'allowance': allowance['allowance']
    }


# ==================== 快照 Fixture ====================

@pytest.fixture(scope="function", autouse=True)
def snapshot(web3_manager):
    """
    自动快照 fixture
    每个测试前创建快照，测试后恢复
    避免测试间状态污染
    """
    w3 = web3_manager.w3

    try:
        # 创建快照
        snapshot_id = w3.provider.make_request("evm_snapshot", [])['result']
        yield
        # 恢复快照
        w3.provider.make_request("evm_revert", [snapshot_id])
    except:
        # 如果不支持快照（非测试网络），跳过
        yield
