"""
链上接口测试客户端：封装 RPC 调用与常用链上查询。
"""
from typing import Any, Dict, Optional

from web3 import Web3

from config import settings
from utils.web3_client import get_w3


class ChainApiClient:
    """链 RPC 与基础查询封装，用于接口测试与数据校验。"""

    def __init__(self, w3: Optional[Web3] = None):
        self._w3 = w3 or get_w3()

    @property
    def chain_id(self) -> int:
        return self._w3.eth.chain_id

    @property
    def block_number(self) -> int:
        return self._w3.eth.block_number

    def get_balance(self, address: str) -> int:
        """wei 余额。"""
        return self._w3.eth.get_balance(Web3.to_checksum_address(address))

    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """获取交易详情。"""
        tx = self._w3.eth.get_transaction(tx_hash)
        if tx is None:
            return None
        return dict(tx)

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """获取交易回执。"""
        receipt = self._w3.eth.get_transaction_receipt(tx_hash)
        if receipt is None:
            return None
        return dict(receipt)

    def get_block(self, block_identifier: str | int, full_tx: bool = False) -> Dict[str, Any]:
        """获取区块。"""
        block = self._w3.eth.get_block(block_identifier, full_transactions=full_tx)
        return dict(block) if block else {}

    def is_connected(self) -> bool:
        return self._w3.is_connected()
