#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : nft_fixtures.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : NFT Mint 场景 Fixtures
"""

import pytest
import json
import allure
from pathlib import Path
from framework.web3 import Web3Client, HardhatClient, RPCClient
from tests.nft_mint.apis import NFTContractAPI
from tests.nft_mint.rpcs import NFTRPC
from framework.utils.test_data_factory import TestDataFactory


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
def nft_contract_deployed(hardhat_client):
    """场景：部署 NFT 合约"""
    with allure.step("编译合约"):
        assert hardhat_client.compile(), "合约编译失败"

    with allure.step("部署 NFT 合约"):
        contract_address = hardhat_client.deploy_contract(
            "MockERC721",
            ["Test NFT", "TNFT", 10000, hardhat_client.web3_client.to_wei(0.01, 'ether')]
        )
        assert contract_address, "合约部署失败"

    # 加载 ABI
    abi, _ = hardhat_client.load_contract_artifact("MockERC721")

    return {
        'address': contract_address,
        'abi': abi,
        'name': 'Test NFT',
        'symbol': 'TNFT',
        'max_supply': 10000,
        'mint_price': hardhat_client.web3_client.to_wei(0.01, 'ether')
    }


@pytest.fixture(scope="function")
def nft_api(web3_client, nft_contract_deployed):
    """NFT 合约 API"""
    return NFTContractAPI(
        web3_client,
        nft_contract_deployed['address'],
        nft_contract_deployed['abi']
    )


@pytest.fixture(scope="function")
def nft_rpc(rpc_client):
    """NFT RPC"""
    return NFTRPC(rpc_client)


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
def minted_nft(nft_api, user1, web3_client):
    """场景：Mint 一个 NFT"""
    with allure.step("准备 Mint 数据"):
        token_uri = f"ipfs://QmTest{TestDataFactory.unique_id()}"
        mint_price = nft_api.mint_price()

    with allure.step(f"用户 Mint NFT: {token_uri}"):
        tx_hash = nft_api.mint(user1.address, token_uri, user1, value=mint_price)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1, "Mint 交易失败"

    with allure.step("获取 Token ID"):
        # 从事件中解析 Token ID
        token_id = nft_api.total_supply() - 1

    return {
        'token_id': token_id,
        'token_uri': token_uri,
        'owner': user1.address,
        'tx_hash': tx_hash,
        'receipt': receipt
    }


@pytest.fixture(scope="function")
def multiple_minted_nfts(nft_api, user1, user2, web3_client):
    """场景：Mint 多个 NFT"""
    nfts = []
    mint_price = nft_api.mint_price()

    with allure.step("用户 1 Mint 3 个 NFT"):
        for i in range(3):
            token_uri = f"ipfs://QmTest{TestDataFactory.unique_id()}"
            tx_hash = nft_api.mint(user1.address, token_uri, user1, value=mint_price)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1

            token_id = nft_api.total_supply() - 1
            nfts.append({
                'token_id': token_id,
                'token_uri': token_uri,
                'owner': user1.address,
                'tx_hash': tx_hash
            })

    with allure.step("用户 2 Mint 2 个 NFT"):
        for i in range(2):
            token_uri = f"ipfs://QmTest{TestDataFactory.unique_id()}"
            tx_hash = nft_api.mint(user2.address, token_uri, user2, value=mint_price)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1

            token_id = nft_api.total_supply() - 1
            nfts.append({
                'token_id': token_id,
                'token_uri': token_uri,
                'owner': user2.address,
                'tx_hash': tx_hash
            })

    return nfts


@pytest.fixture(scope="function")
def nft_with_approval(nft_api, minted_nft, user1, user2, web3_client):
    """场景：NFT 已授权"""
    with allure.step(f"授权 NFT {minted_nft['token_id']} 给 user2"):
        tx_hash = nft_api.approve(user2.address, minted_nft['token_id'], user1)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1, "授权失败"

    with allure.step("验证授权"):
        approved = nft_api.get_approved(minted_nft['token_id'])
        assert approved.lower() == user2.address.lower(), "授权地址不匹配"

    return {
        **minted_nft,
        'approved_to': user2.address,
        'approval_tx_hash': tx_hash
    }


@pytest.fixture(scope="function")
def paused_nft_contract(nft_api, owner, web3_client):
    """场景：NFT 合约已暂停"""
    with allure.step("暂停 NFT 合约"):
        tx_hash = nft_api.set_paused(True, owner)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1, "暂停失败"

    with allure.step("验证暂停状态"):
        assert nft_api.paused() is True, "合约未暂停"

    yield

    # 恢复
    with allure.step("恢复 NFT 合约"):
        tx_hash = nft_api.set_paused(False, owner)
        web3_client.wait_for_transaction_receipt(tx_hash)


@pytest.fixture(scope="function")
def nft_contract_with_balance(nft_api, user1, web3_client, owner):
    """场景：NFT 合约有余额"""
    mint_price = nft_api.mint_price()

    with allure.step("Mint 多个 NFT 以积累合约余额"):
        for i in range(5):
            token_uri = f"ipfs://QmTest{TestDataFactory.unique_id()}"
            tx_hash = nft_api.mint(user1.address, token_uri, user1, value=mint_price)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1

    with allure.step("获取合约余额"):
        contract_balance = web3_client.get_balance(nft_api.address)
        assert contract_balance > 0, "合约余额为 0"

    return {
        'contract_address': nft_api.address,
        'balance': contract_balance,
        'owner': owner
    }
