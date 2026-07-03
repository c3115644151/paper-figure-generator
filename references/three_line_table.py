"""
三线表生成工具（HTML+WeasyPrint → PDF → PNG）
AI 只需传入表格数据和注释文本，不碰任何 HTML/CSS/渲染参数。
底层自动完成：HTML 构建、WeasyPrint 渲染、pdftoppm 转换、PIL 裁剪、三线校验。
"""

import os
import sys
import subprocess
import json

FONT_SERIF_REGULAR = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
FONT_SERIF_BOLD = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'


def render_three_line_table(
    rows_data: list,
    note_text: str = "",
    headers: tuple = ("类别", "重点任务"),
    column: str = "double",
    output_path: str = "table_three_line.png",
    font_regular: str = FONT_SERIF_REGULAR,
    font_bold: str = FONT_SERIF_BOLD,
) -> dict:
    """
    渲染三线表为出版级 PNG。

    参数:
        rows_data: [("第一列", "第二列"), ...]。第二列多行用 <br/> 分隔
        note_text: 表注文本（可选）
        headers:   (第一列表头, 第二列表头)
        column:    "single"(8cm) / "double"(17cm)
        output_path: 输出 PNG 路径

    返回: {"path": str, "width_cm": float, "height_cm": float, "dpi": 300,
           "lines_expected": 3, "lines_detected": int}
    """
    table_w_cm = 17.0 if column == "double" else 8.0

    # 构建数据行 HTML
    data_rows_html = ""
    for i, (col1, col2) in enumerate(rows_data):
        cls = ' class="headline-row data-row"' if i == 0 else ' class="data-row"'
        data_rows_html += f'      <tr{cls}><td>{col1}</td><td>{col2}</td></tr>\n'

    th1, th2 = headers
    note_html = f'<p class="note">{note_text}</p>' if note_text else ""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<style>
