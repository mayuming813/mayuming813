#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : assert_helper.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from web3 import Web3


class AssertHelper:
    """断言辅助类"""

    @staticmethod
    def assert_transaction_success(receipt):
        """断言交易成功"""
        assert receipt['status'] == 1, f"交易失败: {receipt}"

    @staticmethod
    def assert_event_emitted(receipt, event_name: str):
        """断言事件被触发"""
        events = [log['event'] for log in receipt['logs'] if 'event' in log]
        assert event_name in events, f"事件 {event_name} 未被触发"

    @staticmethod
    def assert_balance_changed(w3: Web3, address: str, expected_change: int, before_balance: int):
        """断言余额变化"""
        after_balance = w3.eth.get_balance(address)
        actual_change = after_balance - before_balance
        assert actual_change == expected_change, \
            f"余额变化不符合预期: 预期 {expected_change}, 实际 {actual_change}"

    @staticmethod
    def assert_contract_state(contract, function_name: str, expected_value, *args):
        """断言合约状态"""
        function = getattr(contract.functions, function_name)
        actual_value = function(*args).call()
        assert actual_value == expected_value, \
            f"合约状态不符合预期: 预期 {expected_value}, 实际 {actual_value}"