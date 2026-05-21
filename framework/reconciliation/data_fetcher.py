#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : data_fetcher.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from web3 import Web3
from framework.core.web3_manager import Web3Manager
from framework.utils.http_client import HTTPClient
from framework.utils.polling_helper import PollingHelper


class DataFetcher(ABC):
    """数据获取器基类"""

    @abstractmethod
    def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """
        获取数据
        :param kwargs: 查询参数
        :return: 数据列表
        """
        pass


class OnchainDataFetcher(DataFetcher):
    """链上数据获取器"""

    def __init__(self, web3_manager: Web3Manager = None):
        """
        初始化
        :param web3_manager: Web3Manager 实例
        """
        self.web3_manager = web3_manager or Web3Manager()
        self.w3 = self.web3_manager.w3

    def fetch_transactions(
        self,
        address: str,
        start_block: int = None,
        end_block: int = None
    ) -> List[Dict[str, Any]]:
        """
        获取地址的交易记录
        :param address: 地址
        :param start_block: 起始区块
        :param end_block: 结束区块
        :return: 交易列表
        """
        address = Web3.to_checksum_address(address)
        transactions = []

        if start_block is None:
            start_block = 0
        if end_block is None:
            end_block = self.w3.eth.block_number

        # 注意：这里简化了实现，实际应该使用事件日志或索引服务
        # 遍历区块查找交易（仅示例，生产环境不推荐）
        for block_num in range(start_block, min(end_block + 1, start_block + 100)):
            try:
                block = self.w3.eth.get_block(block_num, full_transactions=True)
                for tx in block.transactions:
                    if tx['from'] == address or tx['to'] == address:
                        transactions.append({
                            'tx_hash': tx['hash'].hex(),
                            'from': tx['from'],
                            'to': tx['to'],
                            'value': tx['value'],
                            'block_number': tx['blockNumber'],
                            'timestamp': block['timestamp']
                        })
            except Exception as e:
                continue

        return transactions

    def fetch_token_transfers(
        self,
        contract_address: str,
        address: str = None,
        start_block: int = None,
        end_block: int = None
    ) -> List[Dict[str, Any]]:
        """
        获取代币转账记录（通过事件日志）
        :param contract_address: 合约地址
        :param address: 过滤地址（可选）
        :param start_block: 起始区块
        :param end_block: 结束区块
        :return: 转账记录列表
        """
        contract_address = Web3.to_checksum_address(contract_address)
        transfers = []

        if start_block is None:
            start_block = 0
        if end_block is None:
            end_block = self.w3.eth.block_number

        # Transfer 事件签名
        transfer_event_signature = Web3.keccak(text="Transfer(address,address,uint256)").hex()

        # 构建过滤器
        filter_params = {
            'fromBlock': start_block,
            'toBlock': end_block,
            'address': contract_address,
            'topics': [transfer_event_signature]
        }

        # 如果指定了地址，添加到 topics
        if address:
            address = Web3.to_checksum_address(address)
            # 可以过滤 from 或 to
            # 这里简化处理

        try:
            logs = self.w3.eth.get_logs(filter_params)

            for log in logs:
                # 解析事件数据
                from_address = '0x' + log['topics'][1].hex()[-40:]
                to_address = '0x' + log['topics'][2].hex()[-40:]
                value = int(log['data'].hex(), 16)

                transfers.append({
                    'tx_hash': log['transactionHash'].hex(),
                    'from': Web3.to_checksum_address(from_address),
                    'to': Web3.to_checksum_address(to_address),
                    'value': value,
                    'block_number': log['blockNumber'],
                    'log_index': log['logIndex']
                })
        except Exception as e:
            pass

        return transfers

    def fetch_balance(self, address: str) -> Dict[str, Any]:
        """
        获取地址余额
        :param address: 地址
        :return: 余额信息
        """
        address = Web3.to_checksum_address(address)
        balance = self.w3.eth.get_balance(address)

        return {
            'address': address,
            'balance': balance,
            'balance_eth': self.w3.from_wei(balance, 'ether'),
            'timestamp': self.w3.eth.get_block('latest')['timestamp']
        }

    def fetch_token_balance(self, contract_address: str, address: str) -> Dict[str, Any]:
        """
        获取代币余额
        :param contract_address: 合约地址
        :param address: 地址
        :return: 余额信息
        """
        contract = self.web3_manager.get_contract(contract_address)
        address = Web3.to_checksum_address(address)

        balance = contract.functions.balanceOf(address).call()
        decimals = contract.functions.decimals().call()

        return {
            'address': address,
            'contract_address': contract_address,
            'balance': balance,
            'balance_formatted': balance / (10 ** decimals),
            'decimals': decimals
        }

    def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """
        通用获取方法
        :param kwargs: 查询参数
        :return: 数据列表
        """
        fetch_type = kwargs.get('type', 'transactions')

        if fetch_type == 'transactions':
            return self.fetch_transactions(
                address=kwargs.get('address'),
                start_block=kwargs.get('start_block'),
                end_block=kwargs.get('end_block')
            )
        elif fetch_type == 'token_transfers':
            return self.fetch_token_transfers(
                contract_address=kwargs.get('contract_address'),
                address=kwargs.get('address'),
                start_block=kwargs.get('start_block'),
                end_block=kwargs.get('end_block')
            )
        else:
            return []


