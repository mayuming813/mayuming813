#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : conftest.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    :
"""
import pytest

# 导入所有 fixtures
from framework.fixtures.common import *
from framework.fixtures.contracts import *
from framework.fixtures.ui import *


def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="以有头模式运行浏览器"
    )
    parser.addoption(
        "--slowmo",
        action="store",
        default=None,
        help="设置浏览器操作延迟（毫秒）"
    )