#!/usr/bin/env python3
"""
三线表生成（HTML+CSS 结构化方案 v2）
工作流：HTML（结构化描述）→ WeasyPrint PDF → pdftoppm PNG → PIL裁剪
完全不用手搓像素坐标，AI 只写表格结构和样式参数。
"""

import subprocess
import os
from weasyprint import HTML

FONT_PATH = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
FONT_BOLD_PATH = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
OUTPUT = '/app/data/所有对话/主对话/table1_three_line.png'
TABLE_W_CM = 17.0

rows_data = [
    ('规划协同<br/>（6项）',
     '编制算力枢纽与能源基地联合布局规划<br/>'
     '建立数据中心用能需求与绿电供给匹配机制<br/>'
     '推动西部算力枢纽配建集中式新能源<br/>'
     '建设算力网络与电力通道协同规划平台<br/>'
     '制定数据中心集群选址用能联合评估标准<br/>'
     '构建算力-电力"一张图"动态监测体系'),
    ('运行协同<br/>（7项）',
     '建设算力负荷监测与电网调度信息互通平台<br/>'
     '建立数据中心可调负荷资源库与动态响应能力评估<br/>'
     '推动AI工作负载与电网峰谷时段智能匹配调度<br/>'
     '制定数据中心参与需求响应的技术标准与接口规范<br/>'
     '建立制冷系统与电网调峰的联动控制机制<br/>'
     '开发面向电网调度的算力负荷预测模型<br/>'
     '部署备电与储能协同控制系统'),
    ('交易协同<br/>（6项）',
     '明确数据中心以VPP身份参与现货市场的准入条件与交易规则<br/>'
     '完善报量报价机制与出清算法<br/>'
     '建立调频/备用辅助服务补偿定价机制<br/>'
     '推动跨省跨区电力交易试点<br/>'
     '建立用电数据与碳交易市场联动机制<br/>'
     '制定绿电采购与绿证交易激励政策'),
]

note_text = ('注：根据国家发改委等四部门《关于促进人工智能与能源双向赋能的行动方案》'
             '（2026年5月）整理，原方案部署29项重点任务，'
             '本表选取其中具有代表性的19项按三类协同维度归类。')

# ── 构建数据行 ──
data_rows_html = ''
for i, (cat, tasks) in enumerate(rows_data):
    cls = ' class="headline-row data-row"' if i == 0 else ' class="data-row"'
    data_rows_html += f'      <tr{cls}><td>{cat}</td><td>{tasks}</td></tr>\n'

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<style>
@page {{
    size: {TABLE_W_CM}cm 30cm;
    margin: 0;
}}
@font-face {{
    font-family: 'NotoSerifCJK';
    src: url('file://{FONT_PATH}') format('truetype');
}}
@font-face {{
    font-family: 'NotoSerifCJKBold';
    src: url('file://{FONT_BOLD_PATH}') format('truetype');
    font-weight: bold;
}}
body {{
    margin: 2px 0 0 0;
    padding: 0;
    font-family: 'NotoSerifCJK', serif;
    font-size: 9pt;
    color: #000;
    width: {TABLE_W_CM}cm;
}}
table {{
    width: {TABLE_W_CM}cm;
    border-collapse: collapse;
    table-layout: fixed;
}}

/* 三线表核心：仅三条横线 */
th, td {{
    border: none;
    padding: 3px 8px;
    vertical-align: top;
    line-height: 1.4;
    font-family: 'NotoSerifCJK', serif;
    font-size: 9pt;
}}

/* 顶线：表头行顶部 */
tr.topline-row th {{
    border-top: 1.5pt solid #000;
    padding-top: 6px;
}}

/* 表头线：第一个数据行顶部 */
tr.headline-row td {{
    border-top: 1.0pt solid #000;
}}

/* 底线：最后一行数据底部 */
tr.data-row:last-child td {{
    border-bottom: 1.5pt solid #000;
    padding-bottom: 8px;
}}

/* 表头样式 */
th {{
    font-family: 'NotoSerifCJKBold', 'NotoSerifCJK', serif;
    font-size: 9pt;
    text-align: center;
}}

/* 第一列居中，第二列左对齐 */
tr.data-row td:first-child,
tr.headline-row td:first-child {{
    text-align: center;
    width: 19%;
}}
tr.data-row td:last-child,
tr.headline-row td:last-child {{
    text-align: left;
    width: 81%;
}}

/* 注释 */
.note {{
    font-family: 'NotoSerifCJK', serif;
    font-size: 7.5pt;
    line-height: 1.4;
    margin: 5px 0 0 0;
    width: {TABLE_W_CM}cm;
    text-align: justify;
}}
</style>
</head>
<body>
<table>
  <tr class="topline-row"><th>类别</th><th>重点任务</th></tr>
{data_rows_html}
</table>
<p class="note">{note_text}</p>
</body>
</html>'''

# ── HTML → PDF (WeasyPrint) ──
html_path = '/app/data/所有对话/主对话/table1_three_line.html'
pdf_path = '/app/data/所有对话/主对话/table1_three_line.pdf'

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

HTML(filename=html_path).write_pdf(pdf_path)
print(f'PDF: {pdf_path}')

# ── PDF → PNG (pdftoppm 300dpi) ──
out_base = OUTPUT.replace('.png', '')
subprocess.run([
    'pdftoppm', '-png', '-r', '300',
    '-singlefile',
    pdf_path, out_base
], capture_output=True, text=True)

# ── 裁剪白边并验证 ──
from PIL import Image
import numpy as np

img = Image.open(OUTPUT)
arr = np.array(img.convert('L'))
w, h = img.size

# 自动裁剪内容区
rows_has_content = np.any(arr < 200, axis=1)
cols_has_content = np.any(arr < 200, axis=0)
if rows_has_content.any():
    y_min = int(np.argmax(rows_has_content))
    y_max = int(len(rows_has_content) - 1 - np.argmax(rows_has_content[::-1]))
    x_min = int(np.argmax(cols_has_content))
    x_max = int(len(cols_has_content) - 1 - np.argmax(cols_has_content[::-1]))
    # 保留边距（不裁到文字）
    pad = 5
    x_min = max(0, x_min - pad)
    x_max = min(w, x_max + pad)
    y_min = max(0, y_min - pad)
    y_max = min(h, y_max + pad)
    cropped = img.crop((x_min, y_min, x_max, y_max))
    cropped.save(OUTPUT)
    w_c, h_c = cropped.size
    print(f'Cropped: {w_c}x{h_c} = {w_c/300*2.54:.1f}x{h_c/300*2.54:.1f}cm @300dpi')
else:
    w_c, h_c = w, h
    print(f'No content found, keeping original: {w_c}x{h_c}')

# ── 三线检测 ──
arr = np.array(Image.open(OUTPUT).convert('L'))
w2, h2 = Image.open(OUTPUT).size
print(f'\nFinal: {w2}x{h2} = {w2/300*2.54:.1f}x{h2/300*2.54:.1f}cm')
print('Thick lines (>30% width, dark<80):')
prev = -999
for y in range(h2):
    dark = (arr[y,:] < 80).sum()
    if dark > w2 * 0.3 and y - prev > 2:
        print(f'  y={y} ({100*y/h2:.0f}%): {dark}px')
        prev = y

print('\nNote rightmost boundary:')
for y in range(h2):
    dark_cols = np.where(arr[y,:] < 150)[0]
    if len(dark_cols) > 5:
        rightmost = dark_cols.max()
        if rightmost < w2 - 2:
            print(f'  y={y}: text rightmost x={rightmost}/{w2} ({100*rightmost/w2:.1f}%)')
            break
