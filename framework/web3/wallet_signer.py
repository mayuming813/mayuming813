#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : wallet_signer.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 钱包签名封装
"""

from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data
from typing import Dict, Any, Optional
from web3 import Web3
from framework.core.logger import logger


class WalletSigner:
    """钱包签名封装"""

    def __init__(self, private_key: Optional[str] = None):
        """
        初始化钱包签名器

        Args:
            private_key: 私钥（可选，如果不提供则创建新账户）
        """
        if private_key:
            self.account = Account.from_key(private_key)
        else:
            self.account = Account.create()

        logger.info(f"钱包签名器已初始化: {self.account.address}")

    @property
    def address(self) -> str:
        """获取地址"""
        return self.account.address

    @property
    def private_key(self) -> str:
        """获取私钥"""
        return self.account.key.hex()

    def sign_message(self, message: str) -> Dict[str, Any]:
        """
        签名消息（Personal Sign）

        Args:
            message: 消息内容

        Returns:
            签名结果
        """
        message_hash = encode_defunct(text=message)
        signed_message = self.account.sign_message(message_hash)

        return {
            'message': message,
            'messageHash': signed_message.messageHash.hex(),
            'signature': signed_message.signature.hex(),
            'r': hex(signed_message.r),
            's': hex(signed_message.s),
            'v': signed_message.v
        }

    def sign_typed_data(self, typed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        签名结构化数据（EIP-712）

        Args:
            typed_data: EIP-712 结构化数据

        Returns:
            签名结果
        """
        signable_message = encode_typed_data(typed_data)
        signed_message = self.account.sign_message(signable_message)

        return {
            'typedData': typed_data,
            'messageHash': signed_message.messageHash.hex(),
            'signature': signed_message.signature.hex(),
            'r': hex(signed_message.r),
            's': hex(signed_message.s),
            'v': signed_message.v
        }

    def sign_transaction(self, transaction: Dict[str, Any]) -> str:
        """
        签名交易

        Args:
            transaction: 交易对象

        Returns:
            签名后的原始交易
        """
        signed_tx = self.account.sign_transaction(transaction)
        return signed_tx.raw_transaction.hex()

    @staticmethod
    def recover_message(message: str, signature: str) -> str:
        """
        从签名恢复地址

        Args:
            message: 原始消息
            signature: 签名

        Returns:
            恢复的地址
        """
        message_hash = encode_defunct(text=message)
        recovered_address = Account.recover_message(message_hash, signature=signature)
        return recovered_address

    @staticmethod
    def recover_typed_data(typed_data: Dict[str, Any], signature: str) -> str:
        """
        从 EIP-712 签名恢复地址

        Args:
            typed_data: EIP-712 结构化数据
            signature: 签名

        Returns:
            恢复的地址
        """
        signable_message = encode_typed_data(typed_data)
        recovered_address = Account.recover_message(signable_message, signature=signature)
        return recovered_address

    @staticmethod
    def verify_signature(message: str, signature: str, expected_address: str) -> bool:
        """
        验证签名

        Args:
            message: 原始消息
            signature: 签名
            expected_address: 期望的地址

        Returns:
            是否验证通过
        """
        try:
            recovered_address = WalletSigner.recover_message(message, signature)
            return Web3.to_checksum_address(recovered_address) == Web3.to_checksum_address(expected_address)
        except Exception as e:
            logger.error(f"签名验证失败: {e}")
            return False

    @staticmethod
    def verify_typed_data_signature(
        typed_data: Dict[str, Any],
        signature: str,
        expected_address: str
    ) -> bool:
        """
        验证 EIP-712 签名

        Args:
            typed_data: EIP-712 结构化数据
            signature: 签名
            expected_address: 期望的地址

        Returns:
            是否验证通过
        """
        try:
            recovered_address = WalletSigner.recover_typed_data(typed_data, signature)
            return Web3.to_checksum_address(recovered_address) == Web3.to_checksum_address(expected_address)
        except Exception as e:
            logger.error(f"EIP-712 签名验证失败: {e}")
            return False

    def create_eip712_permit(
        self,
        token_name: str,
        token_address: str,
        owner: str,
        spender: str,
        value: int,
        nonce: int,
        deadline: int,
        chain_id: int = 1
    ) -> Dict[str, Any]:
        """
        创建 EIP-2612 Permit 签名

        Args:
            token_name: 代币名称
            token_address: 代币地址
            owner: 所有者地址
            spender: 授权地址
            value: 授权金额
            nonce: Nonce
            deadline: 截止时间
            chain_id: 链 ID

        Returns:
            签名结果
        """
        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"}
                ],
                "Permit": [
                    {"name": "owner", "type": "address"},
                    {"name": "spender", "type": "address"},
                    {"name": "value", "type": "uint256"},
                    {"name": "nonce", "type": "uint256"},
                    {"name": "deadline", "type": "uint256"}
                ]
            },
            "primaryType": "Permit",
            "domain": {
                "name": token_name,
                "version": "1",
                "chainId": chain_id,
                "verifyingContract": token_address
            },
            "message": {
                "owner": owner,
                "spender": spender,
                "value": value,
                "nonce": nonce,
                "deadline": deadline
            }
        }

        return self.sign_typed_data(typed_data)

    @staticmethod
    def create_random_wallet() -> 'WalletSigner':
        """
        创建随机钱包

        Returns:
            新的钱包签名器
        """
        return WalletSigner()

    @staticmethod
    def from_mnemonic(mnemonic: str, account_path: str = "m/44'/60'/0'/0/0") -> 'WalletSigner':
        """
        从助记词创建钱包

        Args:
            mnemonic: 助记词
            account_path: 派生路径

        Returns:
            钱包签名器
        """
        account = Account.from_mnemonic(mnemonic, account_path=account_path)
        return WalletSigner(account.key.hex())

    def export_keystore(self, password: str) -> Dict[str, Any]:
        """
        导出 Keystore

        Args:
            password: 密码

        Returns:
            Keystore JSON
        """
        return self.account.encrypt(password)

    @staticmethod
    def from_keystore(keystore: Dict[str, Any], password: str) -> 'WalletSigner':
        """
        从 Keystore 导入

        Args:
            keystore: Keystore JSON
            password: 密码

        Returns:
            钱包签名器
        """
        private_key = Account.decrypt(keystore, password)
        return WalletSigner(private_key.hex())
