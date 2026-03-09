# Web3 测试工程

用 Python 测链上接口、智能合约和钱包 UI，带编译/部署脚本，不依赖 Remix，结果统一出到 `log/`。

---

## 一眼看懂：测什么、在哪、怎么跑

| 测什么 | 代码在哪 | 怎么跑 | 结果/说明 |
|--------|----------|--------|-----------|
| 合约单测（view/写方法） | `tests/unit/` | `python scripts/run_unit_tests.py` | [log/unit/](log/)、[tests/unit/README](tests/unit/README.md) |
| 链上 RPC / JSON-RPC | `tests/api/` | `python scripts/run_api_tests.py` | [log/api/](log/)、[tests/api/README](tests/api/README.md) |
| 钱包 UI（MetaMask） | `tests/ui/` | `python scripts/run_ui_tests.py` | [log/ui/](log/)、[tests/ui/README](tests/ui/README.md) |
| 链上 vs 合约一致性 | `tests/consistency/` | `python scripts/run_consistency_tests.py` | [log/consistency/](log/)、[tests/consistency/README](tests/consistency/README.md) |

合约从源码编译、用私钥部署，见下方「编译与部署」；详细文档在 [docs/](docs/)。

---

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium   # 仅 UI 测试需要
cp .env.example .env
# 编辑 .env：至少填 ETH_RPC_URL、CHAIN_ID；要跑合约/UI 再填 TEST_PRIVATE_KEY、CONTRACT_ADDRESS
```

---

## 运行测试

```bash
# 推荐：用脚本跑，结果进 log/ 对应子目录
python scripts/run_unit_tests.py
python scripts/run_api_tests.py
python scripts/run_ui_tests.py
python scripts/run_consistency_tests.py

# 或用 pytest 直接跑
pytest -m unit
pytest -m api
pytest -m ui
pytest -m consistency
```

结果目录说明见 [log/README.md](log/README.md)（junit.xml、summary.txt 等）。

---

## 配置（.env）

| 变量 | 说明 |
|------|------|
| `ETH_RPC_URL` | 链 RPC，默认 `http://127.0.0.1:8545` |
| `CHAIN_ID` | 链 ID，默认 `1337` |
| `TEST_PRIVATE_KEY` | 测试账户私钥（合约/链上用例用，不填部分会 skip） |
| `CONTRACT_ADDRESS` | 默认合约地址 |
| `BASE_URL` | UI 测试基础 URL |
| `API_BASE_URL` | 业务 API 基地址（一致性/接口用） |

可选：复制 `config/env.yaml.example` 为 `config/env.yaml` 做更多配置。

---

## 编译与部署（不依赖 Remix）

- 合约源码：`contracts/temp_core_flow.sol`（SepoliaClaimFaucet）
- 编译：`python scripts/compile_contract.py`
- 部署：`python scripts/deploy_contract.py`（用 .env 里 `TEST_PRIVATE_KEY`）
- 查余额：`python scripts/check_wallet_balance.py`（和 MetaMask 对照）

详见 [docs/PYTHON_METAMASK_DEMO.md](docs/PYTHON_METAMASK_DEMO.md)。

---

## 项目结构（只看这一块就够）

```
├── config/           # 配置（settings.py、env.yaml.example）
├── contracts/        # 合约源码、ABI、contract_loader
├── scripts/          # 编译、部署、跑各层测试
├── utils/            # Web3/链 RPC/一致性工具
├── tests/            # 单测、接口、UI、一致性
│   ├── unit/         # 合约单测
│   ├── api/          # 链上 RPC / JSON-RPC
│   ├── ui/           # Playwright + MetaMask
│   └── consistency/  # 链上 vs 合约/API 一致性
├── log/              # 测试结果（unit/api/ui/consistency）
└── docs/             # 说明文档、测试方案
```

---

## 文档

| 文档 | 说明 |
|------|------|
| [docs/PYTHON_METAMASK_DEMO.md](docs/PYTHON_METAMASK_DEMO.md) | 编译、部署、和 MetaMask 联动 |
| [docs/REMIX_METAMASK_DEMO.md](docs/REMIX_METAMASK_DEMO.md) | 若仍用 Remix 时的说明 |
| [docs/测试方案/](docs/测试方案/) | 交易所业务场景与测试方案 |

环境要求：Python 3.10+，本地或远程 EVM 节点（如 Hardhat、测试网 RPC）。
