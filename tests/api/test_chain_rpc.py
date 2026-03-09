"""
链上 RPC 接口测试：基础查询与区块/交易接口。
"""
import pytest
from web3 import Web3

from utils import get_w3, get_account, ChainApiClient


@pytest.mark.api
class TestChainRpc:
    """链 RPC 基础接口。"""

    def test_rpc_connected(self, chain_api: ChainApiClient) -> None:
        """断言：RPC 连接成功。"""
        assert chain_api.is_connected() is True

    def test_chain_id(self, chain_api: ChainApiClient, chain_id: int) -> None:
        """断言：链 ID 与配置一致。"""
        assert chain_api.chain_id == chain_id
        assert isinstance(chain_api.chain_id, int)
        assert chain_api.chain_id > 0

    def test_block_number(self, chain_api: ChainApiClient) -> None:
        """断言：区块号为非负整数。"""
        nb = chain_api.block_number
        assert isinstance(nb, int), "block_number 应为 int"
        assert nb >= 0, "block_number 应非负"

    def test_get_block_latest(self, chain_api: ChainApiClient) -> None:
        """断言：最新区块包含 number、hash 等字段。"""
        block = chain_api.get_block("latest")
        assert block is not None
        assert "number" in block and "hash" in block
        assert isinstance(block["number"], int)
        assert block["number"] >= 0
        assert block["hash"] is not None, "区块应有 hash"

    def test_get_balance(self, chain_api: ChainApiClient, tester_address: str) -> None:
        """断言：余额为非负整数（wei）。"""
        balance = chain_api.get_balance(tester_address)
        assert isinstance(balance, int), "余额应为 int"
        assert balance >= 0, "余额应非负"
        assert tester_address is not None and len(tester_address) == 42
