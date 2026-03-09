# 编译、部署与测试说明

本项目**不依赖 Remix**，**全程用 Python 代码**完成编译、部署与测试，**不需要在 MetaMask 里进行任何操作**。测试过程中如需确认链上数据，可打开 MetaMask 查看。

---

## 推荐流程：Python 全程代码

详见 **[docs/PYTHON_METAMASK_DEMO.md](PYTHON_METAMASK_DEMO.md)**：

- **编译**：`python scripts/compile_contract.py`
- **部署**：`python scripts/deploy_contract.py`（.env 中配置 `TEST_PRIVATE_KEY`）
- **测试**：单测、接口测试等全部由 pytest 完成；需要时打开 MetaMask 查看余额、活动即可

---

## 若仍使用 Remix

若你希望用 Remix 编辑/调试合约，再在本地用 Python 做测试，可参考以下精简步骤（Remix 仅作部署与复制 ABI/地址用）：

1. 在 [Remix](https://remix.ethereum.org/) 中打开或粘贴 `contracts/temp_core_flow.sol`，Environment 选 **Injected Provider - MetaMask**，切换到 Sepolia 后部署。
2. 部署完成后，从 Remix 复制**合约地址**；在 **Solidity Compiler** 中复制 **ABI**，保存到本工程 `contracts/abi/SepoliaClaimFaucet.json`。
3. 在 `.env` 中配置 `CONTRACT_ADDRESS`、`ETH_RPC_URL`、`CHAIN_ID=11155111`，即可用本工程进行单测、接口测试与 UI 自动化。

**MetaMask 可操作项**（用于手测或 UI 自动化）仍可参考原说明：主界面「发送」给合约充值、在弹窗中确认 Remix 发起的交易、「活动」Tab 查看交易结果等。UI 自动化直接操作 MetaMask 扩展，见 `tests/ui/README.md`。
