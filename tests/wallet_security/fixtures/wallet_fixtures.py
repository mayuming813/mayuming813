#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : wallet_fixtures.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 钱包签名和授权场景 Fixtures
"""

import pytest
import allure
import time
from framework.web3 import Web3Client, HardhatClient, RPCClient
from tests.wallet_security.apis import WalletAPI


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
def permit_token_deployed(hardhat_client):
    """场景：部署支持 Permit 的代币合约"""
    with allure.step("部署 MockERC20Permit 合约"):
        address = hardhat_client.deploy_contract(
            "MockERC20Permit",
            ["Permit Token", "PMT", 18]
        )
        assert address, "Permit 代币部署失败"

    abi, _ = hardhat_client.load_contract_artifact("MockERC20Permit")
    return {'address': address, 'abi': abi, 'name': 'Permit Token', 'symbol': 'PMT'}


@pytest.fixture(scope="function")
def wallet_api(web3_client, permit_token_deployed):
    """Wallet API"""
    return WalletAPI(web3_client, permit_token_deployed['address'], permit_token_deployed['abi'])


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
def spender(signers):
    """被授权的支出者"""
    return signers[3]


@pytest.fixture(scope="function")
def tokens_minted(wallet_api, owner, user1, user2, web3_client):
    """场景：Mint 代币给用户"""
    mint_amount = web3_client.to_wei(10000, 'ether')

    with allure.step("Mint 代币给测试用户"):
        for user in [owner, user1, user2]:
            tx_hash = wallet_api.client.send_contract_transaction(
                wallet_api.contract,
                "mint",
                owner,
                user.address,
                mint_amount
            )
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1

    return {'mint_amount': mint_amount}


@pytest.fixture(scope="function")
def approved_spender(wallet_api, user1, spender, web3_client):
    """场景：用户授权给 Spender"""
    approve_amount = web3_client.to_wei(1000, 'ether')

    with allure.step("授权代币给 Spender"):
        tx_hash = wallet_api.approve(spender.address, approve_amount, user1)
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    with allure.step("验证授权额度"):
        allowance = wallet_api.allowance(user1.address, spender.address)
        assert allowance == approve_amount

    return {
        'owner': user1.address,
        'spender': spender.address,
        'amount': approve_amount
    }


@pytest.fixture(scope="function")
def permit_signature_generated(wallet_api, user1, spender, web3_client):
    """场景：生成 Permit 签名"""
    value = web3_client.to_wei(500, 'ether')
    deadline = int(time.time()) + 3600  # 1 小时后过期

    with allure.step("生成 Permit 签名"):
        signature_data = wallet_api.generate_permit_signature(
            owner_account=user1,
            spender=spender.address,
            value=value,
            deadline=deadline
        )

    return {
        'owner': user1.address,
        'spender': spender.address,
        'value': value,
        'deadline': deadline,
        'signature': signature_data
    }


@pytest.fixture(scope="function")
def permit_executed(wallet_api, permit_signature_generated, spender, web3_client):
    """场景：执行 Permit 授权"""
    permit_data = permit_signature_generated
    sig = permit_data['signature']

    with allure.step("执行 Permit 授权"):
        tx_hash = wallet_api.permit(
            owner=permit_data['owner'],
            spender=permit_data['spender'],
            value=permit_data['value'],
            deadline=permit_data['deadline'],
            v=sig['v'],
            r=sig['r'],
            s=sig['s'],
            from_account=spender
        )
        receipt = web3_client.wait_for_transaction_receipt(tx_hash)
        assert receipt['status'] == 1

    with allure.step("验证授权额度"):
        allowance = wallet_api.allowance(permit_data['owner'], permit_data['spender'])
        assert allowance == permit_data['value']

    return permit_data


@pytest.fixture(scope="function")
def personal_message_signed(wallet_api, user1):
    """场景：签名个人消息"""
    message = "Hello, Web3 World!"

    with allure.step("签名个人消息"):
        signature_data = wallet_api.sign_personal_message(user1, message)

    return {
        'signer': user1.address,
        'message': message,
        'signature': signature_data
    }


@pytest.fixture(scope="function")
def typed_data_signed(wallet_api, user1, web3_client):
    """场景：签名结构化数据 (EIP-712)"""
    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"}
            ],
            "Mail": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "contents", "type": "string"}
            ]
        },
        "primaryType": "Mail",
        "domain": {
            "name": "Test Mail",
            "version": "1",
            "chainId": 31337,
            "verifyingContract": wallet_api.address
        },
        "message": {
            "from": user1.address,
            "to": "0x0000000000000000000000000000000000000000",
            "contents": "Hello, EIP-712!"
        }
    }

    with allure.step("签名结构化数据"):
        signature_data = wallet_api.sign_typed_data(user1, typed_data)

    return {
        'signer': user1.address,
        'typed_data': typed_data,
        'signature': signature_data
    }


@pytest.fixture(scope="function")
def expired_permit_signature(wallet_api, user1, spender, web3_client):
    """场景：生成已过期的 Permit 签名"""
    value = web3_client.to_wei(500, 'ether')
    deadline = int(time.time()) - 3600  # 1 小时前已过期

    with allure.step("生成已过期的 Permit 签名"):
        signature_data = wallet_api.generate_permit_signature(
            owner_account=user1,
            spender=spender.address,
            value=value,
            deadline=deadline
        )

    return {
        'owner': user1.address,
        'spender': spender.address,
        'value': value,
        'deadline': deadline,
        'signature': signature_data
    }


@pytest.fixture(scope="function")
def invalid_permit_signature(wallet_api, user1, user2, spender, web3_client):
    """场景：生成无效的 Permit 签名（签名者与 owner 不匹配）"""
    value = web3_client.to_wei(500, 'ether')
    deadline = int(time.time()) + 3600

    with allure.step("使用错误的账户生成签名"):
        # 使用 user2 签名，但声称是 user1 的授权
        signature_data = wallet_api.generate_permit_signature(
            owner_account=user2,  # 错误的签名者
            spender=spender.address,
            value=value,
            deadline=deadline
        )

    return {
        'owner': user1.address,  # 声称的 owner
        'actual_signer': user2.address,  # 实际签名者
        'spender': spender.address,
        'value': value,
        'deadline': deadline,
        'signature': signature_data
    }
