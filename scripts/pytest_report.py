"""
根据 junit.xml 生成 summary.txt，汇总失败与跳过用例及原因。
供 run_unit_tests / run_api_tests / run_ui_tests 复用。
"""
import xml.etree.ElementTree as ET
from pathlib import Path


def write_summary(junit_path: Path, summary_path: Path, title: str = "测试报告") -> None:
    """
    解析 junit.xml，写入 summary.txt。
    :param junit_path: junit.xml 路径
    :param summary_path: 输出的 summary.txt 路径
    :param title: 报告标题，如 "单元测试报告"
    """
    if not junit_path.exists():
        return
    try:
        tree = ET.parse(junit_path)
        root = tree.getroot()
        suite = root.find("testsuite") if root.tag == "testsuites" else root
        if suite is None:
            return
        total = int(suite.get("tests", 0))
        failures_count = int(suite.get("failures", 0))
        skipped_count = int(suite.get("skipped", 0))
        passed = total - failures_count - skipped_count

        lines = [
            f"============ {title} ============",
            f"总计: {total}  通过: {passed}  失败: {failures_count}  跳过: {skipped_count}",
            "",
        ]
        for tc in suite.findall("testcase"):
            name = tc.get("name", "")
            failure = tc.find("failure")
            skip = tc.find("skipped")
            if failure is not None:
                msg = (failure.text or failure.get("message", "")).strip()
                msg_first = msg.split("\n")[0] if msg else ""
                lines.append(f"[失败] {name}")
                lines.append(f"  原因: {msg_first}")
                lines.append("")
            elif skip is not None:
                msg = skip.get("message", "").strip()
                lines.append(f"[跳过] {name}")
                lines.append(f"  原因: {msg}")
                lines.append("")

        if failures_count == 0 and skipped_count == 0:
            lines.append("全部通过，无失败与跳过。")
        summary_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass
