#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_wallet_security_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 钱包签名和授权安全场景测试
"""

import pytest
import allure
import time
from framework.core.logger import logger


@allure.feature("Wallet Security")
@allure.story("钱包签名和授权场景")
class TestWalletSecurityScenario:
    """钱包签名和授权安全场景测试"""

    def test_basic_approve_scenario(
        self,
        wallet_api,
        tokens_minted,
        user1,
        spender,
        web3_client
    ):
        """场景：基础授权流程"""
        approve_amount = web3_client.to_wei(1000, 'ether')

        with allure.step("授权代币"):
            tx_hash = wallet_api.approve(spender.address, approve_amount, user1)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "授权交易失败"

        with allure.step("验证授权额度"):
            allowance = wallet_api.allowance(user1.address, spender.address)
            assert allowance == approve_amount, f"授权额度不正确: {allowance}"

        logger.info(f"✅ 基础授权场景测试通过")

    def test_transfer_from_scenario(
        self,
        wallet_api,
        tokens_minted,
        approved_spender,
        user1,
        user2,
        spender,
        web3_client
    ):
        """场景：使用授权转账"""
        transfer_amount = web3_client.to_wei(500, 'ether')

        with allure.step("记录转账前余额"):
            balance_before_user1 = wallet_api.balance_of(user1.address)
            balance_before_user2 = wallet_api.balance_of(user2.address)

        with allure.step("Spender 使用授权转账"):
            tx_hash = wallet_api.transfer_from(
                user1.address,
                user2.address,
                transfer_amount,
                spender
            )
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "转账交易失败"

        with allure.step("验证余额变化"):
            balance_after_user1 = wallet_api.balance_of(user1.address)
            balance_after_user2 = wallet_api.balance_of(user2.address)

            assert balance_after_user1 == balance_before_user1 - transfer_amount, "user1 余额不正确"
            assert balance_after_user2 == balance_before_user2 + transfer_amount, "user2 余额不正确"

        with allure.step("验证授权额度减少"):
            allowance = wallet_api.allowance(user1.address, spender.address)
            expected_allowance = approved_spender['amount'] - transfer_amount
            assert allowance == expected_allowance, f"授权额度不正确: {allowance}"

        logger.info(f"✅ 授权转账场景测试通过")

    def test_permit_signature_generation_scenario(
        self,
        wallet_api,
        tokens_minted,
        user1,
        spender,
        web3_client
    ):
        """场景：生成 Permit 签名"""
        value = web3_client.to_wei(500, 'ether')
        deadline = int(time.time()) + 3600

        with allure.step("生成 Permit 签名"):
            signature_data = wallet_api.generate_permit_signature(
                owner_account=user1,
                spender=spender.address,
                value=value,
                deadline=deadline
            )

        with allure.step("验证签名数据"):
            assert 'v' in signature_data, "签名缺少 v"
            assert 'r' in signature_data, "签名缺少 r"
            assert 's' in signature_data, "签名缺少 s"
            assert 'signature' in signature_data, "签名缺少 signature"
            assert signature_data['v'] in [27, 28], f"v 值不正确: {signature_data['v']}"

        logger.info(f"✅ Permit 签名生成场景测试通过")

    def test_permit_authorization_scenario(
        self,
        wallet_api,
        tokens_minted,
        permit_signature_generated,
        spender,
        web3_client
    ):
        """场景：使用 Permit 授权"""
        permit_data = permit_signature_generated
        sig = permit_data['signature']

        with allure.step("记录授权前的 nonce"):
            nonce_before = wallet_api.nonces(permit_data['owner'])

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
            assert receipt['status'] == 1, "Permit 交易失败"

        with allure.step("验证授权额度"):
            allowance = wallet_api.allowance(permit_data['owner'], permit_data['spender'])
            assert allowance == permit_data['value'], f"授权额度不正确: {allowance}"

        with allure.step("验证 nonce 增加"):
            nonce_after = wallet_api.nonces(permit_data['owner'])
            assert nonce_after == nonce_before + 1, f"nonce 未正确增加: {nonce_after}"

        logger.info(f"✅ Permit 授权场景测试通过")

    def test_permit_gasless_approval_scenario(
        self,
        wallet_api,
        tokens_minted,
        permit_executed,
        user2,
        spender,
        web3_client
    ):
        """场景：无 Gas 授权（Permit 的主要用途）"""
        transfer_amount = web3_client.to_wei(200, 'ether')

        with allure.step("验证 owner 无需支付 gas 即可完成授权"):
            # permit_executed fixture 中，spender 支付了 gas
            # owner (user1) 只是签名，没有发送交易
            allowance = wallet_api.allowance(permit_executed['owner'], permit_executed['spender'])
            assert allowance == permit_executed['value'], "授权未生效"

        with allure.step("Spender 使用授权转账"):
            tx_hash = wallet_api.transfer_from(
                permit_executed['owner'],
                user2.address,
                transfer_amount,
                spender
            )
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "转账失败"

        with allure.step("验证转账成功"):
            balance = wallet_api.balance_of(user2.address)
            assert balance >= transfer_amount, "转账金额不正确"

        logger.info(f"✅ 无 Gas 授权场景测试通过")

    def test_expired_permit_scenario(
        self,
        wallet_api,
        tokens_minted,
        expired_permit_signature,
        spender,
        web3_client
    ):
        """场景：过期的 Permit 签名"""
        permit_data = expired_permit_signature
        sig = permit_data['signature']

        with allure.step("尝试使用过期的 Permit"):
            with pytest.raises(Exception) as exc_info:
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
                web3_client.wait_for_transaction_receipt(tx_hash)

            assert "expired" in str(exc_info.value).lower() or "revert" in str(exc_info.value).lower(), \
                "应该因为过期而失败"

        with allure.step("验证授权未生效"):
            allowance = wallet_api.allowance(permit_data['owner'], permit_data['spender'])
            assert allowance == 0, "授权不应该生效"

        logger.info(f"✅ 过期 Permit 场景测试通过")

    def test_invalid_permit_signature_scenario(
        self,
        wallet_api,
        tokens_minted,
        invalid_permit_signature,
        spender,
        web3_client
    ):
        """场景：无效的 Permit 签名"""
        permit_data = invalid_permit_signature
        sig = permit_data['signature']

        with allure.step("尝试使用无效的 Permit 签名"):
            with pytest.raises(Exception) as exc_info:
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
                web3_client.wait_for_transaction_receipt(tx_hash)

            assert "invalid" in str(exc_info.value).lower() or "revert" in str(exc_info.value).lower(), \
                "应该因为签名无效而失败"

        logger.info(f"✅ 无效 Permit 签名场景测试通过")

    def test_replay_attack_prevention_scenario(
        self,
        wallet_api,
        tokens_minted,
        permit_executed,
        spender,
        web3_client
    ):
        """场景：防止重放攻击"""
        permit_data = permit_executed
        sig = permit_data['signature']

        with allure.step("尝试重复使用相同的 Permit 签名"):
            with pytest.raises(Exception) as exc_info:
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
                web3_client.wait_for_transaction_receipt(tx_hash)

            # nonce 已经使用过，签名无效
            assert "invalid" in str(exc_info.value).lower() or "revert" in str(exc_info.value).lower(), \
                "应该因为 nonce 已使用而失败"

        logger.info(f"✅ 防止重放攻击场景测试通过")

    def test_personal_message_signing_scenario(
        self,
        wallet_api,
        user1
    ):
        """场景：个人消息签名"""
        message = "Hello, Web3 World!"

        with allure.step("签名个人消息"):
            signature_data = wallet_api.sign_personal_message(user1, message)

        with allure.step("验证签名数据"):
            assert 'signature' in signature_data, "缺少签名"
            assert 'message_hash' in signature_data, "缺少消息哈希"
            assert len(signature_data['signature']) > 0, "签名为空"

        with allure.step("恢复签名者地址"):
            recovered_address = wallet_api.recover_signer(message, signature_data['signature'])
            assert recovered_address.lower() == user1.address.lower(), \
                f"恢复的地址不匹配: {recovered_address} != {user1.address}"

        logger.info(f"✅ 个人消息签名场景测试通过")

    def test_typed_data_signing_scenario(
        self,
        wallet_api,
        user1
    ):
        """场景：结构化数据签名 (EIP-712)"""
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

        with allure.step("验证签名数据"):
            assert 'signature' in signature_data, "缺少签名"
            assert 'domain_hash' in signature_data, "缺少 domain hash"
            assert 'message_hash' in signature_data, "缺少 message hash"
            assert len(signature_data['signature']) > 0, "签名为空"

        logger.info(f"✅ 结构化数据签名场景测试通过")

    def test_signature_verification_scenario(
        self,
        wallet_api,
        personal_message_signed
    ):
        """场景：签名验证"""
        signed_data = personal_message_signed

        with allure.step("恢复签名者地址"):
            recovered_address = wallet_api.recover_signer(
                signed_data['message'],
                signed_data['signature']['signature']
            )

        with allure.step("验证签名者"):
            assert recovered_address.lower() == signed_data['signer'].lower(), \
                f"签名者不匹配: {recovered_address} != {signed_data['signer']}"

        logger.info(f"✅ 签名验证场景测试通过")

    def test_unauthorized_transfer_from_scenario(
        self,
        wallet_api,
        tokens_minted,
        user1,
        user2,
        spender,
        web3_client
    ):
        """场景：未授权的转账尝试"""
        transfer_amount = web3_client.to_wei(100, 'ether')

        with allure.step("尝试未授权的转账"):
            with pytest.raises(Exception) as exc_info:
                tx_hash = wallet_api.transfer_from(
                    user1.address,
                    user2.address,
                    transfer_amount,
                    spender
                )
                web3_client.wait_for_transaction_receipt(tx_hash)

            assert "insufficient allowance" in str(exc_info.value).lower() or "revert" in str(exc_info.value).lower(), \
                "应该因为未授权而失败"

        with allure.step("验证余额未变"):
            balance = wallet_api.balance_of(user1.address)
            assert balance == tokens_minted['mint_amount'], "余额不应该改变"

        logger.info(f"✅ 未授权转账场景测试通过")

    def test_exceed_allowance_scenario(
        self,
        wallet_api,
        approved_spender,
        user1,
        user2,
        spender,
        web3_client
    ):
        """场景：超出授权额度的转账"""
        exceed_amount = approved_spender['amount'] + web3_client.to_wei(1, 'ether')

        with allure.step("尝试超出授权额度的转账"):
            with pytest.raises(Exception) as exc_info:
                tx_hash = wallet_api.transfer_from(
                    user1.address,
                    user2.address,
                    exceed_amount,
                    spender
                )
                web3_client.wait_for_transaction_receipt(tx_hash)

            assert "insufficient allowance" in str(exc_info.value).lower() or "revert" in str(exc_info.value).lower(), \
                "应该因为超出授权额度而失败"

        with allure.step("验证授权额度未变"):
            allowance = wallet_api.allowance(user1.address, spender.address)
            assert allowance == approved_spender['amount'], "授权额度不应该改变"

        logger.info(f"✅ 超出授权额度场景测试通过")

    def test_revoke_approval_scenario(
        self,
        wallet_api,
        approved_spender,
        user1,
        spender,
        web3_client
    ):
        """场景：撤销授权"""
        with allure.step("撤销授权（设置为 0）"):
            tx_hash = wallet_api.approve(spender.address, 0, user1)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "撤销授权交易失败"

        with allure.step("验证授权已撤销"):
            allowance = wallet_api.allowance(user1.address, spender.address)
            assert allowance == 0, f"授权应该为 0: {allowance}"

        logger.info(f"✅ 撤销授权场景测试通过")

    def test_nonce_increment_scenario(
        self,
        wallet_api,
        tokens_minted,
        user1,
        spender,
        web3_client
    ):
        """场景：Nonce 递增机制"""
        with allure.step("记录初始 nonce"):
            nonce_initial = wallet_api.nonces(user1.address)

        with allure.step("执行第一次 Permit"):
            value1 = web3_client.to_wei(100, 'ether')
            deadline1 = int(time.time()) + 3600
            sig1 = wallet_api.generate_permit_signature(user1, spender.address, value1, deadline1)

            tx_hash = wallet_api.permit(
                user1.address, spender.address, value1, deadline1,
                sig1['v'], sig1['r'], sig1['s'], spender
            )
            web3_client.wait_for_transaction_receipt(tx_hash)

        with allure.step("验证 nonce 增加"):
            nonce_after_first = wallet_api.nonces(user1.address)
            assert nonce_after_first == nonce_initial + 1, "nonce 应该增加 1"

        with allure.step("执行第二次 Permit"):
            value2 = web3_client.to_wei(200, 'ether')
            deadline2 = int(time.time()) + 3600
            sig2 = wallet_api.generate_permit_signature(user1, spender.address, value2, deadline2)

            tx_hash = wallet_api.permit(
                user1.address, spender.address, value2, deadline2,
                sig2['v'], sig2['r'], sig2['s'], spender
            )
            web3_client.wait_for_transaction_receipt(tx_hash)

        with allure.step("验证 nonce 再次增加"):
            nonce_after_second = wallet_api.nonces(user1.address)
            assert nonce_after_second == nonce_initial + 2, "nonce 应该增加 2"

        logger.info(f"✅ Nonce 递增场景测试通过")

