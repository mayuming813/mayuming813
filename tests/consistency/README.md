# 数据一致性检测

## 目录说明

- **test_consistency_placeholder.py**：一致性工具函数单元测试（diff_dict、assert_consistent、normalize_hex_address）。
- **test_chain_contract_consistency.py**：**链上与合约数据一致性**：
  - 合约 `getStats()` 中的 `contractBalance` 与链上 `eth_getBalance(contract)` 一致。
  - `owner`、`getParams()`、`getStats()` 类型与非负约束。
  - 使用 `normalize_hex_address`、`assert_consistent` 做链上数据与视图/API 的对比示例。

## 运行

```bash
python scripts/run_consistency_tests.py
```

结果写入 `log/consistency/junit.xml` 与 `log/consistency/summary.txt`。

## 配置

- **CONTRACT_ADDRESS**：合约地址，未配置则合约相关一致性用例跳过。
- 依赖 `tests/conftest.py` 中的 `w3`、`faucet_contract`。
