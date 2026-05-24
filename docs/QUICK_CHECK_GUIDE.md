# 安全和性能检查工具 - 快速指南

## 一键命令

### 1. 静态分析（Slither）- 快速
```bash
# 检查所有合约
npm run check:slither

# 检查单个合约
python -m framework.utils.security_check --contract contracts/NFTMint.sol --slither
```

### 2. 安全扫描（Mythril）- 较慢
```bash
# 扫描单个合约
python -m framework.utils.security_check --contract contracts/NFTMint.sol --mythril

# 完整安全检查（Slither + Mythril）
python -m framework.utils.security_check --contract contracts/NFTMint.sol --all
```

### 3. 合约大小检查
```bash
# 编译并检查合约大小
npm run check:size

# 仅检查（不编译）
python -m framework.utils.contract_size
```

### 4. Gas 费用分析
```bash
# 分析所有测试的 Gas 消耗
npm run check:gas

# 分析特定测试
python -m framework.utils.gas_report --test tests/nft_mint/scenarios/test_nft_scenario.py --contract NFTMint

# 查看 Gas 报告
npm run report:gas
```

### 5. 完整检查
```bash
# 运行所有快速检查（Slither + 合约大小）
npm run check:all
```

## 详细用法

### security_check.py - 安全检查

```bash
# 基本用法
python -m framework.utils.security_check --contract <path> [--slither] [--mythril] [--all]

# 示例
python -m framework.utils.security_check --contract contracts/NFTMint.sol --slither
python -m framework.utils.security_check --contract contracts/ --all
python -m framework.utils.security_check --contract contracts/DEXSwap.sol --mythril --max-depth 12 --timeout 180
```

**参数说明：**
- `--contract`: 合约文件或目录路径（必需）
- `--slither`: 运行 Slither 静态分析
- `--mythril`: 运行 Mythril 安全扫描
- `--all`: 运行所有检查
- `--output`: 报告输出目录（默认：reports/security）
- `--max-depth`: Mythril 最大搜索深度（默认：22）
- `--timeout`: Mythril 超时时间（默认：300秒）

### gas_report.py - Gas 分析

```bash
# 基本用法
python -m framework.utils.gas_report --test <path> [--contract <name>]

# 示例
python -m framework.utils.gas_report --test tests/nft_mint/scenarios/
python -m framework.utils.gas_report --test tests/nft_mint/scenarios/test_nft_scenario.py --contract NFTMint

# 对比 Gas 报告
python -m framework.utils.gas_report --compare \
  --baseline reports/gas/baseline-NFTMint.json \
  --current reports/gas/gas-report-NFTMint.json \
  --threshold 0.1
```

**参数说明：**
- `--test`: 测试文件或目录路径
- `--contract`: 合约名称（用于过滤报告）
- `--output`: 报告输出目录（默认：reports/gas）
- `--compare`: 对比模式
- `--baseline`: 基线报告文件
- `--current`: 当前报告文件
- `--threshold`: 变化阈值（默认：0.1 = 10%）

### contract_size.py - 合约大小检查

```bash
# 基本用法
python -m framework.utils.contract_size [--artifacts <path>] [--compile]

# 示例
python -m framework.utils.contract_size
python -m framework.utils.contract_size --compile
python -m framework.utils.contract_size --artifacts artifacts/contracts
```

**参数说明：**
- `--artifacts`: 编译产物目录（默认：artifacts/contracts）
- `--output`: 报告输出目录（默认：reports/contract-size）
- `--compile`: 检查前先编译合约

## 报告位置

```
reports/
├── security/                    # 安全报告
│   ├── slither-NFTMint.json
│   └── mythril-NFTMint.json
├── gas/                         # Gas 报告
│   ├── gas-report-NFTMint.txt
│   └── gas-report-NFTMint.json
└── contract-size/               # 合约大小报告
    ├── contract-size-report.txt
    └── contract-size-report.json
```

## 工作流程示例

### 开发阶段
```bash
# 1. 编写合约
vim contracts/MyContract.sol

# 2. 编译
npm run compile

# 3. 快速检查
npm run check:slither
npm run check:size
```

### 提交前检查
```bash
# 完整检查
npm run check:all

# 如果时间充足，运行 Mythril
python -m framework.utils.security_check --contract contracts/MyContract.sol --mythril
```

### 性能优化
```bash
# 1. 运行测试并生成 Gas 报告
npm run check:gas

# 2. 查看报告
npm run report:gas

# 3. 优化后对比
python -m framework.utils.gas_report --compare \
  --baseline reports/gas/baseline.json \
  --current reports/gas/gas-report-MyContract.json
```

## CI/CD 集成

### GitHub Actions
```yaml
- name: Security Check
  run: npm run check:slither

- name: Contract Size Check
  run: npm run check:size

- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: security-reports
    path: reports/
```

## 常见问题

**Q: Slither 报告太多误报？**
A: 可以在合约中添加注释忽略特定检查：
```solidity
// slither-disable-next-line reentrancy-eth
function withdraw() public {
    // ...
}
```

**Q: Mythril 太慢？**
A: 降低 `--max-depth` 参数或只在发布前运行：
```bash
python -m framework.utils.security_check --contract contracts/MyContract.sol --mythril --max-depth 12 --timeout 120
```

**Q: 合约超过 24KB 限制？**
A: 优化建议：
1. 拆分大合约为多个小合约
2. 使用库（library）提取公共逻辑
3. 优化存储布局
4. 移除未使用的代码

**Q: 如何设置 Gas 基线？**
A: 首次运行后，复制报告作为基线：
```bash
cp reports/gas/gas-report-MyContract.json reports/gas/baseline-MyContract.json
```

## 最佳实践

1. **每次提交前运行 Slither**
2. **发布前运行完整安全检查**
3. **定期对比 Gas 消耗变化**
4. **保持合约大小在 20KB 以下**
5. **将报告集成到 CI/CD 流程**