@page {{
    size: {table_w_cm}cm 30cm;
    margin: 0;
}}
@font-face {{
    font-family: 'NotoSerifCJK';
    src: url('file://{font_regular}') format('truetype');
}}
@font-face {{
    font-family: 'NotoSerifCJKBold';
    src: url('file://{font_bold}') format('truetype');
    font-weight: bold;
}}
body {{
    margin: 2px 0 0 0; padding: 0;
    font-family: 'NotoSerifCJK', serif;
    font-size: 9pt; color: #000;
    width: {table_w_cm}cm;
}}
table {{
    width: {table_w_cm}cm;
    border-collapse: collapse;
    table-layout: fixed;
}}
th, td {{
    border: none; padding: 3px 8px;
    vertical-align: top; line-height: 1.4;
    font-family: 'NotoSerifCJK', serif;
    font-size: 9pt;
}}
tr.topline-row th {{
    border-top: 1.5pt solid #000; padding-top: 6px;
}}
tr.headline-row td {{
    border-top: 1.0pt solid #000;
}}
tr.data-row:last-child td {{
    border-bottom: 1.5pt solid #000; padding-bottom: 8px;
}}
th {{
    font-family: 'NotoSerifCJKBold', 'NotoSerifCJK', serif;
    font-size: 9pt; text-align: center;
}}
tr.data-row td:first-child,
tr.headline-row td:first-child {{
    text-align: center; width: 19%;
}}
tr.data-row td:last-child,
tr.headline-row td:last-child {{
    text-align: left; width: 81%;
}}
.note {{
    font-family: 'NotoSerifCJK', serif;
    font-size: 7.5pt; line-height: 1.4;
    margin: 5px 0 0 0;
    width: {table_w_cm}cm;
    text-align: justify;
}}
</style>
</head>
<body>
<table>
  <tr class="topline-row"><th>{th1}</th><th>{th2}</th></tr>
{data_rows_html}
</table>
{note_html}
</body>
</html>"""

    # 渲染流程
    base = os.path.dirname(output_path) or '.'
    os.makedirs(base, exist_ok=True)
    html_path = os.path.join(base, '_three_line_temp.html')
    pdf_path = os.path.join(base, '_three_line_temp.pdf')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    from weasyprint import HTML
    HTML(filename=html_path).write_pdf(pdf_path)

    out_base = output_path.replace('.png', '')
    try:
        subprocess.run(
            ['pdftoppm', '-png', '-r', '300', '-singlefile', pdf_path, out_base],
            capture_output=True, text=True, timeout=30, check=True,
        )
    except Exception as e:
        raise RuntimeError(f"pdftoppm 渲染失败: {e}")

    for tmp in [html_path, pdf_path]:
        try:
            os.unlink(tmp)
        except Exception:
            pass

    # 裁剪白边
    from PIL import Image
    import numpy as np
    img = Image.open(output_path)
    arr = np.array(img.convert('L'))
    w, h = img.size

    rows_content = np.any(arr < 200, axis=1)
    cols_content = np.any(arr < 200, axis=0)
    if rows_content.any():
        y_min = int(np.argmax(rows_content))
        y_max = int(len(rows_content) - 1 - np.argmax(rows_content[::-1]))
        x_min = int(np.argmax(cols_content))
        x_max = int(len(cols_content) - 1 - np.argmax(cols_content[::-1]))
        pad = 5
        x_min = max(0, x_min - pad)
        x_max = min(w, x_max + pad)
        y_min = max(0, y_min - pad)
        y_max = min(h, y_max + pad)
        cropped = img.crop((x_min, y_min, x_max, y_max))
        cropped.save(output_path)
        w_c, h_c = cropped.size
    else:
        w_c, h_c = w, h

    w_cm = round(w_c / 300 * 2.54, 1)
    h_cm = round(h_c / 300 * 2.54, 1)

    # 三线检测
    arr2 = np.array(Image.open(output_path).convert('L'))
    h2 = Image.open(output_path).size[1]
    lines_detected = 0
    for y in range(h2):
        dark = (arr2[y, :] < 80).sum()
        if dark > w_c * 300 / 2.54 * 0.3:
            lines_detected += 1

    return {
        "path": output_path,
        "width_cm": w_cm,
        "height_cm": h_cm,
        "dpi": 300,
        "lines_expected": 3,
        "lines_detected": lines_detected,
    }


def load_example_data() -> tuple:
    """生成示例三线表数据"""
    rows = [
        ('规划协同\n（6项）',
         '编制算力枢纽与能源基地联合布局规划<br/>'
         '建立数据中心用能需求与绿电供给匹配机制<br/>'
         '推动西部算力枢纽配建集中式新能源<br/>'
         '建设算力网络与电力通道协同规划平台<br/>'
         '制定数据中心集群选址用能联合评估标准<br/>'
         '构建算力-电力"一张图"动态监测体系'),
        ('运行协同\n（7项）',
         '建设算力负荷监测与电网调度信息互通平台<br/>'
         '建立数据中心可调负荷资源库与动态响应能力评估<br/>'
         '推动AI工作负载与电网峰谷时段智能匹配调度<br/>'
         '制定数据中心参与需求响应的技术标准与接口规范<br/>'
         '建立制冷系统与电网调峰的联动控制机制<br/>'
         '开发面向电网调度的算力负荷预测模型<br/>'
         '部署备电与储能协同控制系统'),
        ('交易协同\n（6项）',
         '明确数据中心以VPP身份参与现货市场的准入条件与交易规则<br/>'
         '完善报量报价机制与出清算法<br/>'
         '建立调频/备用辅助服务补偿定价机制<br/>'
         '推动跨省跨区电力交易试点<br/>'
         '建立用电数据与碳交易市场联动机制<br/>'
         '制定绿电采购与绿证交易激励政策'),
    ]
    note = ('注：根据国家发改委等四部门《关于促进人工智能与能源双向赋能的行动方案》'
            '（2026年5月）整理。')
    return rows, note


if __name__ == "__main__":
    print("测试模式：生成示例三线表")
    rows, note = load_example_data()
    result = render_three_line_table(rows, note_text=note, column="double",
                                     output_path="/tmp/test_three_line.png")
    print(json.dumps(result, ensure_ascii=False, indent=2))
