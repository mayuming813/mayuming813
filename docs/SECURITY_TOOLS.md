# 安全和性能检查工具

本框架集成了智能合约静态分析、安全扫描和 Gas 费用分析工具。

## 工具列表

### 1. Slither - 静态分析
- **功能**: 检测常见的智能合约漏洞和代码质量问题
- **速度**: 快速（秒级）
- **适用场景**: CI/CD 流水线、日常开发

### 2. Mythril - 安全扫描
- **功能**: 深度符号执行，检测安全漏洞
- **速度**: 较慢（分钟级）
- **适用场景**: 发布前安全审计

### 3. Gas Analyzer - Gas 费用分析
- **功能**: 追踪和分析合约函数的 Gas 消耗
- **速度**: 实时（测试执行时）
- **适用场景**: 性能优化、成本估算

## 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Slither（需要 solc）
pip install slither-analyzer

# 安装 Mythril（可选，较慢）
pip install mythril
```

## 快速使用

### 一键执行所有检查

```bash
# 快速检查（仅静态分析）
npm run security:check

# 完整检查（包含 Mythril，较慢）
npm run security:full

# 仅静态分析
npm run security:static
```

### 在测试中使用

```python
# 示例：Gas 追踪
def test_nft_mint_gas(gas_analyzer, nft_contract_api, test_accounts):
    """测试 NFT 铸造的 Gas 消耗"""
    owner = test_accounts[0]
    recipient = test_accounts[1]

    # 执行操作
    tx_hash = nft_contract_api.mint(recipient, "ipfs://token-1", owner)
    receipt = nft_contract_api.client.w3.eth.get_transaction_receipt(tx_hash)

    # 记录 Gas
    gas_analyzer.record_transaction("mint", receipt["gasUsed"], tx_hash)

    # 检查 Gas 消耗
    avg_gas = gas_analyzer.get_average_gas("mint")
    assert avg_gas < 200000, f"Gas 消耗过高: {avg_gas}"

    # 生成报告
    gas_analyzer.save_report("NFTMint")
```

### 运行安全测试示例

```bash
# 运行安全测试示例
npm run test:security

# 或使用 pytest
pytest examples/test_security_example.py -v
```

## 报告位置

所有报告保存在 `reports/` 目录：

```
reports/
├── security/           # 安全报告
│   ├── slither-report.json
│   └── mythril-*.json
└── gas/               # Gas 报告
    ├── gas-report-*.txt
    └── gas-report-*.json
```

### 查看 Gas 报告

```bash
# 查看所有 Gas 报告
npm run report:gas

# 或直接查看文件
cat reports/gas/gas-report-NFTMint.txt
```

## API 使用

### SlitherAnalyzer

```python
from framework.security import SlitherAnalyzer

analyzer = SlitherAnalyzer("contracts")

# 分析所有合约
result = analyzer.analyze()

# 获取高危漏洞
high_severity = analyzer.get_high_severity_issues(result)

# 生成报告
report = analyzer.generate_report(result)
print(report)
```

### MythrilScanner

```python
from framework.security import MythrilScanner

scanner = MythrilScanner("contracts")

# 扫描单个合约
result = scanner.scan("contracts/NFTMint.sol", max_depth=12)

# 获取严重问题
critical = scanner.get_critical_issues(result)

# 生成报告
report = scanner.generate_report(result)
print(report)
```

### GasAnalyzer

```python
from framework.security import GasAnalyzer

analyzer = GasAnalyzer()

# 记录交易
analyzer.record_transaction("mint", gas_used=150000, tx_hash="0x...")

# 获取统计
avg_gas = analyzer.get_average_gas("mint")
min_gas = analyzer.get_min_gas("mint")
max_gas = analyzer.get_max_gas("mint")

# 生成报告
analyzer.save_report("MyContract")

# 与基线对比
comparison = analyzer.compare_with_baseline("reports/gas/baseline.json")
```

## CI/CD 集成

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
        run: |
          pip install -r requirements.txt
          pip install slither-analyzer

      - name: Run security checks
        run: npm run security:check

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: reports/
```

## 最佳实践

1. **开发阶段**: 使用 Slither 进行快速检查
2. **提交前**: 运行完整的安全检查（包含 Mythril）
3. **性能优化**: 使用 Gas Analyzer 追踪和对比 Gas 消耗
4. **CI/CD**: 集成 Slither 到自动化流水线
5. **发布前**: 进行完整的安全审计和 Gas 优化

## 常见问题

### Q: Slither 报告太多误报怎么办？
A: 可以使用 `--exclude` 参数排除特定检测器，或在代码中添加 `// slither-disable-next-line` 注释。

### Q: Mythril 扫描太慢怎么办？
A: 可以降低 `max_depth` 参数，或只在发布前运行完整扫描。

### Q: 如何设置 Gas 消耗基线？
A: 首次运行后，将生成的 JSON 报告作为基线，后续使用 `compare_with_baseline()` 对比。

## 参考资源

- [Slither 文档](https://github.com/crytic/slither)
- [Mythril 文档](https://github.com/ConsenSys/mythril)
- [Smart Contract Security Best Practices](https://consensys.github.io/smart-contract-best-practices/)
