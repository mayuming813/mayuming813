# UI 自动化：pynpress + MetaMask（助记词导入）

本目录使用 **pynpress** 启动带 MetaMask 扩展的浏览器，**每次运行都通过配置的助记词导入钱包**，再打开扩展主界面（`home.html`）完成主流程。助记词与密码配置化，步骤可复现。

## 主流程用例（test_wallet_main_flow.py）

| 用例 | 步骤 | 说明 |
|------|------|------|
| test_01_open_metamask_popup_and_see_main_ui | 共用页已打开 popup，断言主界面（发送/收款）可见 | 校验插件弹窗可正常打开 |
| test_02_send_eth_from_popup_to_contract | 同一页回到 popup → 发送 → 填合约地址与金额 → 下一步/确认 | 需 CONTRACT_ADDRESS |
| test_03_full_flow_popup_only | 同一页回到 popup → 完整发送流程 → 确认 | 不重复开页 |

**说明**：三个用例共用一个浏览器、一个 popup 页（`shared_popup_page`），按 01 → 02 → 03 顺序执行，不在每个用例里重复 `new_page()`。

## 配置与运行

- **METAMASK_SEED_PHRASE**（或 **MNEMONIC**）：助记词，必填。pynpress 每次启动都会用该助记词执行「导入钱包」流程。
- **METAMASK_PASSWORD**：MetaMask 解锁密码，导入时设置。默认 `TestPassword123!`，可在 `.env` 覆盖。
- **WALLET_EXTENSION_PATH**：MetaMask 扩展目录；不填则使用 conftest 默认 Chrome 扩展路径。
- **CONTRACT_ADDRESS**：test_02、test_03 向该地址发送 0.001 ETH，不配置则跳过。
- **浏览器**：需安装 Playwright Chromium：`python3 -m playwright install chromium`。
- 运行后 pynpress 会自动完成导入，进入 home 主界面；建议在测试前将网络切到 Sepolia。

## MetaMask 可操作项速查（与文档对应）

完整说明见 [docs/REMIX_METAMASK_DEMO.md](../../docs/REMIX_METAMASK_DEMO.md) 第五节。

| 用途 | 界面位置 | 说明 |
|------|----------|------|
| 确认/拒绝交易 | 弹窗（Remix 发起交易后） | 确认、拒绝、修改 Gas 等 |
| 给合约转 ETH | 主界面 **发送** | 收款地址 = 合约地址，金额 = SepoliaETH |
| 查交易结果 | 主界面 **活动** Tab | 最新交易状态、成功/失败 |
| 当前余额 | 主界面顶部 或 **代币** Tab | 断言余额或代币列表 |
| 切换网络 | 顶部网络选择 | 确保 Sepolia |
| 切换账户 | 顶部账户下拉（如 Account 1） | 多账户场景 |
| 复制地址 | 账户旁复制图标 | 当前账户或用于“发送”收款方 |

自动化时优先覆盖：**发送**（填合约地址+金额+确认）、**活动**（断言交易成功）、弹窗内的**确认**按钮。

## 元素定位（优先 data-testid）

`locators.py` 中**优先使用 MetaMask 官方 data-testid**（与扩展 E2E 一致），无则回退到 role/文案：

- **data-testid**：`send-token-button`、`receive-token-button`、`recipient-address-input`、`amount-input`、`review-button`、`confirm-footer-button`、`page-container__next-button` 等（见 [metamask-extension](https://github.com/MetaMask/metamask-extension) 源码）。
- **回退**：`get_by_role("button", name=SEND)`、`get_by_text(SEND)` 等，兼容未提供 testid 的版本或语言。

用例中统一通过 `get_by_test_id(TESTID_XXX).or_(role/text 回退)` 定位，避免只依赖文案导致多语言/版本失败。
