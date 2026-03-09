# SepoliaClaimFaucet 单元测试说明

**一键执行（推荐）**：在项目根目录执行  
`python scripts/run_unit_tests.py`  

或：`pytest tests/unit/test_sepolia_claim_faucet.py -v -m unit`  

前置条件：已编译合约、已部署并配置 `.env` 中 `CONTRACT_ADDRESS`、`TEST_PRIVATE_KEY`、`ETH_RPC_URL`、`CHAIN_ID`。  
用例在单类内按 01～15 顺序执行，脚本可重复运行。

---

## 执行顺序（单类 TestSepoliaClaimFaucet，固定 01～15）

| 顺序 | 用例 | 步骤概要 | 断言概要 |
|------|------|----------|----------|
| 01 | test_01_contract_is_deployed_and_connected | 加载合约、owner() | owner 为 0x 地址 |
| 02 | test_02_owner_matches_deployer | owner 与 tester 地址对比 | 与本地钱包一致 |
| 03 | test_03_initial_params_and_stats | getParams、getStats | totalClaimed==0 |
| 04 | test_04_getParams_returns_four_values | getParams() | 返回 4 个 int |
| 05 | test_05_setParams_owner_succeeds | owner setParams | 成功且参数一致 |
| 06 | test_06_setParams_owner_can_repeat | owner 再次 setParams | 可重复 |
| 07 | test_07_contract_balance_increases_after_send | 向合约转 0.001 ETH | 余额增加 |
| 08 | test_08_getStats_balance_matches_chain | getStats 与链上余额 | 一致 |
| 09 | test_09_claimableAmount_non_negative | claimableAmount(user) | 非负 |
| 10 | test_10_canClaim_returns_bool_and_uint | canClaim(user) | (bool, uint) |
| 11 | test_11_getUserStats_returns_two_ints | getUserStats(user) | 两非负整数 |
| 12 | test_12_claim_once_increases_claimed | 可领时 claim() | userClaimed/totalClaimed 增加 |
| 13 | test_13_after_claim_view_types_ok | claim 后 view | 类型正确 |
| 14 | test_14_withdraw_owner_succeeds | owner withdraw | 合约余额减少 |
| 15 | test_15_claim_when_claimable_zero_reverts | 不可领时 claim | status==0 |

脚本可重复执行（同一合约、同一账户）；依赖不满足时部分用例会 skip。
