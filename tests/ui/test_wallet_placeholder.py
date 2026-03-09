"""
钱包 UI 自动化占位：直接操作 MetaMask 扩展（弹窗、确认/拒绝交易等）。
"""
import pytest
from playwright.sync_api import BrowserContext, Page


@pytest.mark.ui
class TestMetaMaskUI:
    """占位：在带 MetaMask 的浏览器中直接操作扩展弹窗。"""

    def test_browser_with_extension_launches(self, browser_with_metamask: BrowserContext) -> None:
        """带 MetaMask 扩展的浏览器可正常启动。"""
        assert browser_with_metamask is not None
        assert browser_with_metamask.pages is not None
        assert isinstance(browser_with_metamask.pages, list)

    def test_can_open_new_tab(self, wallet_page: Page) -> None:
        """在带扩展环境中可打开新标签页（用于后续打开 DApp 或等待 MetaMask 弹窗）。"""
        wallet_page.goto("about:blank")
        assert wallet_page.url is not None
        assert "about:blank" in wallet_page.url

    # 后续示例（直接操作 MetaMask 弹窗）：
    # 1. 从 context.pages 中找到 chrome-extension://.../home.html 的 Page
    # 2. 在 popup 上操作：解锁、切换网络、确认签名/交易等
    # 3. 与 DApp 页配合：DApp 发起请求 -> 切到 popup 点击确认 -> 断言链上结果
