# 接口自动化：链上 RPC 与 JSON-RPC

## 目录说明

- **test_chain_rpc.py**：基于 Web3 的链上接口（chain_id、block_number、get_block、get_balance 等）。
- **test_json_rpc.py**：**Raw JSON-RPC** 接口自动化，直接对 `ETH_RPC_URL` 发起 `eth_*` / `net_*` / `web3_*` 请求并断言：
  - `eth_blockNumber`、`eth_chainId`、`eth_getBalance`、`eth_getBlockByNumber`、`eth_gasPrice`
  - `net_version`、`web3_clientVersion`
  - 错误请求的异常处理
  - 与 Web3 结果一致性（同一查询 RPC 与 Web3 应一致）

## 运行

```bash
python scripts/run_api_tests.py
```

结果写入 `log/api/junit.xml` 与 `log/api/summary.txt`。

## 配置

- **ETH_RPC_URL**、**CHAIN_ID**：链地址与链 ID。
- **TEST_PRIVATE_KEY** / **CONTRACT_ADDRESS**：部分用例需要（如 get_balance、一致性用例）。
