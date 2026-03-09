"""
数据一致性检查工具：链上数据与 API/DB 等对比。
"""
from typing import Any, Dict, List, Optional

from deepdiff import DeepDiff


def diff_dict(
    actual: Dict[str, Any],
    expected: Dict[str, Any],
    ignore_order: bool = False,
    exclude_paths: Optional[List[str]] = None,
) -> DeepDiff:
    """
    比较两个字典，返回 DeepDiff 结果。
    @param actual 实际数据
    @param expected 期望数据
    @param ignore_order 是否忽略列表顺序
    @param exclude_paths 排除的路径，如 ["root['timestamp']"]
    @return DeepDiff 实例，无差异时 bool(d) 为 False（兼容无 .totals 的 DeepDiff 版本）
    """
    return DeepDiff(
        expected,
        actual,
        ignore_order=ignore_order,
        exclude_paths=exclude_paths or [],
    )


def _has_differences(d: DeepDiff) -> bool:
    """是否有差异：兼容有 .totals 与无 .totals 的 DeepDiff 版本。"""
    if getattr(d, "totals", None):
        return bool(d.totals)
    return bool(d)


def assert_consistent(
    actual: Dict[str, Any],
    expected: Dict[str, Any],
    ignore_order: bool = False,
    exclude_paths: Optional[List[str]] = None,
    msg: str = "Data inconsistency",
) -> None:
    """
    断言两字典一致，否则抛出 AssertionError 并打印 diff。
    """
    d = diff_dict(actual, expected, ignore_order=ignore_order, exclude_paths=exclude_paths)
    if _has_differences(d):
        raise AssertionError(f"{msg}\n{d.pretty()}")


def normalize_hex_address(data: Dict[str, Any], keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    将字典中指定 key 的地址统一为小写（便于与 API 返回对比）。
    @param data 原始数据
    @param keys 要规范化的 key 列表，默认包含 'address','from','to','sender','receiver'
    """
    keys = keys or ["address", "from", "to", "sender", "receiver"]
    out = dict(data)
    for k in keys:
        if k in out and isinstance(out[k], str) and out[k].startswith("0x"):
            out[k] = out[k].lower()
    return out
