#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : transaction_helper.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from web3 import Web3
from eth_account.signers.local import LocalAccount
from framework.core.logger import logger


class TransactionHelper:
    """交易辅助类"""

    @staticmethod
    def send_transaction(w3: Web3, account: LocalAccount, tx_params: dict) -> str:
        """发送交易并等待确认"""
        # 设置默认参数
        if 'from' not in tx_params:
            tx_params['from'] = account.address
        if 'nonce' not in tx_params:
            tx_params['nonce'] = w3.eth.get_transaction_count(account.address)
        if 'gas' not in tx_params:
            tx_params['gas'] = 3000000
        if 'gasPrice' not in tx_params:
            tx_params['gasPrice'] = w3.eth.gas_price

        # 签名交易
        signed_tx = account.sign_transaction(tx_params)

        # 发送交易
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        logger.info(f"交易已发送: {tx_hash.hex()}")

        # 等待确认
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info(f"交易已确认: {receipt['transactionHash'].hex()}, 状态: {receipt['status']}")

        return receipt

    @staticmethod
    def call_contract_function(contract, function_name: str, account: LocalAccount, *args, **kwargs):
        """调用合约函数"""
        w3 = contract.w3
        function = getattr(contract.functions, function_name)

        # 构建交易
        tx_params = function(*args).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': kwargs.get('gas', 3000000),
            'gasPrice': w3.eth.gas_price
        })

        return TransactionHelper.send_transaction(w3, account, tx_params)

    @staticmethod
    def get_event_logs(w3: Web3, contract, event_name: str, from_block: int = 0, to_block: str = 'latest'):
        """获取事件日志"""
        event = getattr(contract.events, event_name)
        logs = event.get_logs(fromBlock=from_block, toBlock=to_block)
        logger.info(f"获取到 {len(logs)} 条 {event_name} 事件")
        return logs
