#!/usr/bin/env python3
"""
将 马玉铭-简历-优化版.md 转为 .docx（纯 zip + OOXML，不依赖 python-docx）。
运行：python scripts/build_resume_docx.py
输出：马玉铭-简历-优化版.docx
"""
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "马玉铭-简历-优化版.md"
DOCX_PATH = ROOT / "马玉铭-简历-优化版.docx"

# 转义 XML 文本
def esc(t):
    if not t:
        return ""
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", str(t))  # 去掉 ** 保留内容
    return (
        t.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def parse_md_to_body(md_text):
    """简单解析 md：标题、段落、表格、列表 -> OOXML body 片段列表。"""
    lines = md_text.replace("\r\n", "\n").split("\n")
    fragments = []
    i = 0

    def w_p(text, bold=False):
        if bold:
            return f'<w:p><w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
        return f'<w:p><w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'

    def w_p_empty():
        return "<w:p/>"

    def w_heading(level, text):
        return f'<w:p><w:pPr><w:pStyle w:val="Heading{level}"/></w:pPr><w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'

    def w_table(rows):
        # rows: list of list of str (cell text)
        if not rows:
            return ""
        ncol = max(len(r) for r in rows)
        grid = "".join(['<w:gridCol w:w="3000"/>'] * ncol)
        trs = []
        for row in rows:
            tcs = "".join(
                f'<w:tc><w:tcPr><w:tcW w:w="3000" w:type="dxa"/></w:tcPr><w:p><w:r><w:t xml:space="preserve">{esc(cell)}</w:t></w:r></w:p></w:tc>'
                for cell in row
            )
            trs.append(f"<w:tr>{tcs}</w:tr>")
        return f'<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(trs)}</w:tbl>'

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 一级标题 # xxx
        if stripped.startswith("# ") and not stripped.startswith("## "):
            fragments.append(w_heading(1, stripped[2:].strip()))
            i += 1
            continue

        # 二级标题 ## xxx
        if stripped.startswith("## "):
            fragments.append(w_heading(2, stripped[3:].strip()))
            i += 1
            continue

        # 三级标题 ### xxx
        if stripped.startswith("### "):
            fragments.append(w_heading(3, stripped[4:].strip()))
            i += 1
            continue

        # 表格：| a | b |
        if stripped.startswith("|") and "|" in stripped:
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw = lines[i].strip()
                if re.match(r"^\|[-:\s|]+\|$", raw):  # 分隔行
                    i += 1
                    continue
                cells = [c.strip() for c in raw.split("|")[1:-1]]
                if cells:
                    table_rows.append(cells)
                i += 1
            if table_rows:
                fragments.append(w_table(table_rows))
            continue

        # 引用 > xxx
        if stripped.startswith("> "):
            fragments.append(w_p(stripped[2:].strip()))
            i += 1
            continue

        # 空行
        if not stripped:
            fragments.append(w_p_empty())
            i += 1
            continue

        # 列表 - 或 *
        if stripped.startswith("- ") or stripped.startswith("* "):
            fragments.append(w_p("• " + stripped[2:].strip()))
            i += 1
            continue

        # 数字列表
        if re.match(r"^\d+\.\s", stripped):
            fragments.append(w_p(stripped))
            i += 1
            continue

        # 普通段落（esc 内会去 **）
        fragments.append(w_p(stripped))
        i += 1

    return fragments


def make_document_xml(body_fragments):
    body_inner = "".join(body_fragments)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body_inner}
    <w:p><w:r><w:t></w:t></w:r></w:p>
  </w:body>
</w:document>"""


def main():
    md_text = MD_PATH.read_text(encoding="utf-8")
    # 去掉说明行（> 使用说明）
    md_text = re.sub(r"\n> 使用说明.*?\n", "\n", md_text, flags=re.DOTALL)
    md_text = re.sub(r"\n---\n", "\n", md_text)

    fragments = parse_md_to_body(md_text)
    document_xml = make_document_xml(fragments)

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

    core = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties">
  <dc:title>马玉铭-简历</dc:title>
  <dc:creator>马玉铭</dc:creator>
</cp:coreProperties>"""

    app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Application>Python</Application>
</Properties>"""

    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:styleId="Heading1" w:default="0"><w:name w:val="Heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:sz w:val="28"/><w:szCs w:val="28"/></w:pPr><w:rPr><w:b/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2" w:default="0"><w:name w:val="Heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:sz w:val="24"/><w:szCs w:val="24"/></w:pPr><w:rPr><w:b/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3" w:default="0"><w:name w:val="Heading 3"/><w:basedOn w:val="Normal"/><w:pPr><w:sz w:val="22"/></w:pPr><w:rPr><w:b/></w:rPr></w:style>
</w:styles>"""

    with zipfile.ZipFile(DOCX_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        z.writestr("word/styles.xml", styles)

    print(f"已生成：{DOCX_PATH}")


if __name__ == "__main__":
    main()
