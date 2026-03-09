"""
SepoliaClaimFaucet 智能合约单元测试。

执行顺序固定为 01～15，按建议流程：部署状态 → setParams → 充值 → view → claim → withdraw → revert。
直接执行：pytest tests/unit/test_sepolia_claim_faucet.py -v
"""
import pytest
from eth_account import Account
from web3 import Web3
from web3.contract import Contract


def _transact(
    w3: Web3,
    contract: Contract,
    fn_name: str,
    args: tuple,
    account: Account,
    value_wei: int = 0,
):
    """构建、签名并发送合约写交易，等待回执。"""
    fn = getattr(contract.functions, fn_name)(*args)
    tx = fn.build_transaction({
        "from": account.address,
        "chainId": w3.eth.chain_id,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 500_000,
    })
    if value_wei:
        tx["value"] = value_wei
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)


@pytest.mark.unit
class TestSepoliaClaimFaucet:
    """
    单类按顺序执行：01 部署与状态 → 02～04 初始/params → 05～06 setParams
    → 07～08 充值 → 09～11 view → 12～13 claim → 14 withdraw → 15 revert。
    脚本可重复执行（同一合约、同一账户）。
    """

    # --- 一、部署与初始状态 (01-04) ---
    def test_01_contract_is_deployed_and_connected(self, w3: Web3, faucet_contract: Contract) -> None:
        """步骤：加载合约并调用 owner()。断言：owner 为有效 0x 地址且非零。"""
        owner = faucet_contract.functions.owner().call()
        assert owner is not None and len(owner) == 42 and owner.startswith("0x")
        assert owner != "0x0000000000000000000000000000000000000000", "owner 不应为零地址"

    def test_02_owner_matches_deployer(self, w3: Web3, faucet_contract: Contract, tester_address: str) -> None:
        """步骤：对比 owner 与 TEST_PRIVATE_KEY 对应地址。断言：一致则与本地钱包联动。"""
        owner = faucet_contract.functions.owner().call()
        assert owner.lower() == tester_address.lower()

    def test_03_initial_params_and_stats(self, faucet_contract: Contract) -> None:
        """步骤：getParams()、getStats()。断言：totalClaimed==0，contractBalance>=0。"""
        _, _, _, _ = faucet_contract.functions.getParams().call()
        total_claimed, contract_balance = faucet_contract.functions.getStats().call()
        assert total_claimed == 0 and contract_balance >= 0

    def test_04_getParams_returns_four_values(self, faucet_contract: Contract) -> None:
        """步骤：getParams()。断言：返回 4 个非负 int（claim_amount, total_cap, per_user_cap, cooldown）。"""
        result = faucet_contract.functions.getParams().call()
        assert len(result) == 4 and all(isinstance(x, int) for x in result)
        claim_amount, total_cap, per_user_cap, cooldown = result
        assert claim_amount >= 0 and total_cap >= 0 and per_user_cap >= 0 and cooldown >= 0

    # --- 二、setParams (05-06) ---
    def test_05_setParams_owner_succeeds(
        self, w3: Web3, faucet_contract: Contract, tester_account: Account
    ) -> None:
        """步骤：owner 调用 setParams。断言：成功且 getParams() 与传入一致。"""
        claim_amount = 1_000_000_000_000_000
        total_cap = 100_000_000_000_000_000
        per_user_cap = 10_000_000_000_000_000
        cooldown = 60
        receipt = _transact(
            w3, faucet_contract, "setParams",
            (claim_amount, total_cap, per_user_cap, cooldown),
            tester_account,
        )
        assert receipt["status"] == 1, "setParams 交易应成功"
        assert receipt.get("blockNumber") is not None and receipt.get("transactionHash") is not None
        a, b, c, d = faucet_contract.functions.getParams().call()
        assert (a, b, c, d) == (claim_amount, total_cap, per_user_cap, cooldown)

    def test_06_setParams_owner_can_repeat(
        self, w3: Web3, faucet_contract: Contract, tester_account: Account
    ) -> None:
        """步骤：owner 再次 setParams 相同值。断言：可重复调用。"""
        claim_amount, total_cap, per_user_cap, cooldown = faucet_contract.functions.getParams().call()
        _transact(w3, faucet_contract, "setParams", (claim_amount, total_cap, per_user_cap, cooldown), tester_account)
        assert faucet_contract.functions.getParams().call()[0] == claim_amount

    # --- 三、合约接收 ETH (07-08) ---
    def test_07_contract_balance_increases_after_send(
        self, w3: Web3, faucet_contract: Contract, tester_account: Account
    ) -> None:
        """步骤：向合约转 0.001 ETH。断言：合约余额增加（钱包中可见该笔转账记录）。"""
        contract_address = faucet_contract.address
        before = w3.eth.get_balance(contract_address)
        send_wei = 1_000_000_000_000_000
        gas_price = w3.eth.gas_price
        tx = {
            "from": tester_account.address,
            "to": contract_address,
            "value": send_wei,
            "chainId": w3.eth.chain_id,
            "nonce": w3.eth.get_transaction_count(tester_account.address),
            "gas": 100_000,
            "gasPrice": gas_price,
        }
        signed = tester_account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert receipt["status"] == 1, "转账交易应成功"
        assert receipt["to"] == contract_address
        assert w3.eth.get_balance(contract_address) == before + send_wei

    def test_08_getStats_balance_matches_chain(self, w3: Web3, faucet_contract: Contract) -> None:
        """步骤：getStats() 与 get_balance 对比。断言：一致且非负。"""
        total_claimed, contract_balance = faucet_contract.functions.getStats().call()
        assert isinstance(total_claimed, int) and total_claimed >= 0
        assert isinstance(contract_balance, int) and contract_balance >= 0
        assert contract_balance == w3.eth.get_balance(faucet_contract.address)

    # --- 四、claim 相关 view (09-11) ---
    def test_09_claimableAmount_non_negative(self, faucet_contract: Contract, tester_address: str) -> None:
        """步骤：claimableAmount(user)。断言：非负整数。"""
        amount = faucet_contract.functions.claimableAmount(tester_address).call()
        assert isinstance(amount, int) and amount >= 0

    def test_10_canClaim_returns_bool_and_uint(
        self, faucet_contract: Contract, tester_address: str
    ) -> None:
        """步骤：canClaim(user)。断言：返回 (bool, uint256)。"""
        can, wait_until = faucet_contract.functions.canClaim(tester_address).call()
        assert isinstance(can, bool) and isinstance(wait_until, int) and wait_until >= 0

    def test_11_getUserStats_returns_two_ints(
        self, faucet_contract: Contract, tester_address: str
    ) -> None:
        """步骤：getUserStats(user)。断言：返回两非负整数。"""
        user_claimed, last_claim_at = faucet_contract.functions.getUserStats(tester_address).call()
        assert user_claimed >= 0 and last_claim_at >= 0

    # --- 五、claim 流程 (12-13) ---
    def test_12_claim_once_increases_claimed(
        self, w3: Web3, faucet_contract: Contract, tester_account: Account, tester_address: str
    ) -> None:
        """步骤：若可领则 claim()。断言：userClaimed、totalClaimed 增加。"""
        claimable = faucet_contract.functions.claimableAmount(tester_address).call()
        if claimable == 0:
            pytest.skip("当前不可领（需 05 setParams + 07 充值且未达上限/冷却）")
        user_before, _ = faucet_contract.functions.getUserStats(tester_address).call()
        total_before, _ = faucet_contract.functions.getStats().call()
        receipt = _transact(w3, faucet_contract, "claim", (), tester_account)
        assert receipt["status"] == 1
        user_after, _ = faucet_contract.functions.getUserStats(tester_address).call()
        total_after, _ = faucet_contract.functions.getStats().call()
        assert user_after == user_before + claimable and total_after == total_before + claimable

    def test_13_after_claim_view_types_ok(self, faucet_contract: Contract, tester_address: str) -> None:
        """步骤：claim 后调用 claimableAmount、canClaim。断言：类型正确。"""
        claimable = faucet_contract.functions.claimableAmount(tester_address).call()
        can, _ = faucet_contract.functions.canClaim(tester_address).call()
        assert isinstance(claimable, int) and isinstance(can, bool)

    # --- 六、withdraw (14) ---
    def test_14_withdraw_owner_succeeds(
        self, w3: Web3, faucet_contract: Contract, tester_account: Account
    ) -> None:
        """步骤：owner withdraw(少量)。断言：合约余额减少。"""
        _, balance_before = faucet_contract.functions.getStats().call()
        if balance_before == 0:
            pytest.skip("合约余额为 0")
        withdraw_amount = min(balance_before, 1_000_000_000_000_000)
        assert withdraw_amount > 0, "withdraw 金额应大于 0"
        receipt = _transact(w3, faucet_contract, "withdraw", (withdraw_amount,), tester_account)
        assert receipt["status"] == 1, "withdraw 交易应成功"
        _, balance_after = faucet_contract.functions.getStats().call()
        assert balance_after == balance_before - withdraw_amount
        assert balance_after >= 0

    # --- 七、revert (15) ---
    def test_15_claim_when_claimable_zero_reverts(
        self, w3: Web3, faucet_contract: Contract, tester_account: Account, tester_address: str
    ) -> None:
        """步骤：claimableAmount==0 时调用 claim。断言：receipt.status==0。"""
        claimable = faucet_contract.functions.claimableAmount(tester_address).call()
        if claimable > 0:
            pytest.skip("当前可领，无法测 revert")
        receipt = _transact(w3, faucet_contract, "claim", (), tester_account)
        assert receipt["status"] == 0
