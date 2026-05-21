# 测试框架使用示例

本目录包含了 Web3 自动化测试框架的完整使用示例，展示了如何使用框架提供的各种原子能力来构建测试。

## 📁 示例文件说明

### 1. `test_data_factory_examples.py`
**测试数据工厂使用示例**

展示如何使用 `TestDataFactory` 生成各种测试数据：
- 基础数据：唯一 ID、随机字符串、数字、时间戳
- 用户数据：用户名、邮箱、密码、手机号、地址
- Web3 数据：钱包地址、合约地址、交易哈希、代币数量
- 批量数据：随机选择、批量生成
- 参数化数据：测试矩阵、边界值
- 复杂结构：订单数据、嵌套数据
- 数据持久化：JSON 保存和加载

**运行方式：**
```bash
# 运行所有示例
pytest examples/test_data_factory_examples.py -v

# 运行特定示例类
pytest examples/test_data_factory_examples.py::TestBasicDataGeneration -v

# 直接执行脚本
python examples/test_data_factory_examples.py
```

### 2. `rpc_examples.py`
**RPC 测试完整示例**

展示 RPC 测试的三层架构使用方式：
- **单接口测试**：直接调用 RPC 接口进行测试
  - 区块链基础接口（区块号、区块信息、交易数量）
  - 合约接口（合约调用、Gas 估算）
- **场景测试**：通过 pytest fixtures 组装多个接口
  - 区块链查询场景（最新区块、历史区块）
  - 交易场景（交易生命周期）
- **数据驱动测试**：参数化测试
- **错误处理**：异常场景测试

**运行方式：**
```bash
# 运行所有 RPC 示例
pytest examples/rpc_examples.py -v

# 运行单接口测试
pytest examples/rpc_examples.py::TestBlockchainRPCExamples -v

# 运行场景测试
pytest examples/rpc_examples.py::TestBlockchainScenarios -v

# 生成 Allure 报告
pytest examples/rpc_examples.py --alluredir=allure-results
allure serve allure-results
```

## 🏗️ 框架架构理解

### 三层架构

```
framework/          # 原子能力层
    └── utils/      # 工具类（RPC 客户端、验证器、数据工厂等）

tests/
    └── rpc/
        ├── rpcs/       # 单接口层（封装单个 RPC 接口）
        ├── fixtures/   # 场景层（通过 fixtures 组装接口）
        └── scenarios/  # 场景测试（执行业务场景）
```

### 使用原则

1. **framework 提供原子能力**
   - 不包含业务逻辑
   - 提供通用工具类
   - 可在任何测试中复用

2. **单接口是构建块**
   - 封装单个 API/RPC 接口
   - 只负责调用和返回
   - 不包含断言和验证

3. **场景通过 fixtures 组装**
   - 使用 pytest fixtures 组合多个接口
   - 实现业务场景逻辑
   - 可以包含断言和验证

4. **测试执行场景**
   - 测试用例调用场景 fixtures
   - 验证场景执行结果
   - 生成测试报告

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置 RPC URL
# RPC_URL=https://your-rpc-endpoint
```

### 3. 运行示例

```bash
# 运行所有示例
pytest examples/ -v

# 生成 Allure 报告
pytest examples/ --alluredir=allure-results
allure serve allure-results
```

## 📚 学习路径

### 初学者
1. 先看 `test_data_factory_examples.py`，了解如何生成测试数据
2. 再看 `rpc_examples.py` 的单接口测试部分
3. 理解如何使用 fixtures 进行场景组装

### 进阶使用
1. 学习如何创建自定义 fixtures
2. 了解参数化测试和数据驱动
3. 掌握错误处理和重试机制

### 高级应用
1. 设计复杂的测试场景
2. 实现自定义验证器
3. 扩展框架能力

## 💡 最佳实践

### 1. 测试数据管理
```python
# ✅ 好的做法：使用数据工厂
factory = TestDataFactory()
address = factory.unique_wallet_address()

# ❌ 避免：硬编码测试数据
address = "0x1234567890123456789012345678901234567890"
```

### 2. 接口调用
```python
# ✅ 好的做法：使用封装的 RPC 类
response = blockchain_rpc.get_block_number()

# ❌ 避免：直接调用 RPC 客户端
response = rpc_client.call("eth_blockNumber", [])
```

### 3. 场景组装
```python
# ✅ 好的做法：使用 fixtures 组装场景
@pytest.fixture
def latest_block(blockchain_rpc, rpc_validator):
    # 组装逻辑
    return {"block_number": ..., "block_info": ...}

# ❌ 避免：在测试中写大量逻辑
def test_something():
    # 大量的接口调用和数据处理
    ...
```

### 4. 断言和验证
```python
# ✅ 好的做法：使用验证器
assert rpc_validator.validate_rpc_response(response)

# ✅ 好的做法：清晰的断言消息
assert block_number, "区块号不能为空"

# ❌ 避免：模糊的断言
assert block_number
```

## 🔧 常见问题

### Q: 如何添加新的 RPC 接口？
A: 在 `tests/rpc/rpcs/` 目录下的相应类中添加方法，参考现有接口实现。

### Q: 如何创建新的测试场景？
A: 在 `tests/rpc/fixtures/rpc_fixtures.py` 中创建新的 fixture，组合现有接口。

### Q: 如何生成测试报告？
A: 使用 `pytest --alluredir=allure-results`，然后 `allure serve allure-results`。

### Q: 如何处理异步操作？
A: 使用 `PollingHelper` 进行轮询，或使用 `@retry_on_failure` 装饰器。

## 📖 相关文档

- [框架设计文档](../docs/framework_design.md)
- [API 测试指南](../docs/api_testing_guide.md)
- [RPC 测试指南](../docs/rpc_testing_guide.md)
- [配置说明](../docs/configuration.md)

## 🤝 贡献

欢迎提交新的示例或改进现有示例！请确保：
- 代码清晰易懂
- 包含必要的注释
- 遵循项目的编码规范
