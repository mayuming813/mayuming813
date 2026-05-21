# UI 自动化测试增强功能说明

## 新增功能

### 1. 失败自动截图和录屏 ✅

**配置项**（`config/local.yaml`）：
```yaml
ui:
  screenshot_on_failure: true  # 失败时自动截图
  video_on_failure: true       # 失败时保留录屏
  record_video: true           # 是否录制视频
  trace_on_failure: true       # 失败时保存 trace
```

**工作原理**：
- 测试失败时，自动截取完整页面截图（保存在 `screenshots/`）
- 测试失败时，保留视频录制（保存在 `videos/`）
- 测试失败时，保存 Playwright Trace（保存在 `traces/`，可回放调试）
- 测试通过时，自动清理 trace（节省空间）

**文件命名**：
- 截图：`{测试名称}_{时间戳}.png`
- 视频：自动生成
- Trace：`{测试名称}_{时间戳}.zip`

### 2. 有头/无头模式切换 ✅

**命令行参数**：
```bash
# 无头模式（默认）
pytest tests/ui

# 有头模式（显示浏览器）
pytest tests/ui --headed

# 自定义操作延迟
pytest tests/ui --headed --slowmo=500
```

**配置文件**（`config/local.yaml`）：
```yaml
ui:
  headless: true   # 默认无头模式
  slow_mo: 100     # 默认操作延迟（毫秒）
```

**优先级**：命令行参数 > 配置文件

### 3. Assume 和 Assert 双重断言支持 ✅

#### 严格断言（Assert）
失败时立即停止测试，适用于关键验证点。

```python
from framework.utils.smart_assert import AssertMode
from framework.pages.dapp_home_page import DAppHomePage

def test_example(page):
    dapp_page = DAppHomePage(page, assert_mode=AssertMode.STRICT)

    # 失败立即停止
    dapp_page.assert_helper.true(condition, "错误信息")
```

#### 软断言（Assume）
收集所有失败，继续执行，适用于批量验证。

```python
from framework.utils.smart_assert import AssertMode
from framework.pages.dapp_home_page import DAppHomePage

def test_example(page):
    dapp_page = DAppHomePage(page, assert_mode=AssertMode.SOFT)

    # 即使失败也继续执行，最后统一报告
    dapp_page.assert_helper.true(condition1, "错误1")
    dapp_page.assert_helper.true(condition2, "错误2")
    dapp_page.assert_helper.true(condition3, "错误3")
```

#### 可用的断言方法

```python
# 相等性
assert_helper.equal(actual, expected, msg)
assert_helper.not_equal(actual, expected, msg)

# 布尔
assert_helper.true(condition, msg)
assert_helper.false(condition, msg)

# 空值
assert_helper.is_none(value, msg)
assert_helper.is_not_none(value, msg)

# 包含
assert_helper.contains(container, item, msg)
assert_helper.not_contains(container, item, msg)

# 比较
assert_helper.greater(actual, expected, msg)
assert_helper.less(actual, expected, msg)
assert_helper.greater_equal(actual, expected, msg)
assert_helper.less_equal(actual, expected, msg)

# 字符串
assert_helper.starts_with(text, prefix, msg)
assert_helper.ends_with(text, suffix, msg)
assert_helper.match(text, pattern, msg)  # 正则

# 其他
assert_helper.length(container, expected_length, msg)
assert_helper.instance_of(obj, expected_type, msg)
```

## 使用示例

### 示例 1：严格断言 + 失败截图

```python
@allure.title("测试钱包连接")
def test_connect_wallet(page, metamask_setup):
    dapp_page = DAppHomePage(page, assert_mode=AssertMode.STRICT)

    dapp_page.connect_wallet()

    # 失败立即停止并自动截图
    dapp_page.assert_helper.true(
        dapp_page.is_wallet_connected(),
        "钱包连接失败"
    )
```

### 示例 2：软断言 + 批量验证

```python
@allure.title("测试表单验证")
def test_form_validation(page):
    dapp_page = DAppHomePage(page, assert_mode=AssertMode.SOFT)

    # 收集所有错误
    dapp_page.assert_helper.true(
        page.locator("#name-error").is_visible(),
        "未显示姓名错误"
    )
    dapp_page.assert_helper.true(
        page.locator("#email-error").is_visible(),
        "未显示邮箱错误"
    )
    # 测试结束时统一报告所有失败
```

### 示例 3：有头模式调试

```bash
# 显示浏览器，慢速执行
pytest tests/ui/test_dapp_interaction.py::test_connect_metamask_strict \
  --headed \
  --slowmo=1000 \
  -v
```

## 查看失败信息

### 1. 查看截图
```bash
ls screenshots/
# test_connect_wallet_20260331_120000.png
```

### 2. 查看视频
```bash
ls videos/
# 自动生成的视频文件
```

### 3. 查看 Trace（推荐）
```bash
# 使用 Playwright 查看器回放操作
playwright show-trace traces/test_name_20260331_120000.zip
```

Trace 包含：
- 完整的操作步骤
- 每一步的截图
- 网络请求
- 控制台日志
- DOM 快照

## 文件结构

```
web3-auto-test/
├── screenshots/          # 失败截图
│   └── test_xxx_20260331_120000.png
├── videos/              # 失败录屏
│   └── video_xxx.webm
├── traces/              # Playwright Trace
│   └── test_xxx_20260331_120000.zip
├── framework/
│   ├── fixtures/
│   │   └── ui.py        # 增强的 UI fixtures
│   ├── pages/
│   │   └── base_page.py # 增强的 BasePage
│   └── utils/
│       └── smart_assert.py  # 智能断言工具
└── tests/ui/
    └── test_dapp_interaction.py  # 示例测试
```

## 依赖更新

新增依赖：
```
pytest-assume>=2.4.3  # 软断言支持
```

安装：
```bash
pip install -r requirements.txt
```

## 最佳实践

1. **关键路径用严格断言**：登录、支付等失败应立即停止
2. **批量验证用软断言**：表单验证、UI 检查可收集所有错误
3. **开发时用有头模式**：`--headed` 方便观察
4. **CI/CD 用无头模式**：默认配置，速度快
5. **失败时查看 Trace**：比视频更详细
6. **合理使用截图**：关键步骤手动截图，失败自动截图

## 完整示例

参考 `tests/ui/test_dapp_interaction.py`，包含：
- 严格断言示例
- 软断言示例
- 失败截图演示
- Allure 报告集成