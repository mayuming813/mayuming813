# 测试结果输出目录

| 子目录 | 说明 | 生成方式 |
|--------|------|----------|
| unit/ | 单元测试结果 | `python scripts/run_unit_tests.py` |
| api/  | 接口测试结果 | `python scripts/run_api_tests.py` |
| ui/   | UI 测试结果 | `python scripts/run_ui_tests.py` |
| consistency/ | 一致性测试结果 | `python scripts/run_consistency_tests.py` |

每次运行脚本会写入：
- **junit.xml**：JUnit 格式，便于 CI 或工具解析。
- **summary.txt**：文本摘要，列出**失败**与**跳过**的用例及原因，便于快速排查。
