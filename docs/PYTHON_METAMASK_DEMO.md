# Python 全程代码：编译、部署与测试

**编译、部署、单测、接口测试** 全部由 **Python/代码** 完成，**不需要在 MetaMask 里进行任何操作**。测试过程中如需确认链上数据（余额、交易记录等），可以打开 MetaMask 看一眼即可。

---

## 一、流程概览

```
合约源码 (contracts/temp_core_flow.sol)
    ↓ Python 编译 (scripts/compile_contract.py)
ABI + 字节码 → contracts/abi/*.json、contracts/build/*.json
    ↓ Python 部署 (scripts/deploy_contract.py，使用 .env 私钥)
链上合约地址 → .env CONTRACT_ADDRESS
    ↓ 单测 / 接口测试 / 数据一致性（全部 Python）
（可选）打开 MetaMask 查看余额、活动等链上数据
```

- **编译、部署、测试**：全程代码，不依赖 Remix，也不需要在 MetaMask 里点确认或签名。
- **MetaMask**：仅用于测试过程中需要时**查看**链上数据（如余额、活动 Tab 中的交易）。

---

## 二、环境准备

- Python 3.10+
- 项目依赖（含 `py-solc-x`、`web3`）：

```bash
pip install -r requirements.txt
```

首次编译会通过 `py-solc-x` 自动下载对应 `solc` 版本（如 0.8.20），需网络。

---

## 三、编译合约（Python）

在项目根目录执行：

```bash
python scripts/compile_contract.py
```

- 编译 `contracts/temp_core_flow.sol` 中的 `SepoliaClaimFaucet`。
- 产出：`contracts/abi/SepoliaClaimFaucet.json`、`contracts/build/SepoliaClaimFaucet.json`。

---

## 四、部署合约（Python，联动本地 MetaMask 钱包）

1. 在项目根目录配置 `.env`：
   - `ETH_RPC_URL`：链 RPC（如 Sepolia 使用 `https://rpc.sepolia.org`）。
   - `CHAIN_ID`：链 ID（Sepolia 为 `11155111`）。
   - `WALLET_ADDRESS`：本地 MetaMask 账户地址（如 `0xb1D0Ff0982D3b700eBE0b1861be6e6514e1f6164`），用于校验私钥是否与该钱包一致。
   - `TEST_PRIVATE_KEY`：在 MetaMask 中导出该账户私钥（账户详情 → 导出私钥），填入此处。部署将由此账户发起，与本地钱包联动。

2. 执行部署：

```bash
python scripts/deploy_contract.py
```

3. 若配置了 `WALLET_ADDRESS`，脚本会校验私钥对应地址是否一致；一致则打印「部署账户（与本地 MetaMask 联动）」并继续部署。终端输出**合约地址**与**交易哈希**；将合约地址写入 `.env` 的 `CONTRACT_ADDRESS`。

4. 部署后可在 MetaMask 中查看该账户的余额与活动 Tab 中的交易记录。

**验证与本地钱包联动**：执行 `python scripts/check_wallet_balance.py`，会按 .env 中的私钥/地址查询链上余额并打印；与 MetaMask 中同一地址、同一网络的余额对比一致即表示联动正确。

全程在命令行完成，无需在 MetaMask 里点确认。

---

## 五、测试（全部 Python）

- **单元测试**：`pytest -m unit`，使用 `CONTRACT_ADDRESS` 与 `contracts/abi/SepoliaClaimFaucet.json`，通过 `get_contract(w3, "SepoliaClaimFaucet")` 做 view/写方法断言。
- **接口测试**：`pytest -m api`，同一 RPC + 合约地址，对链上读/写与状态做校验。
- **数据一致性**：`pytest -m consistency`，链上数据与预期或 API 对比。

全部由代码与 pytest 完成，不需要在 MetaMask 里操作。

---

## 六、测试过程中查看链上数据（可选）

如需确认余额、交易是否上链等，可**打开 MetaMask** 查看：

- 顶部余额、**代币** Tab：查看 SepoliaETH 等。
- **活动** Tab：查看部署、setParams、claim 等交易记录。

仅作查看，不参与编译、部署与测试脚本执行。

---

## 七、与本工程配置小结

| 用途     | 说明 |
|----------|------|
| 编译     | `python scripts/compile_contract.py` |
| 部署     | `python scripts/deploy_contract.py`；.env 中 `WALLET_ADDRESS`（本地 MetaMask 地址）+ `TEST_PRIVATE_KEY`（从 MetaMask 导出）实现联动 |
| 单测/接口 | `.env` 中 `CONTRACT_ADDRESS`、`ETH_RPC_URL`、`CHAIN_ID`；ABI 来自编译产出 |
| 查看数据 | 需要时打开 MetaMask 查看该账户余额、活动即可 |

Sepolia 建议配置：

- `ETH_RPC_URL`: `https://rpc.sepolia.org` 或 `https://ethereum-sepolia.publicnode.com`
- `CHAIN_ID`: `11155111`
