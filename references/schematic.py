"""
示意图生成工具（Graphviz DOT → PNG）
AI 只需编写 DOT 描述文本（结构化节点关系），不碰渲染参数。
底层自动处理：布局引擎、DPI、尺寸转换、物理尺寸校验。
"""

import os
import sys
import subprocess
import tempfile
import json

DOT_DPI = 300
DOUBLE_COL_CM = 16.9
SINGLE_COL_CM = 8.0


def _check_dot() -> bool:
    try:
        return subprocess.run(["which", "dot"], capture_output=True, text=True, timeout=5).returncode == 0
    except Exception:
        return False


def render_dot_to_png(dot_text: str, output_path: str,
                      column: str = "double", dpi: int = DOT_DPI) -> dict:
    """
    将 DOT 描述文本渲染为 PNG 图片。

    参数:
        dot_text: 完整的 DOT 描述文本（含 digraph 声明）
        output_path: 输出 PNG 路径
        column: "single"(8cm) / "double"(16.9cm)
        dpi: 输出分辨率

    返回: {"path": str, "width_cm": float, "height_cm": float, "dpi": int}
    """
    if not _check_dot():
        raise RuntimeError(
            "Graphviz (dot) 命令不可用。安装：\n"
            "  Ubuntu/Debian: sudo apt-get install graphviz\n"
            "  macOS: brew install graphviz\n"
            "  Windows: https://graphviz.org/download/"
        )

    w_inch = (SINGLE_COL_CM if column == "single" else DOUBLE_COL_CM) / 2.54

    with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
        f.write(dot_text)
        dot_path = f.name

    cmd = ["dot", "-Tpng", dot_path, "-o", output_path,
           f"-Gdpi={dpi}", f"-Gsize={w_inch},10"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        os.unlink(dot_path)
        raise RuntimeError(f"Graphviz 渲染失败: {result.stderr}")
    os.unlink(dot_path)

    from PIL import Image
    img = Image.open(output_path)
    w_cm = img.size[0] / dpi * 2.54
    h_cm = img.size[1] / dpi * 2.54
    return {"path": output_path, "width_cm": round(w_cm, 1),
            "height_cm": round(h_cm, 1), "dpi": dpi}


# ── DOT 编写辅助 ──────────────────────────────────────────

def make_dot_template(rankdir: str = "TB", splines: str = "ortho") -> str:
    """生成标准 DOT 模板框架"""
    return f'''digraph {{
    rankdir={rankdir}; splines={splines}; compound=true;
    bgcolor="white"; fontname="Noto Sans CJK SC";
    node [fontname="Noto Sans CJK SC", fontsize=9, shape=box, style="filled,rounded"];
    edge [color="#666666", penwidth=1.0];

    // ── 在此添加节点和边 ──

}}'''


# ── draw.io XML 辅助（可选） ─────────────────────────────

def make_drawio_xml(nodes: list, edges: list, page_w: int = 850, page_h: int = 1100) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<mxfile host="app.diagrams.net">',
        '  <diagram name="示意图" id="paper-diagram">',
        f'    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" pageWidth="{page_w}" pageHeight="{page_h}">',
        '      <root>',
        '        <mxCell id="0"/><mxCell id="1" parent="0"/>',
    ]
    for n in nodes:
        s = (f'rounded=1;whiteSpace=wrap;html=1;'
             f'fillColor={n.get("fill","#F0F0F0")};'
             f'strokeColor={n.get("stroke","#888888")};'
             f'{n.get("style","")}')
        lines.append(
            f'        <mxCell id="{n["id"]}" value="{n["label"]}" '
            f'style="{s}" parent="1" vertex="1">'
            f'<mxGeometry x="{n["x"]}" y="{n["y"]}" '
            f'width="{n["w"]}" height="{n["h"]}" as="geometry"/></mxCell>')
    for e in edges:
        s = f'edgeStyle=orthogonalEdgeStyle;endArrow=classic;html=1;rounded=1;{e.get("style","")}'
        lines.append(
            f'        <mxCell id="{e["id"]}" value="{e.get("label","")}" '
            f'style="{s}" parent="1" source="{e["source"]}" '
            f'target="{e["target"]}" edge="1">'
            f'<mxGeometry relative="1" as="geometry"/></mxCell>')
    lines.extend(['      </root>', '    </mxGraphModel>', '  </diagram>', '</mxfile>'])
    return '\n'.join(lines)


def save_drawio_xml(xml_content: str, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_content)


if __name__ == "__main__":
    if not _check_dot():
        print("Graphviz 未安装。")
        sys.exit(1)
    test_dot = '''digraph G {
        rankdir=TB; splines=ortho;
        node [shape=box, style="filled,rounded", fillcolor="#E8E8E8"];
        "输入层" -> "特征提取" -> "分类器" -> "输出";
    }'''
    result = render_dot_to_png(test_dot, "/tmp/test_schematic.png")
    print(json.dumps(result, ensure_ascii=False, indent=2))
