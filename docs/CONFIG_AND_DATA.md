# 配置管理优化说明

## 配置拆分策略

### 1. 敏感信息 → .env 文件

所有敏感信息（私钥、密码、API Key）存储在 `.env` 文件中，不提交到仓库。

**文件位置**：项目根目录 `.env`

**示例**：
```bash
# 私钥
DEPLOYER_PRIVATE_KEY=0x...
USER1_PRIVATE_KEY=0x...

# MetaMask
METAMASK_SEED_PHRASE=test test test...
METAMASK_PASSWORD=Test@1234

# API Key
API_KEY=your_api_key_here
```

### 2. 非敏感配置 → config.example.yaml

通用配置（超时时间、日志级别等）存储在 YAML 文件中，可以提交到仓库。

**文件位置**：`config/config.example.yaml`

**示例**：
```yaml
logging:
  level: "INFO"
  file: "logs/test.log"

ui:
  headless: true
  timeout: 30000
```

### 3. 配置优先级

**环境变量 > local.yaml > config.example.yaml**

程序会按照以下顺序加载配置：
1. 首先加载 `.env` 文件中的环境变量
2. 然后加载 `config/local.yaml`（如果存在）
3. 最后加载 `config/config.example.yaml`（如果存在）

环境变量的优先级最高，会覆盖配置文件中的同名配置。

## 使用方式

### 1. 初始化配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 填入实际值
vim .env
```

### 2. 在代码中使用

```python
from framework.core.config import config

# 获取配置
rpc_url = config.rpc_url
chain_id = config.chain_id
api_url = config.backend_api_url

# 获取账户
account = config.get_account("deployer")
private_key = account['private_key']

# 获取合约
contract_info = config.get_contract("token")
address = contract_info['address']
```

### 3. 环境变量命名规则

配置项 `ui.base_url` 对应环境变量 `UI_BASE_URL`

转换规则：
- 小写转大写
- `.` 替换为 `_`

示例：
```
ui.headless → UI_HEADLESS
api.timeout → API_TIMEOUT
logging.level → LOGGING_LEVEL
```

## 数据驱动优化

### 1. 快捷装饰器（推荐）

```python
from framework.utils.data_loader import parametrize_data

@parametrize_data("api/users.yaml", key="valid_users")
def test_login(test_data):
    username = test_data['username']
    password = test_data['password']
    # 测试逻辑
```

### 2. 自定义测试 ID

```python
# 使用字段名作为 ID
@parametrize_data("api/users.yaml", ids="username")
def test_users(test_data):
    pass

# 使用 lambda 自定义 ID
@parametrize_data("unit/token_transfer.json", ids=lambda x: x['description'])
def test_transfer(test_data):
    pass
```

### 3. 直接加载数据

```python
from framework.utils.data_loader import load_data

def test_batch():
    users = load_data("api/users.yaml", key="users")
    for user in users:
        # 测试逻辑
        pass
```

### 4. 支持的数据格式

- **JSON**: `data/api/users.json`
- **YAML**: `data/api/users.yaml`
- **CSV**: `data/ui/cases.csv`

### 5. 数据文件结构

```
data/
├── api/              # 接口测试数据
│   └── users.yaml
├── unit/             # 单元测试数据
│   └── token_transfer.json
├── integration/      # 集成测试数据
│   └── nft_purchase.json
└── ui/               # UI 测试数据
    └── transfer_cases.csv
```

## 完整示例

### 配置文件 (.env)

```bash
# 网络配置
LOCAL_RPC_URL=http://127.0.0.1:8545
ACTIVE_NETWORK=local

# 账户配置
DEPLOYER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
USER1_PRIVATE_KEY=0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d

# 合约配置
TOKEN_CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
NFT_CONTRACT_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512

# API 配置
BACKEND_API_URL=http://localhost:3000
DAPP_BASE_URL=http://localhost:3001

# MetaMask
METAMASK_SEED_PHRASE=test test test test test test test test test test test junk
METAMASK_PASSWORD=Test@1234
```

### 测试数据 (data/api/users.yaml)

```yaml
valid_users:
  - username: "testuser1"
    password: "Test@1234"
    expected_status: 200
  - username: "testuser2"
    password: "Test@5678"
    expected_status: 200
```

### 测试代码

```python
from framework.utils.data_loader import parametrize_data
from framework.core.config import config

@parametrize_data("api/users.yaml", key="valid_users", ids="username")
def test_login(test_data):
    # 从配置获取 API URL
    api_url = config.backend_api_url

    # 从测试数据获取用户信息
    username = test_data['username']
    password = test_data['password']

    # 执行测试
    response = requests.post(
        f"{api_url}/api/auth/login",
        json={"username": username, "password": password}
    )

    assert response.status_code == test_data['expected_status']
```

## 优势

1. **安全性**：敏感信息不提交到仓库
2. **灵活性**：环境变量可以覆盖配置文件
3. **易用性**：装饰器简化数据驱动测试
4. **可维护性**：配置和数据分离，易于管理
5. **扩展性**：支持多种数据格式，易于扩展

## 注意事项

1. `.env` 文件已在 `.gitignore` 中，不会提交到仓库
2. 使用 `.env.example` 作为模板，团队成员复制后填入实际值
3. CI/CD 环境中，通过环境变量注入敏感信息
4. 测试数据文件可以提交到仓库（不包含敏感信息）