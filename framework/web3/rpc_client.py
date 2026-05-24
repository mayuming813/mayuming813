#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : rpc_client.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : JSON-RPC 调用封装
"""

import requests
from typing import Optional, Dict, Any, List
from framework.core.logger import logger


class RPCClient:
    """JSON-RPC 调用封装"""

    def __init__(self, rpc_url: str, timeout: int = 30):
        """
        初始化 RPC 客户端

        Args:
            rpc_url: RPC 节点地址
            timeout: 请求超时时间
        """
        self.rpc_url = rpc_url
        self.timeout = timeout
        self.session = requests.Session()
        self.request_id = 0
        logger.info(f"RPC 客户端已初始化: {rpc_url}")

    def call(self, method: str, params: Optional[List] = None) -> Dict[str, Any]:
        """
        发送 JSON-RPC 请求

        Args:
            method: RPC 方法名
            params: 方法参数

        Returns:
            RPC 响应
        """
        self.request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": self.request_id
        }

        try:
            response = self.session.post(
                self.rpc_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                logger.error(f"RPC 错误: {result['error']}")
                return result

            logger.debug(f"RPC 调用成功: {method}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"RPC 请求失败: {e}")
            return {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }

    def batch_call(self, calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量 RPC 调用

        Args:
            calls: 调用列表，每个元素包含 method 和 params

        Returns:
            响应列表
        """
        payloads = []
        for call in calls:
            self.request_id += 1
            payloads.append({
                "jsonrpc": "2.0",
                "method": call["method"],
                "params": call.get("params", []),
                "id": self.request_id
            })

        try:
            response = self.session.post(
                self.rpc_url,
                json=payloads,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            results = response.json()
            logger.debug(f"批量 RPC 调用成功: {len(calls)} 个请求")
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"批量 RPC 请求失败: {e}")
            return []

    # ========== 区块链相关方法 ==========

    def eth_block_number(self) -> Dict:
        """获取最新区块号"""
        return self.call("eth_blockNumber")

    def eth_get_block_by_number(self, block_number: str, full_tx: bool = False) -> Dict:
        """获取区块信息"""
        return self.call("eth_getBlockByNumber", [block_number, full_tx])

    def eth_get_block_by_hash(self, block_hash: str, full_tx: bool = False) -> Dict:
        """通过哈希获取区块"""
        return self.call("eth_getBlockByHash", [block_hash, full_tx])

    def eth_get_transaction_by_hash(self, tx_hash: str) -> Dict:
        """获取交易信息"""
        return self.call("eth_getTransactionByHash", [tx_hash])

    def eth_get_transaction_receipt(self, tx_hash: str) -> Dict:
        """获取交易回执"""
        return self.call("eth_getTransactionReceipt", [tx_hash])

    def eth_get_balance(self, address: str, block: str = "latest") -> Dict:
        """获取账户余额"""
        return self.call("eth_getBalance", [address, block])

    def eth_get_transaction_count(self, address: str, block: str = "latest") -> Dict:
        """获取账户交易数量（nonce）"""
        return self.call("eth_getTransactionCount", [address, block])

    def eth_get_code(self, address: str, block: str = "latest") -> Dict:
        """获取合约代码"""
        return self.call("eth_getCode", [address, block])

    def eth_call(self, transaction: Dict, block: str = "latest") -> Dict:
        """执行只读调用"""
        return self.call("eth_call", [transaction, block])

    def eth_estimate_gas(self, transaction: Dict) -> Dict:
        """估算 Gas"""
        return self.call("eth_estimateGas", [transaction])

    def eth_gas_price(self) -> Dict:
        """获取 Gas 价格"""
        return self.call("eth_gasPrice")

    def eth_send_raw_transaction(self, signed_tx: str) -> Dict:
        """发送原始交易"""
        return self.call("eth_sendRawTransaction", [signed_tx])

    def eth_get_logs(self, filter_params: Dict) -> Dict:
        """获取日志"""
        return self.call("eth_getLogs", [filter_params])

    def eth_new_filter(self, filter_params: Dict) -> Dict:
        """创建过滤器"""
        return self.call("eth_newFilter", [filter_params])

    def eth_get_filter_changes(self, filter_id: str) -> Dict:
        """获取过滤器变化"""
        return self.call("eth_getFilterChanges", [filter_id])

    def eth_uninstall_filter(self, filter_id: str) -> Dict:
        """卸载过滤器"""
        return self.call("eth_uninstallFilter", [filter_id])

    # ========== 网络相关方法 ==========

    def net_version(self) -> Dict:
        """获取网络 ID"""
        return self.call("net_version")

    def net_listening(self) -> Dict:
        """检查节点是否在监听"""
        return self.call("net_listening")

    def net_peer_count(self) -> Dict:
        """获取对等节点数量"""
        return self.call("net_peerCount")

    def web3_client_version(self) -> Dict:
        """获取客户端版本"""
        return self.call("web3_clientVersion")

    def web3_sha3(self, data: str) -> Dict:
        """计算 Keccak-256 哈希"""
        return self.call("web3_sha3", [data])

    # ========== 调试相关方法 ==========

    def debug_trace_transaction(self, tx_hash: str, options: Optional[Dict] = None) -> Dict:
        """追踪交易执行"""
        return self.call("debug_traceTransaction", [tx_hash, options or {}])

    def debug_trace_call(self, transaction: Dict, block: str = "latest", options: Optional[Dict] = None) -> Dict:
        """追踪调用执行"""
        return self.call("debug_traceCall", [transaction, block, options or {}])

    # ========== Hardhat 特定方法 ==========

    def hardhat_impersonate_account(self, address: str) -> Dict:
        """模拟账户（Hardhat）"""
        return self.call("hardhat_impersonateAccount", [address])

    def hardhat_stop_impersonating_account(self, address: str) -> Dict:
        """停止模拟账户（Hardhat）"""
        return self.call("hardhat_stopImpersonatingAccount", [address])

    def hardhat_set_balance(self, address: str, balance: str) -> Dict:
        """设置账户余额（Hardhat）"""
        return self.call("hardhat_setBalance", [address, balance])

    def hardhat_mine(self, blocks: int = 1) -> Dict:
        """挖矿（Hardhat）"""
        return self.call("hardhat_mine", [hex(blocks)])

    def hardhat_reset(self, forking: Optional[Dict] = None) -> Dict:
        """重置网络（Hardhat）"""
        return self.call("hardhat_reset", [forking] if forking else [])

    def evm_snapshot(self) -> Dict:
        """创建快照"""
        return self.call("evm_snapshot")

    def evm_revert(self, snapshot_id: str) -> Dict:
        """恢复快照"""
        return self.call("evm_revert", [snapshot_id])

    def evm_increase_time(self, seconds: int) -> Dict:
        """增加时间"""
        return self.call("evm_increaseTime", [seconds])

    def evm_set_next_block_timestamp(self, timestamp: int) -> Dict:
        """设置下一个区块时间戳"""
        return self.call("evm_setNextBlockTimestamp", [timestamp])

    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info("RPC 客户端已关闭")
