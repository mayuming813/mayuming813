#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : dex_fixtures.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : DEX Swap 场景 Fixtures
"""

import pytest
import allure
from framework.web3 import Web3Client, HardhatClient, RPCClient
from tests.dex_swap.apis import DEXAPI, ERC20API


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
def token_a_deployed(hardhat_client):
    """场景：部署 Token A"""
    with allure.step("部署 Token A"):
        address = hardhat_client.deploy_contract(
            "MockERC20",
            ["Token A", "TKA", 18]
        )
        assert address, "Token A 部署失败"

    abi, _ = hardhat_client.load_contract_artifact("MockERC20")
    return {'address': address, 'abi': abi, 'name': 'Token A', 'symbol': 'TKA', 'decimals': 18}


@pytest.fixture(scope="session")
def token_b_deployed(hardhat_client):
    """场景：部署 Token B"""
    with allure.step("部署 Token B"):
        address = hardhat_client.deploy_contract(
            "MockERC20",
            ["Token B", "TKB", 18]
        )
        assert address, "Token B 部署失败"

    abi, _ = hardhat_client.load_contract_artifact("MockERC20")
    return {'address': address, 'abi': abi, 'name': 'Token B', 'symbol': 'TKB', 'decimals': 18}


@pytest.fixture(scope="session")
def dex_deployed(hardhat_client):
    """场景：部署 DEX 合约"""
    with allure.step("部署 DEX 合约"):
        address = hardhat_client.deploy_contract("SimpleDEX", [])
        assert address, "DEX 部署失败"

    abi, _ = hardhat_client.load_contract_artifact("SimpleDEX")
    return {'address': address, 'abi': abi}


@pytest.fixture(scope="function")
def dex_api(web3_client, dex_deployed):
    """DEX API"""
    return DEXAPI(web3_client, dex_deployed['address'], dex_deployed['abi'])


@pytest.fixture(scope="function")
def token_a_api(web3_client, token_a_deployed):
    """Token A API"""
    return ERC20API(web3_client, token_a_deployed['address'], token_a_deployed['abi'])


@pytest.fixture(scope="function")
def token_b_api(web3_client, token_b_deployed):
    """Token B API"""
    return ERC20API(web3_client, token_b_deployed['address'], token_b_deployed['abi'])


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
def tokens_minted(token_a_api, token_b_api, owner, user1, user2, web3_client):
    """场景：Mint Token 给用户"""
    amount = web3_client.to_wei(10000, 'ether')

    with allure.step("Mint Token A 给用户"):
        for user in [user1, user2]:
            tx_hash = token_a_api.mint(user.address, amount, owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1

    with allure.step("Mint Token B 给用户"):
        for user in [user1, user2]:
            tx_hash = token_b_api.mint(user.address, amount, owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1

    return {
        'token_a': token_a_api.address,
        'token_b': token_b_api.address,
        'amount': amount
    }


@pytest.fixture(scope="function")
def pool_created(dex_api, token_a_api, token_b_api, owner, web3_client):
    """场景：创建流动性池"""
    with allure.step("创建流动性池"):
        tx_hash = dex_api.create_pool(token_a_api.address, token_b_api.address, owner)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1, "创建流动性池失败"

    with allure.step("获取 Pool ID"):
        pool_id = dex_api.get_pool_id(token_a_api.address, token_b_api.address)

    return {
        'pool_id': pool_id,
        'token_a': token_a_api.address,
        'token_b': token_b_api.address
    }


@pytest.fixture(scope="function")
def tokens_approved(dex_api, token_a_api, token_b_api, user1, web3_client):
    """场景：用户授权 Token 给 DEX"""
    max_amount = 2**256 - 1

    with allure.step("授权 Token A 给 DEX"):
        tx_hash = token_a_api.approve(dex_api.address, max_amount, user1)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    with allure.step("授权 Token B 给 DEX"):
        tx_hash = token_b_api.approve(dex_api.address, max_amount, user1)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {
        'user': user1.address,
        'dex': dex_api.address,
        'amount': max_amount
    }


@pytest.fixture(scope="function")
def liquidity_added(
    dex_api,
    token_a_api,
    token_b_api,
    pool_created,
    tokens_minted,
    tokens_approved,
    user1,
    web3_client
):
    """场景：添加流动性"""
    amount_a = web3_client.to_wei(1000, 'ether')
    amount_b = web3_client.to_wei(2000, 'ether')

    with allure.step("添加流动性"):
        tx_hash = dex_api.add_liquidity(
            token_a_api.address,
            token_b_api.address,
            amount_a,
            amount_b,
            user1
        )
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1, "添加流动性失败"

    with allure.step("获取流动性信息"):
        pool = dex_api.get_pool(pool_created['pool_id'])
        liquidity = dex_api.get_liquidity_balance(pool_created['pool_id'], user1.address)

    return {
        'pool_id': pool_created['pool_id'],
        'token_a': token_a_api.address,
        'token_b': token_b_api.address,
        'amount_a': amount_a,
        'amount_b': amount_b,
        'liquidity': liquidity,
        'provider': user1.address,
        'pool': pool
    }


@pytest.fixture(scope="function")
def user2_tokens_approved(dex_api, token_a_api, token_b_api, user2, web3_client):
    """场景：用户 2 授权 Token 给 DEX"""
    max_amount = 2**256 - 1

    with allure.step("用户 2 授权 Token A 给 DEX"):
        tx_hash = token_a_api.approve(dex_api.address, max_amount, user2)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    with allure.step("用户 2 授权 Token B 给 DEX"):
        tx_hash = token_b_api.approve(dex_api.address, max_amount, user2)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    return {
        'user': user2.address,
        'dex': dex_api.address
    }
