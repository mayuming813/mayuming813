# UI 测试使用指南

## 功能特性

### 1. 失败自动截图和录屏

测试失败时会自动：
- 截取完整页面截图（保存在 `screenshots/` 目录）
- 保留视频录制（保存在 `videos/` 目录）
- 保存 Playwright Trace（保存在 `traces/` 目录，可用于回放调试）

### 2. 有头/无头模式切换

```bash
# 无头模式（默认，配置文件中设置）
pytest tests/ui

# 有头模式（显示浏览器窗口）
pytest tests/ui --headed

# 自定义操作延迟（毫秒）
pytest tests/ui --headed --slowmo=500
```

### 3. 双重断言支持

#### 严格断言（Assert）
失败时立即停止测试，适用于关键验证点。

```python
from framework.utils.smart_assert import AssertMode
from framework.pages.dapp_home_page import DAppHomePage

def test_example(page):
    dapp_page = DAppHomePage(page, assert_mode=AssertMode.STRICT)

    # 失败立即停止
    dapp_page.assert_helper.true(condition, "错误信息")
    dapp_page.assert_helper.equal(actual, expected, "错误信息")
```

#### 软断言（Assume）
收集所有失败，继续执行，适用于批量验证。

```python
from framework.utils.smart_assert import AssertMode
from framework.pages.dapp_home_page import DAppHomePage

def test_example(page):
    dapp_page = DAppHomePage(page, assert_mode=AssertMode.SOFT)

    # 即使失败也继续执行
    dapp_page.assert_helper.true(condition1, "错误1")
    dapp_page.assert_helper.true(condition2, "错误2")
    dapp_page.assert_helper.true(condition3, "错误3")
    # 最后统一报告所有失败
```

### 4. 可用的断言方法

```python
# 相等性断言
assert_helper.equal(actual, expected, msg)
assert_helper.not_equal(actual, expected, msg)

# 布尔断言
assert_helper.true(condition, msg)
assert_helper.false(condition, msg)

# 空值断言
assert_helper.is_none(value, msg)
assert_helper.is_not_none(value, msg)

# 包含断言
assert_helper.contains(container, item, msg)
assert_helper.not_contains(container, item, msg)

# 比较断言
assert_helper.greater(actual, expected, msg)
assert_helper.greater_equal(actual, expected, msg)
assert_helper.less(actual, expected, msg)
assert_helper.less_equal(actual, expected, msg)

# 字符串断言
assert_helper.starts_with(text, prefix, msg)
assert_helper.ends_with(text, suffix, msg)
assert_helper.match(text, pattern, msg)  # 正则匹配

# 其他断言
assert_helper.length(container, expected_length, msg)
assert_helper.instance_of(obj, expected_type, msg)
```

## 配置说明

在 `config/local.yaml` 中配置：

```yaml
ui:
  base_url: "http://localhost:3001"
  headless: true  # 默认无头模式
  slow_mo: 100  # 操作延迟（毫秒）
  screenshot_on_failure: true  # 失败时截图
  video_on_failure: true  # 失败时保留录屏
  record_video: true  # 是否录制视频
  video_size:
    width: 1920
    height: 1080
  trace_on_failure: true  # 失败时保存 trace
```

## 使用示例

### 示例 1：严格断言 + 失败截图

```python
@allure.title("测试钱包连接")
def test_connect_wallet(page, metamask_setup):
    dapp_page = DAppHomePage(page, assert_mode=AssertMode.STRICT)

    # 连接钱包
    dapp_page.connect_wallet()

    # 严格断言：失败立即停止并截图
    dapp_page.assert_helper.true(
        dapp_page.is_wallet_connected(),
        "钱包连接失败"
    )

    # 手动截图
    dapp_page.screenshot("wallet_connected")
```

### 示例 2：软断言 + 批量验证

```python
@allure.title("测试表单验证")
def test_form_validation(page):
    dapp_page = DAppHomePage(page, assert_mode=AssertMode.SOFT)

    # 软断言：收集所有错误
    with allure.step("验证所有表单字段"):
        dapp_page.assert_helper.true(
            page.locator("#name-error").is_visible(),
            "未显示姓名错误"
        )
        dapp_page.assert_helper.true(
            page.locator("#email-error").is_visible(),
            "未显示邮箱错误"
        )
        dapp_page.assert_helper.true(
            page.locator("#phone-error").is_visible(),
            "未显示电话错误"
        )
    # 测试结束时统一报告所有失败
```

### 示例 3：有头模式调试

```bash
# 显示浏览器，慢速执行，方便观察
pytest tests/ui/test_dapp_interaction.py::TestDAppWalletConnection::test_connect_metamask_strict \
  --headed \
  --slowmo=1000 \
  -v
```

### 示例 4：查看失败录屏

测试失败后：

1. 截图保存在 `screenshots/` 目录
2. 视频保存在 `videos/` 目录
3. Trace 保存在 `traces/` 目录

查看 Trace（可回放操作）：

```bash
playwright show-trace traces/test_name_20260331_120000.zip
```

## 最佳实践

1. **关键路径使用严格断言**：登录、支付等关键流程失败应立即停止
2. **批量验证使用软断言**：表单验证、UI 元素检查等可以收集所有错误
3. **开发时使用有头模式**：`--headed` 方便观察和调试
4. **CI/CD 使用无头模式**：默认配置，速度快
5. **失败时查看 Trace**：比视频更详细，可以查看网络请求、控制台日志等
6. **合理使用截图**：关键步骤手动截图，失败自动截图

## 故障排查

### 问题：视频没有保存

检查配置：
```yaml
ui:
  record_video: true
  video_on_failure: true
```

### 问题：截图不清晰

调整视频尺寸：
```yaml
ui:
  video_size:
    width: 1920
    height: 1080
```

### 问题：软断言没有报告失败

确保安装了 `pytest-assume`：
```bash
pip install pytest-assume
```

### 问题：有头模式不显示浏览器

检查命令行参数：
```bash
pytest tests/ui --headed  # 注意是 --headed 不是 --headless
```