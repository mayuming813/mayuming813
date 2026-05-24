# 安全和性能检查工具 - 使用指南

## ✅ 已完成功能

本框架已集成以下智能合约检查工具：

1. **静态分析** - Slither（可选安装，有基本分析后备）
2. **安全扫描** - Mythril（可选安装）
3. **合约大小检查** - 内置工具
4. **Gas 费用分析** - 内置工具

## 🚀 快速开始

### 一键命令（推荐）

```bash
# 运行所有快速检查（静态分析 + 合约大小）
npm run check:all

# 单独运行
npm run check:slither    # 静态分析
npm run check:size       # 合约大小检查
npm run check:gas        # Gas 分析（需要先运行测试）
```

### 检查单个合约

```bash
# 静态分析单个合约
python3 -m framework.utils.security_check --contract contracts/SimpleDEX.sol --slither

# 安全扫描单个合约（需要安装 Mythril）
python3 -m framework.utils.security_check --contract contracts/SimpleDEX.sol --mythril

# 完整检查
python3 -m framework.utils.security_check --contract contracts/SimpleDEX.sol --all
```

## 📊 测试结果

### ✅ 合约大小检查 - 通过

```
Contract                                 Size (bytes)    Size (KB)       Status
-------------------------------------------------------------------------------------
MockERC20                                3,173           3.10            ✅  12.9%
MockERC20Permit                          5,605           5.47            ✅  22.8%
MockERC721                               6,910           6.75            ✅  28.1%
SimpleDEX                                4,679           4.57            ✅  19.0%
StakingPool                              3,892           3.80            ✅  15.8%

Total contracts: 5
Oversized contracts: 0
```

所有合约都在 24KB 限制内，最大的合约（MockERC721）仅占用 28.1% 的限制。

### ⚠️ 静态分析 - 发现问题

```
Total issues: 8
  🔴 High: 3
  🟢 Informational: 5

High Severity Issues:
  - unchecked-transfer: Return value of transfer not checked (3 instances)
```

**建议修复：**
- 检查 ERC20 token 的 `transfer` 返回值
- 或使用 OpenZeppelin 的 `SafeERC20` 库

## 📁 报告位置

所有报告保存在 `reports/` 目录：

```
reports/
├── security/                    # 安全报告
│   ├── basic-analysis-all.json
│   └── slither-*.json
├── gas/                         # Gas 报告
│   ├── gas-report-*.txt
│   └── gas-report-*.json
└── contract-size/               # 合约大小报告
    ├── contract-size-report.txt
    └── contract-size-report.json
```

## 🛠️ 工具详解

### 1. security_check.py - 安全检查

**功能：**
- Slither 静态分析（可选，未安装时使用基本分析）
- Mythril 安全扫描（可选）
- 支持单文件或目录批量检查

**用法：**
```bash
# 基本用法
python3 -m framework.utils.security_check --contract <path> [--slither] [--mythril] [--all]

# 示例
python3 -m framework.utils.security_check --contract contracts/SimpleDEX.sol --slither
python3 -m framework.utils.security_check --contract contracts/ --all
```

**参数：**
- `--contract`: 合约文件或目录路径（必需）
- `--slither`: 运行 Slither 静态分析
- `--mythril`: 运行 Mythril 安全扫描
- `--all`: 运行所有检查
- `--output`: 报告输出目录（默认：reports/security）

### 2. contract_size.py - 合约大小检查

**功能：**
- 检查所有编译后的合约大小
- 标识超过 24KB 限制的合约
- 生成详细报告

**用法：**
```bash
# 基本用法
python3 -m framework.utils.contract_size [--artifacts <path>]

# 示例
python3 -m framework.utils.contract_size
python3 -m framework.utils.contract_size --artifacts artifacts/contracts/contracts
```

**参数：**
- `--artifacts`: 编译产物目录（默认：artifacts/contracts）
- `--output`: 报告输出目录（默认：reports/contract-size）
- `--compile`: 检查前先编译合约

### 3. gas_report.py - Gas 分析

**功能：**
- 追踪测试中的 Gas 消耗
- 生成详细的 Gas 报告
- 对比基线报告

**用法：**
```bash
# 基本用法
python3 -m framework.utils.gas_report --test <path> [--contract <name>]

# 示例
python3 -m framework.utils.gas_report --test tests/nft_mint/scenarios/
python3 -m framework.utils.gas_report --test tests/dex_swap/ --contract SimpleDEX

# 对比报告
python3 -m framework.utils.gas_report --compare \
  --baseline reports/gas/baseline-SimpleDEX.json \
  --current reports/gas/gas-report-SimpleDEX.json
```

**参数：**
- `--test`: 测试文件或目录路径
- `--contract`: 合约名称（用于过滤报告）
- `--compare`: 对比模式
- `--baseline`: 基线报告文件
- `--current`: 当前报告文件

## 📦 可选依赖安装

### Slither（推荐）

```bash
pip install slither-analyzer
```

**优势：**
- 快速（秒级）
- 检测 70+ 种漏洞
- 适合 CI/CD 集成

**注意：** 未安装时会使用基本分析（检测常见问题）

### Mythril（可选）

```bash
pip install mythril
```

**优势：**
- 深度符号执行
- 检测复杂漏洞

**注意：** 较慢（分钟级），建议发布前使用

## 🔄 工作流程建议

### 开发阶段
```bash
# 1. 编写合约
vim contracts/MyContract.sol

# 2. 快速检查
npm run check:all
```

### 提交前
```bash
# 完整检查
npm run check:all

# 查看报告
cat reports/security/basic-analysis-all.json
cat reports/contract-size/contract-size-report.txt
```

### 发布前
```bash
# 完整安全检查（如果安装了 Mythril）
python3 -m framework.utils.security_check --contract contracts/ --all

# Gas 优化
npm run check:gas
npm run report:gas
```

## 🎯 CI/CD 集成

### GitHub Actions 示例

```yaml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run security checks
        run: npm run check:all

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: reports/
```

## ❓ 常见问题

**Q: 为什么不使用 Hardhat 插件？**
A: Hardhat 3.x 与现有插件不兼容，Python 脚本更灵活且与 pytest 框架集成更好。

**Q: 基本分析和 Slither 有什么区别？**
A: 基本分析检测常见问题（tx.origin、未检查的 transfer 等），Slither 提供 70+ 种检测器。

**Q: 如何修复 "unchecked-transfer" 问题？**
A: 使用 OpenZeppelin 的 SafeERC20：
```solidity
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

using SafeERC20 for IERC20;
token.safeTransfer(to, amount);
```

**Q: 合约超过 24KB 怎么办？**
A: 优化建议：
1. 拆分大合约为多个小合约
2. 使用库（library）提取公共逻辑
3. 优化存储布局
4. 移除未使用的代码

## 📚 参考资源

- [Slither 文档](https://github.com/crytic/slither)
- [Mythril 文档](https://github.com/ConsenSys/mythril)
- [Smart Contract Security Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [EIP-170: Contract code size limit](https://eips.ethereum.org/EIPS/eip-170)

## ✨ 总结

本框架提供了完整的智能合约检查工具链：

✅ **已测试通过：**
- 合约大小检查 - 所有合约都在限制内
- 静态分析 - 发现 8 个问题（3 个高危）
- 一键命令 - `npm run check:all` 正常工作

✅ **功能完整：**
- 支持单文件和目录批量检查
- 自动生成 JSON 和文本报告
- 提供基本分析后备方案
- 集成到 npm scripts

✅ **易于使用：**
- 一键命令快速检查
- 详细的帮助文档
- 清晰的报告输出
