#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : ui.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from framework.core.config import config
from framework.pages.metamask_page import MetaMaskPage


@pytest.fixture(scope="session")
def browser_config(request):
    """浏览器配置"""
    # 命令行参数优先级高于配置文件
    headed = request.config.getoption("--headed")
    slowmo = request.config.getoption("--slowmo")

    return {
        'headless': not headed if headed else config.get('ui.headless', True),
        'slow_mo': int(slowmo) if slowmo else config.get('ui.slow_mo', 0)
    }


@pytest.fixture(scope="session")
def browser(browser_config):
    """浏览器实例"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=browser_config['headless'],
            slow_mo=browser_config['slow_mo']
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser, request):
    """浏览器上下文（带 MetaMask 扩展）"""
    # 创建目录
    video_dir = Path(__file__).parent.parent.parent / "videos"
    video_dir.mkdir(exist_ok=True)

    # 配置上下文
    video_size = config.get('ui.video_size', {'width': 1920, 'height': 1080})
    record_video = config.get('ui.record_video', True)

    context = browser.new_context(
        viewport=video_size,
        record_video_dir=str(video_dir) if record_video else None,
        record_video_size=video_size if record_video else None
    )

    # 启用 tracing（用于调试）
    if config.get('ui.trace_on_failure', True):
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    # 测试失败时的处理
    if request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False:
        # 保存 trace
        if config.get('ui.trace_on_failure', True):
            trace_dir = Path(__file__).parent.parent.parent / "traces"
            trace_dir.mkdir(exist_ok=True)
            trace_path = trace_dir / f"{request.node.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            context.tracing.stop(path=str(trace_path))

        # 保留视频（通过不删除）
        if config.get('ui.video_on_failure', True):
            pass  # 视频会自动保存
    else:
        # 测试通过时停止 tracing（不保存）
        if config.get('ui.trace_on_failure', True):
            context.tracing.stop()

    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, request):
    """页面实例"""
    page = context.new_page()
    page.goto(config.dapp_base_url)

    yield page

    # 测试失败时截图
    if request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False:
        if config.get('ui.screenshot_on_failure', True):
            screenshot_dir = Path(__file__).parent.parent.parent / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / f"{request.node.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)

    page.close()


@pytest.fixture(scope="session")
def metamask_setup(browser: Browser):
    """MetaMask 初始化（仅执行一次）"""
    # 创建临时上下文用于初始化 MetaMask
    context = browser.new_context()
    page = context.new_page()

    metamask = MetaMaskPage(page)
    seed_phrase = config.metamask_seed_phrase
    password = config.metamask_password

    # 初始化 MetaMask（导入钱包）
    metamask.import_wallet(seed_phrase, password)

    context.close()
    return True


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook 用于在 fixture 中访问测试结果
    使得可以在失败时执行特定操作
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