class OffchainDataFetcher(DataFetcher):
    """链下数据获取器（API）"""

    def __init__(self, http_client: HTTPClient = None, base_url: str = None):
        """
        初始化
        :param http_client: HTTP 客户端
        :param base_url: API 基础 URL
        """
        self.client = http_client or HTTPClient(base_url=base_url)

    def fetch_user_transactions(
        self,
        user_id: str = None,
        address: str = None,
        start_time: int = None,
        end_time: int = None,
        page: int = 1,
        size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取用户交易记录
        :param user_id: 用户ID
        :param address: 地址
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param page: 页码
        :param size: 每页数量
        :return: 交易列表
        """
        params = {
            'user_id': user_id,
            'address': address,
            'start_time': start_time,
            'end_time': end_time,
            'page': page,
            'size': size
        }

        # 移除 None 值
        params = {k: v for k, v in params.items() if v is not None}

        response = self.client.get('/api/transactions', params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('transactions', [])
        else:
            return []

    def fetch_user_balance(self, user_id: str = None, address: str = None) -> Dict[str, Any]:
        """
        获取用户余额
        :param user_id: 用户ID
        :param address: 地址
        :return: 余额信息
        """
        params = {'user_id': user_id, 'address': address}
        params = {k: v for k, v in params.items() if v is not None}

        response = self.client.get('/api/user/balance', params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get('data', {})
        else:
            return {}

    def fetch_all_pages(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        page_param: str = 'page',
        size_param: str = 'size',
        max_pages: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取所有分页数据
        :param endpoint: API 端点
        :param params: 查询参数
        :param page_param: 分页参数名
        :param size_param: 每页数量参数名
        :param max_pages: 最大页数
        :return: 所有数据
        """
        all_data = []
        params = params or {}
        page = 1

        while page <= max_pages:
            params[page_param] = page
            response = self.client.get(endpoint, params=params)

            if response.status_code != 200:
                break

            data = response.json()
            items = data.get('data', {}).get('items', [])

            if not items:
                break

            all_data.extend(items)

            # 检查是否还有下一页
            has_more = data.get('data', {}).get('has_more', False)
            if not has_more:
                break

            page += 1

        return all_data

    def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        """
        通用获取方法
        :param kwargs: 查询参数
        :return: 数据列表
        """
        fetch_type = kwargs.get('type', 'transactions')

        if fetch_type == 'transactions':
            return self.fetch_user_transactions(
                user_id=kwargs.get('user_id'),
                address=kwargs.get('address'),
                start_time=kwargs.get('start_time'),
                end_time=kwargs.get('end_time')
            )
        else:
            return []


class AsyncDataFetcher:
    """异步数据获取器（处理链上异步数据）"""

    def __init__(self, fetcher: DataFetcher, polling_helper: PollingHelper = None):
        """
        初始化
        :param fetcher: 数据获取器
        :param polling_helper: 轮询辅助工具
        """
        self.fetcher = fetcher
        self.polling_helper = polling_helper or PollingHelper()

    def fetch_with_polling(
        self,
        condition: callable,
        timeout: float = 60.0,
        interval: float = 3.0,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        轮询获取数据直到满足条件
        :param condition: 条件函数
        :param timeout: 超时时间
        :param interval: 轮询间隔
        :param kwargs: 获取参数
        :return: 数据列表
        """
        def fetch_func():
            return self.fetcher.fetch(**kwargs)

        return self.polling_helper.poll_until_success(
            fetch_func,
            condition,
            timeout,
            interval
        )

    def fetch_until_count(
        self,
        expected_count: int,
        timeout: float = 60.0,
        interval: float = 3.0,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        轮询直到数据数量达到预期
        :param expected_count: 期望数量
        :param timeout: 超时时间
        :param interval: 轮询间隔
        :param kwargs: 获取参数
        :return: 数据列表
        """
        def condition(data):
            return len(data) >= expected_count

        return self.fetch_with_polling(condition, timeout, interval, **kwargs)
