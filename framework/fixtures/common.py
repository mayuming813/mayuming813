#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : common.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
from framework.core.web3_manager import web3_manager
from framework.core.logger import Logger


@pytest.fixture(scope="session")
def w3():
    """Web3 实例"""
    return web3_manager.w3


@pytest.fixture(scope="session")
def deployer_account():
    """部署者账户"""
    return web3_manager.get_account("deployer")


@pytest.fixture(scope="session")
def user1_account():
    """测试用户1"""
    return web3_manager.get_account("user1")


@pytest.fixture(scope="session")
def user2_account():
    """测试用户2"""
    return web3_manager.get_account("user2")


@pytest.fixture(scope="function")
def test_logger(request):
    """测试日志记录器"""
    logger = Logger.get_logger(request.node.name)
    logger.info(f"开始测试: {request.node.name}")
    yield logger
    logger.info(f"结束测试: {request.node.name}")


@pytest.fixture(scope="function")
def snapshot(w3):
    """区块链快照，用于测试后恢复状态"""
    snapshot_id = w3.provider.make_request("evm_snapshot", [])
    yield snapshot_id
    w3.provider.make_request("evm_revert", [snapshot_id['result']])
