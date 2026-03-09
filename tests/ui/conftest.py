"""
UI 测试：使用 pynpress 启动 MetaMask，每次用配置的助记词导入钱包。
"""
from pathlib import Path
from typing import Optional

import pytest
from playwright.sync_api import BrowserContext, Page

from config import settings


def _metamask_extension_path() -> Optional[Path]:
    """MetaMask 扩展目录（.env 中 WALLET_EXTENSION_PATH 或 Chrome 默认路径）。"""
    path = getattr(settings, "wallet_extension_path", None)
    if path:
        return Path(path)
    for p in [
        Path.home() / "Library/Application Support/Google/Chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn",
        Path.home() / ".config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn",
    ]:
        if p.exists():
            sub = next(p.iterdir(), None)
            if sub and sub.is_dir():
                return sub
    return None


@pytest.fixture(scope="session")
def metamask_extension_path():
    """MetaMask 扩展路径，供 pynpress 加载。"""
    p = _metamask_extension_path()
    if not p:
        pytest.skip("WALLET_EXTENSION_PATH 未配置且未找到默认 MetaMask 扩展路径")
    return str(p)


@pytest.fixture(scope="module")
def pynpress_context_and_wallet(metamask_extension_path):
    """
    通过 pynpress 启动浏览器并用量身定制的助记词导入 MetaMask。
    每次运行都会执行导入流程，助记词与密码从配置读取。
    """
    from pynpress import Launcher, WalletType

    seed = getattr(settings, "metamask_seed_phrase", None) or ""
    if not seed or not seed.strip():
        pytest.skip("未配置 METAMASK_SEED_PHRASE 或 MNEMONIC，无法导入钱包")

    password = getattr(settings, "metamask_password", None) or "TestPassword123!"
    launcher = Launcher(WalletType.METAMASK)
    context, wallet = launcher.launch(
        seed_phrase=seed.strip(),
        password=password,
        headless=False,
        extension_path=metamask_extension_path,
    )
    yield context, wallet
    context.close()


@pytest.fixture(scope="module")
def browser_with_metamask(pynpress_context_and_wallet) -> BrowserContext:
    """与原有命名兼容：即 pynpress 的 browser context。"""
    context, _ = pynpress_context_and_wallet
    return context


@pytest.fixture(scope="module")
def pynpress_wallet(pynpress_context_and_wallet):
    """pynpress 的 Wallet 实例（approve_connect 等）。"""
    _, wallet = pynpress_context_and_wallet
    return wallet


@pytest.fixture(scope="module")
def metamask_extension_id(browser_with_metamask: BrowserContext) -> str:
    """从 context 的 service worker 获取扩展 ID。"""
    if len(browser_with_metamask.service_workers) == 0:
        browser_with_metamask.wait_for_event("serviceworker", timeout=15000)
    sw = browser_with_metamask.service_workers[0]
    return sw.url.split("/")[2]


@pytest.fixture(scope="module")
def metamask_popup_url(metamask_extension_id: str) -> str:
    """MetaMask 扩展主界面 URL（home.html）。"""
    return f"chrome-extension://{metamask_extension_id}/home.html"


@pytest.fixture
def wallet_page(browser_with_metamask: BrowserContext) -> Page:
    """在带 MetaMask 的浏览器中打开一个新标签页。"""
    page = browser_with_metamask.new_page()
    yield page
    page.close()


@pytest.fixture
def metamask_popup_page(browser_with_metamask: BrowserContext, metamask_popup_url: str) -> Page:
    """打开 MetaMask 扩展主界面页（单次使用）。"""
    page = browser_with_metamask.new_page()
    page.goto(metamask_popup_url, wait_until="domcontentloaded")
    yield page
    page.close()


@pytest.fixture(scope="module")
def shared_popup_page(browser_with_metamask: BrowserContext, metamask_popup_url: str) -> Page:
    """主流程用例共用的单页：pynpress 已导入钱包，打开 home 主界面。"""
    page = browser_with_metamask.new_page()
    page.goto(metamask_popup_url, wait_until="domcontentloaded")
    yield page
    page.close()
