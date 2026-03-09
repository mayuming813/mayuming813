"""
数据一致性检查占位：链上数据与 API/DB 对比。
"""
import pytest

from utils.consistency import diff_dict, assert_consistent, normalize_hex_address


@pytest.mark.consistency
class TestConsistencyPlaceholder:
    """占位：后续根据业务补充链上 vs API 一致性用例。"""

    def test_diff_dict_no_change(self) -> None:
        a = {"balance": 100, "address": "0xAbc"}
        b = {"balance": 100, "address": "0xAbc"}
        d = diff_dict(a, b)
        assert not d, "无差异时 DeepDiff 应为 falsy"

    def test_diff_dict_detects_change(self) -> None:
        a = {"balance": 100}
        b = {"balance": 200}
        d = diff_dict(a, b)
        assert d, "有差异时 DeepDiff 应为 truthy"

    def test_assert_consistent_pass(self) -> None:
        assert_consistent({"x": 1}, {"x": 1})

    def test_assert_consistent_fail(self) -> None:
        with pytest.raises(AssertionError):
            assert_consistent({"x": 1}, {"x": 2}, msg="custom")

    def test_normalize_hex_address(self) -> None:
        data = {"from": "0xABC", "to": "0xDef"}
        out = normalize_hex_address(data)
        assert out["from"] == "0xabc"
        assert out["to"] == "0xdef"
