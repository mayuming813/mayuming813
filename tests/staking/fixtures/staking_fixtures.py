#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : staking_fixtures.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : Staking 场景 Fixtures
"""

import pytest
import allure
import time
from framework.web3 import Web3Client, HardhatClient, RPCClient
from tests.staking.apis import StakingAPI
from tests.dex_swap.apis import ERC20API


@pytest.fixture(scope="session")
def hardhat_client():
    """Hardhat 客户端"""
    return HardhatClient()


@pytest.fixture(scope="session")
def web3_client():
    """Web3 客户端"""
    return Web3Client("http://127.0.0.1:8545")


@pytest.fixture(scope="session")
def rpc_client():
    """RPC 客户端"""
    return RPCClient("http://127.0.0.1:8545")


@pytest.fixture(scope="session")
def staking_token_deployed(hardhat_client):
    """场景：部署质押代币"""
    with allure.step("部署质押代币"):
        address = hardhat_client.deploy_contract(
            "MockERC20",
            ["Staking Token", "STK", 18]
        )
        assert address, "质押代币部署失败"

    abi, _ = hardhat_client.load_contract_artifact("MockERC20")
    return {'address': address, 'abi': abi, 'name': 'Staking Token', 'symbol': 'STK'}


@pytest.fixture(scope="session")
def reward_token_deployed(hardhat_client):
    """场景：部署奖励代币"""
    with allure.step("部署奖励代币"):
        address = hardhat_client.deploy_contract(
            "MockERC20",
            ["Reward Token", "RWD", 18]
        )
        assert address, "奖励代币部署失败"

    abi, _ = hardhat_client.load_contract_artifact("MockERC20")
    return {'address': address, 'abi': abi, 'name': 'Reward Token', 'symbol': 'RWD'}


@pytest.fixture(scope="session")
def staking_pool_deployed(hardhat_client, staking_token_deployed, reward_token_deployed, web3_client):
    """场景：部署 Staking 合约"""
    with allure.step("部署 Staking 合约"):
        reward_rate = web3_client.to_wei(0.1, 'ether')  # 0.1 token/秒
        lock_duration = 86400  # 1 天

        address = hardhat_client.deploy_contract(
            "StakingPool",
            [
                staking_token_deployed['address'],
                reward_token_deployed['address'],
                reward_rate,
                lock_duration
            ]
        )
        assert address, "Staking 合约部署失败"

    abi, _ = hardhat_client.load_contract_artifact("StakingPool")
    return {
        'address': address,
        'abi': abi,
        'reward_rate': reward_rate,
        'lock_duration': lock_duration
    }


@pytest.fixture(scope="function")
def staking_api(web3_client, staking_pool_deployed):
    """Staking API"""
    return StakingAPI(web3_client, staking_pool_deployed['address'], staking_pool_deployed['abi'])


@pytest.fixture(scope="function")
def staking_token_api(web3_client, staking_token_deployed):
    """质押代币 API"""
    return ERC20API(web3_client, staking_token_deployed['address'], staking_token_deployed['abi'])


@pytest.fixture(scope="function")
def reward_token_api(web3_client, reward_token_deployed):
    """奖励代币 API"""
    return ERC20API(web3_client, reward_token_deployed['address'], reward_token_deployed['abi'])


@pytest.fixture(scope="function")
def signers(hardhat_client):
    """获取测试账户"""
    return hardhat_client.get_signers(10)


@pytest.fixture(scope="function")
def owner(signers):
    """合约所有者"""
    return signers[0]


@pytest.fixture(scope="function")
def user1(signers):
    """测试用户 1"""
    return signers[1]


@pytest.fixture(scope="function")
def user2(signers):
    """测试用户 2"""
    return signers[2]


@pytest.fixture(scope="function")
def tokens_minted(staking_token_api, reward_token_api, owner, user1, user2, web3_client):
    """场景：Mint 代币给用户"""
    staking_amount = web3_client.to_wei(10000, 'ether')
    reward_amount = web3_client.to_wei(100000, 'ether')

    with allure.step("Mint 质押代币给用户"):
        for user in [user1, user2]:
            tx_hash = staking_token_api.mint(user.address, staking_amount, owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1

    with allure.step("Mint 奖励代币给 Owner"):
        tx_hash = reward_token_api.mint(owner.address, reward_amount, owner)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {
        'staking_amount': staking_amount,
        'reward_amount': reward_amount
    }


@pytest.fixture(scope="function")
def staking_approved(staking_api, staking_token_api, user1, web3_client):
    """场景：用户授权质押代币"""
    max_amount = 2**256 - 1

    with allure.step("授权质押代币给 Staking 合约"):
        tx_hash = staking_token_api.approve(staking_api.address, max_amount, user1)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {'user': user1.address, 'amount': max_amount}


@pytest.fixture(scope="function")
def reward_deposited(staking_api, reward_token_api, owner, tokens_minted, web3_client):
    """场景：Owner 存入奖励代币"""
    reward_amount = tokens_minted['reward_amount']

    with allure.step("授权奖励代币给 Staking 合约"):
        tx_hash = reward_token_api.approve(staking_api.address, reward_amount, owner)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    with allure.step("存入奖励代币"):
        tx_hash = staking_api.deposit_reward_tokens(reward_amount, owner)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {'amount': reward_amount}


@pytest.fixture(scope="function")
def user_staked(
    staking_api,
    staking_token_api,
    tokens_minted,
    staking_approved,
    reward_deposited,
    user1,
    web3_client
):
    """场景：用户质押代币"""
    stake_amount = web3_client.to_wei(1000, 'ether')

    with allure.step("质押代币"):
        tx_hash = staking_api.stake(stake_amount, user1)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    with allure.step("验证质押余额"):
        staked = staking_api.staked_balance(user1.address)
        assert staked == stake_amount

    return {
        'user': user1.address,
        'amount': stake_amount,
        'tx_hash': tx_hash,
        'timestamp': int(time.time())
    }


@pytest.fixture(scope="function")
def user2_staking_approved(staking_api, staking_token_api, user2, web3_client):
    """场景：用户 2 授权质押代币"""
    max_amount = 2**256 - 1

    with allure.step("用户 2 授权质押代币"):
        tx_hash = staking_token_api.approve(staking_api.address, max_amount, user2)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {'user': user2.address}


@pytest.fixture(scope="function")
def multiple_users_staked(
    staking_api,
    user_staked,
    user2,
    user2_staking_approved,
    tokens_minted,
    web3_client
):
    """场景：多个用户质押"""
    stake_amount = web3_client.to_wei(500, 'ether')

    with allure.step("用户 2 质押代币"):
        tx_hash = staking_api.stake(stake_amount, user2)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {
        'user1': user_staked,
        'user2': {
            'user': user2.address,
            'amount': stake_amount
        }
    }
