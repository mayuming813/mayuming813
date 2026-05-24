#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : conftest.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : Staking 测试配置
"""

import pytest

# 导入 fixtures
pytest_plugins = [
    "tests.staking.fixtures.staking_fixtures",
]
