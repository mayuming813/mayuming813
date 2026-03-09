"""
JSON-RPC 接口自动化：直接对节点发起 eth_* / net_* / web3_* 请求并断言响应。
"""
import pytest

from config import settings
from utils.json_rpc import (
    eth_block_number,
    eth_chain_id,
    eth_get_balance,
    eth_get_block_by_number,
    eth_gas_price,
    net_version,
    rpc_call,
    web3_client_version,
)


@pytest.mark.api
class TestJsonRpc:
    """Raw JSON-RPC 接口：请求/响应格式与返回值断言。"""

    def test_eth_block_number(self) -> None:
        """eth_blockNumber：返回当前区块号，非负整数。"""
        nb = eth_block_number()
        assert isinstance(nb, int), "应为 int"
        assert nb >= 0, "区块号应非负"

    def test_eth_chain_id(self) -> None:
        """eth_chainId：与配置 CHAIN_ID 一致。"""
        got = eth_chain_id()
        assert got == settings.chain_id
        assert isinstance(got, int) and got > 0

    def test_net_version(self) -> None:
        """net_version：返回链 ID 字符串，与配置一致。"""
        ver = net_version()
        assert isinstance(ver, str)
        assert ver == str(settings.chain_id)

    def test_web3_client_version(self) -> None:
        """web3_clientVersion：返回非空字符串。"""
        v = web3_client_version()
        assert isinstance(v, str)
        assert len(v) > 0

    def test_eth_gas_price(self) -> None:
        """eth_gasPrice：返回 wei，非负整数。"""
        gas = eth_gas_price()
        assert isinstance(gas, int)
        assert gas >= 0

    def test_eth_get_balance(self, tester_address: str) -> None:
        """eth_getBalance(address, 'latest')：返回 wei，非负。"""
        balance = eth_get_balance(tester_address)
        assert isinstance(balance, int)
        assert balance >= 0
        assert tester_address.startswith("0x") and len(tester_address) == 42

    def test_eth_get_block_by_number_latest(self) -> None:
        """eth_getBlockByNumber('latest', false)：返回区块对象，含 number/hash。"""
        block = eth_get_block_by_number("latest", full_tx=False)
        assert block is not None
        assert "number" in block or "hash" in block
        if "number" in block:
            # 可能为 hex 或 int，依节点而定
            num = block["number"]
            if isinstance(num, str):
                assert num.startswith("0x")
            else:
                assert isinstance(num, int) and num >= 0

    def test_eth_get_block_by_number_hex(self) -> None:
        """eth_getBlockByNumber(0, false)：创世块或指定块。"""
        block = eth_get_block_by_number(0, full_tx=False)
        assert block is not None
        assert "hash" in block

    def test_rpc_call_error_handling(self) -> None:
        """错误方法名或参数应得到 error 响应并被转为异常。"""
        with pytest.raises(RuntimeError) as exc_info:
            rpc_call("eth_notExist")
        assert "error" in str(exc_info.value).lower() or "JSON-RPC" in str(exc_info.value)


@pytest.mark.api
class TestJsonRpcConsistencyWithWeb3:
    """JSON-RPC 与 Web3 结果一致性：同一链上同一查询应一致。"""

    def test_block_number_matches_web3(self, chain_api) -> None:
        """eth_blockNumber 与 Web3 block_number 一致。"""
        from utils import ChainApiClient

        api: ChainApiClient = chain_api
        rpc_block = eth_block_number()
        w3_block = api.block_number
        assert rpc_block == w3_block

    def test_chain_id_matches_web3(self, chain_api) -> None:
        """eth_chainId 与 Web3 chain_id 一致。"""
        from utils import ChainApiClient

        api: ChainApiClient = chain_api
        assert eth_chain_id() == api.chain_id

    def test_balance_matches_web3(self, chain_api, tester_address: str) -> None:
        """eth_getBalance 与 Web3 get_balance 一致。"""
        from utils import ChainApiClient

        api: ChainApiClient = chain_api
        rpc_bal = eth_get_balance(tester_address)
        w3_bal = api.get_balance(tester_address)
        assert rpc_bal == w3_bal
