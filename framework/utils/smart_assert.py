#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : smart_assert.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
from typing import Any, Callable
from framework.core.logger import logger


class AssertMode:
    """断言模式"""
    STRICT = "strict"  # 严格模式，使用 assert，失败立即停止
    SOFT = "soft"      # 软断言模式，使用 assume，收集所有失败


class SmartAssert:
    """智能断言类，支持 assert 和 assume 双模式"""

    def __init__(self, mode: str = AssertMode.STRICT):
        """
        初始化断言模式
        :param mode: AssertMode.STRICT 或 AssertMode.SOFT
        """
        self.mode = mode

    def equal(self, actual: Any, expected: Any, msg: str = None):
        """断言相等"""
        message = msg or f"预期 {expected}, 实际 {actual}"
        if self.mode == AssertMode.STRICT:
            assert actual == expected, message
        else:
            pytest.assume(actual == expected, message)
        logger.info(f"✓ 断言通过: {message}")

    def not_equal(self, actual: Any, expected: Any, msg: str = None):
        """断言不相等"""
        message = msg or f"预期不等于 {expected}, 实际 {actual}"
        if self.mode == AssertMode.STRICT:
            assert actual != expected, message
        else:
            pytest.assume(actual != expected, message)
        logger.info(f"✓ 断言通过: {message}")

    def true(self, condition: bool, msg: str = None):
        """断言为真"""
        message = msg or f"预期为 True, 实际为 {condition}"
        if self.mode == AssertMode.STRICT:
            assert condition is True, message
        else:
            pytest.assume(condition is True, message)
        logger.info(f"✓ 断言通过: {message}")

    def false(self, condition: bool, msg: str = None):
        """断言为假"""
        message = msg or f"预期为 False, 实际为 {condition}"
        if self.mode == AssertMode.STRICT:
            assert condition is False, message
        else:
            pytest.assume(condition is False, message)
        logger.info(f"✓ 断言通过: {message}")

    def is_none(self, value: Any, msg: str = None):
        """断言为 None"""
        message = msg or f"预期为 None, 实际为 {value}"
        if self.mode == AssertMode.STRICT:
            assert value is None, message
        else:
            pytest.assume(value is None, message)
        logger.info(f"✓ 断言通过: {message}")

    def is_not_none(self, value: Any, msg: str = None):
        """断言不为 None"""
        message = msg or f"预期不为 None, 实际为 {value}"
        if self.mode == AssertMode.STRICT:
            assert value is not None, message
        else:
            pytest.assume(value is not None, message)
        logger.info(f"✓ 断言通过: {message}")

    def contains(self, container: Any, item: Any, msg: str = None):
        """断言包含"""
        message = msg or f"预期 {container} 包含 {item}"
        if self.mode == AssertMode.STRICT:
            assert item in container, message
        else:
            pytest.assume(item in container, message)
        logger.info(f"✓ 断言通过: {message}")

    def not_contains(self, container: Any, item: Any, msg: str = None):
        """断言不包含"""
        message = msg or f"预期 {container} 不包含 {item}"
        if self.mode == AssertMode.STRICT:
            assert item not in container, message
        else:
            pytest.assume(item not in container, message)
        logger.info(f"✓ 断言通过: {message}")

    def greater(self, actual: Any, expected: Any, msg: str = None):
        """断言大于"""
        message = msg or f"预期 {actual} > {expected}"
        if self.mode == AssertMode.STRICT:
            assert actual > expected, message
        else:
            pytest.assume(actual > expected, message)
        logger.info(f"✓ 断言通过: {message}")

    def greater_equal(self, actual: Any, expected: Any, msg: str = None):
        """断言大于等于"""
        message = msg or f"预期 {actual} >= {expected}"
        if self.mode == AssertMode.STRICT:
            assert actual >= expected, message
        else:
            pytest.assume(actual >= expected, message)
        logger.info(f"✓ 断言通过: {message}")

    def less(self, actual: Any, expected: Any, msg: str = None):
        """断言小于"""
        message = msg or f"预期 {actual} < {expected}"
        if self.mode == AssertMode.STRICT:
            assert actual < expected, message
        else:
            pytest.assume(actual < expected, message)
        logger.info(f"✓ 断言通过: {message}")

    def less_equal(self, actual: Any, expected: Any, msg: str = None):
        """断言小于等于"""
        message = msg or f"预期 {actual} <= {expected}"
        if self.mode == AssertMode.STRICT:
            assert actual <= expected, message
        else:
            pytest.assume(actual <= expected, message)
        logger.info(f"✓ 断言通过: {message}")

    def match(self, text: str, pattern: str, msg: str = None):
        """断言正则匹配"""
        import re
        message = msg or f"预期 {text} 匹配模式 {pattern}"
        if self.mode == AssertMode.STRICT:
            assert re.search(pattern, text), message
        else:
            pytest.assume(re.search(pattern, text), message)
        logger.info(f"✓ 断言通过: {message}")

    def starts_with(self, text: str, prefix: str, msg: str = None):
        """断言以指定字符串开头"""
        message = msg or f"预期 {text} 以 {prefix} 开头"
        if self.mode == AssertMode.STRICT:
            assert text.startswith(prefix), message
        else:
            pytest.assume(text.startswith(prefix), message)
        logger.info(f"✓ 断言通过: {message}")

    def ends_with(self, text: str, suffix: str, msg: str = None):
        """断言以指定字符串结尾"""
        message = msg or f"预期 {text} 以 {suffix} 结尾"
        if self.mode == AssertMode.STRICT:
            assert text.endswith(suffix), message
        else:
            pytest.assume(text.endswith(suffix), message)
        logger.info(f"✓ 断言通过: {message}")

    def length(self, container: Any, expected_length: int, msg: str = None):
        """断言长度"""
        actual_length = len(container)
        message = msg or f"预期长度 {expected_length}, 实际长度 {actual_length}"
        if self.mode == AssertMode.STRICT:
            assert actual_length == expected_length, message
        else:
            pytest.assume(actual_length == expected_length, message)
        logger.info(f"✓ 断言通过: {message}")

    def instance_of(self, obj: Any, expected_type: type, msg: str = None):
        """断言类型"""
        message = msg or f"预期类型 {expected_type}, 实际类型 {type(obj)}"
        if self.mode == AssertMode.STRICT:
            assert isinstance(obj, expected_type), message
        else:
            pytest.assume(isinstance(obj, expected_type), message)
        logger.info(f"✓ 断言通过: {message}")


# 便捷函数
def strict_assert() -> SmartAssert:
    """创建严格断言实例（失败立即停止）"""
    return SmartAssert(mode=AssertMode.STRICT)


def soft_assert() -> SmartAssert:
    """创建软断言实例（收集所有失败）"""
    return SmartAssert(mode=AssertMode.SOFT)
