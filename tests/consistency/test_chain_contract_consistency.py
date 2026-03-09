"""
数据一致性检测：链上原始数据与合约 view 返回的数据一致。
"""
import pytest
from web3 import Web3

from config import settings
from utils.consistency import assert_consistent, normalize_hex_address


@pytest.mark.consistency
class TestChainContractConsistency:
    """链上 get_balance / 区块 与合约 getStats、getParams 等的一致性。"""

    def test_contract_balance_matches_chain(
        self,
        w3: Web3,
        faucet_contract,
    ) -> None:
        """
        一致性：合约 getStats() 中的 contractBalance 与链上 eth_getBalance(contract) 一致。
        """
        _, contract_balance = faucet_contract.functions.getStats().call()
        contract_address = faucet_contract.address
        chain_balance = w3.eth.get_balance(contract_address)
        assert contract_balance == chain_balance, (
            f"合约 getStats().balance({contract_balance}) 与链上余额({chain_balance}) 不一致"
        )

    def test_owner_address_format(self, faucet_contract) -> None:
        """一致性：owner 为 0x 格式、42 字符。"""
        owner = faucet_contract.functions.owner().call()
        assert owner is not None
        assert isinstance(owner, str) and owner.startswith("0x") and len(owner) == 42

    def test_get_params_types_and_non_negative(self, faucet_contract) -> None:
        """一致性：getParams() 返回四元组且均为非负整数。"""
        a, b, c, d = faucet_contract.functions.getParams().call()
        assert all(isinstance(x, int) and x >= 0 for x in (a, b, c, d))

    def test_get_stats_types_and_non_negative(self, faucet_contract) -> None:
        """一致性：getStats() 返回 (totalClaimed, contractBalance) 非负。"""
        total_claimed, contract_balance = faucet_contract.functions.getStats().call()
        assert isinstance(total_claimed, int) and total_claimed >= 0
        assert isinstance(contract_balance, int) and contract_balance >= 0


@pytest.mark.consistency
class TestConsistencyHelpers:
    """一致性工具函数：normalize_hex_address、assert_consistent 在链上数据上的用法。"""

    def test_normalize_hex_address_for_tx(self) -> None:
        """链上 tx 的 from/to 规范化后可与 API 返回对比。"""
        tx_like = {"from": "0xAbc123", "to": "0xDef456", "value": 1}
        out = normalize_hex_address(tx_like)
        assert out["from"] == "0xabc123"
        assert out["to"] == "0xdef456"
        assert out["value"] == 1

    def test_assert_consistent_balance_view(self) -> None:
        """链上余额与「视图」一致时 assert_consistent 不抛。"""
        from_chain = normalize_hex_address({"balance": 1000, "address": "0xabc"})
        from_view = normalize_hex_address({"balance": 1000, "address": "0xABC"})
        assert_consistent(from_chain, from_view, msg="余额视图一致")

    def test_assert_consistent_fails_on_mismatch(self) -> None:
        """余额不一致时应抛出 AssertionError。"""
        from_chain = {"balance": 1000}
        from_view = {"balance": 1001}
        with pytest.raises(AssertionError) as exc_info:
            assert_consistent(from_chain, from_view, msg="余额不一致")
        err_msg = str(exc_info.value)
        assert "inconsistency" in err_msg.lower() or "1000" in err_msg or "1001" in err_msg
