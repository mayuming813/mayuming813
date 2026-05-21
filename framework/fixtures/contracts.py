#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : contracts.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
from framework.core.web3_manager import web3_manager


@pytest.fixture(scope="session")
def token_contract():
    """Token 合约实例"""
    return web3_manager.load_contract("token")


@pytest.fixture(scope="session")
def nft_contract():
    """NFT 合约实例"""
    return web3_manager.load_contract("nft")
