---
name: paper-figure-generator
description: 论文图表生成工具，覆盖统计图表（Python函数调用，AI只传结构化数据）、示意图（Graphviz函数调用渲染，AI只写DOT）、三线表（Python函数调用自动渲染为可出版级PNG）三类论文图表产出。当用户需要生成论文图表、统计图、示意图、三线表、学术图表、科研绘图、paper figure、scientific figure时使用。支持按论文期刊规范自动设置分辨率(300dpi)、字体(Arial 8-12pt)、尺寸(单栏8cm/双栏17cm)、色彩(RGB/色盲友好)等参数。
---

# 论文图表生成

## 概述

本技能用于生成符合学术论文出版规范的图表，覆盖三类产出：
- **统计图表**：折线图、柱状图、散点图、箱线图等（基于 matplotlib + SciencePlots）
- **示意图**：流程图、架构图、框架图、时间线等（基于 Graphviz DOT 语言渲染为 PNG，不依赖 GPU/浏览器/X11）
- **三线表**：Python 函数调用自动渲染为可出版级 PNG，AI 只传数据不写像素坐标

## 通用论文规范（所有图表必须遵循）

1. **分辨率**：≥300 dpi，线条图 600-1200 dpi
2. **格式**：矢量格式优先（PDF/SVG）；位图用 TIFF（LZW压缩），禁用 JPEG。三线表用 PNG 输出（16位灰度，300dpi）
3. **字体**：论文正文衬线字体优先（中文论文：Noto Serif CJK SC；英文论文：Arial/Computer Modern），所有字体必须嵌入
4. **颜色**：RGB 模式，色盲友好（避免红绿对比，用蓝橙替代）。经济学/社科论文默认灰度配色
5. **尺寸**：单栏 8-8.5cm（3.15-3.35in），双栏 17-17.8cm（6.69-7.0in）
6. **轴标签**：包含变量名和单位，如"时间 (s)"
7. **图例**：放在图内空白区域，不遮挡数据
8. **标记点**：优先用几何形状（○□△◇），不用颜色作为唯一区分

## 工作流程

### 第一步：理解需求

解析用户输入，提取：
1. **图表类型**：统计图 / 示意图 / 三线表 / 混合
2. **数据来源**：用户提供的数据（文本/表格/文件）或需要示例数据
3. **输出格式**：用户指定的格式，或在文件生成时使用默认格式
4. **期刊要求**：如有明确期刊（如 Nature / IEEE / Science），按对应模板调整

### 第二步：生成统计图表（函数调用）

适用场景：折线图、柱状图、散点图、箱线图、小提琴图、直方图

**核心原则**：AI 只传结构化的数据和图表类型，不碰任何 matplotlib 参数。底层自动处理样式、DPI、尺寸、字体、颜色方案、图例、误差线、标记形状等。

执行步骤：
1. 从用户数据中提取结构化信息，按图表类型组织成 data dict
2. 从 `main.py` 导入 `render_statistical_chart()`
3. 调用函数，传入 data dict 和 chart_type
4. 输出生成的图片路径和尺寸信息

```python
from main import render_statistical_chart

# 折线图示例
data = {
    "x": [0, 1, 2, 3, 4, 5],
    "y1": [0.1, 0.4, 0.9, 1.6, 2.5, 3.6],
    "y2": [0.2, 0.6, 1.2, 2.0, 3.0, 4.2]
}
result = render_statistical_chart(data, chart_type="line", style="science",
                                   column="double", output_path="chart.png",
                                   xlabel="时间 (s)", ylabel="幅值")

# 柱状图示例
data = {
    "categories": ["对照组", "实验组A", "实验组B", "实验组C"],
    "values": [12.3, 18.7, 25.1, 15.4],
    "errors": [1.2, 1.5, 2.0, 1.3]
}
result = render_statistical_chart(data, chart_type="bar", ...)
```

**data dict 格式说明**（按 chart_type）：

| chart_type | 必需字段 | 可选字段 |
|-----------|---------|---------|
| line | x, y1[, y2, y3...] | — |
| bar | categories, values | errors |
| scatter | x, y | — |
| box | data, labels | — |
| hist | data | bins |
| violin | data, labels | — |

样式选择指南：
- `science`：通用学术风格（默认）
- `ieee`：IEEE 期刊（双栏紧凑）
- `nature`：Nature 风格（简洁，无网格）
- `high-vis`：高对比度，适合展示/PPT

### 第三步：生成示意图（函数调用）

适用场景：框架图、流程图、架构图、时间线、模型结构图、层级结构图

**核心原则**：AI 只需编写 DOT 描述语言（结构化节点关系描述），调用 `render_dot_to_png()` 即可完成渲染。Graphviz 是矢量渲染引擎，不依赖 GPU/浏览器/X11。底层自动处理：graphviz 安装检查、尺寸转换、DPI、渲染、物理尺寸校验。

执行步骤：
1. 编写 DOT 描述文本（描述节点、边、分组、方向）
2. 导入 `render_dot_to_png()` 并调用
3. 输出生成的图片路径和尺寸信息

```python
from main import render_dot_to_png

dot_text = '''
digraph 模型架构 {
    rankdir=TB; splines=ortho; compound=true;
    bgcolor="white"; fontname="Noto Sans CJK SC";
    node [fontname="Noto Sans CJK SC", fontsize=9, shape=box, style="filled,rounded"];
    edge [color="#666666", penwidth=1.0];

    input [label="输入层", fillcolor="#F0F0F0"];
    feat [label="特征提取", fillcolor="#E0E0E0"];
    cls [label="分类器", fillcolor="#E0E0E0"];
    output [label="输出", fillcolor="#CCCCCC"];

    input -> feat -> cls -> output;
}
'''

result = render_dot_to_png(dot_text, "diagram.png", column="double")
print(f'{result["width_cm"]:.1f}x{result["height_cm"]:.1f}cm @{result["dpi"]}dpi')
```

**DOT 编写参考：**

| 配置 | 选项 | 说明 |
|------|------|------|
| `rankdir` | TB / LR | 自上而下 / 自左向右 |
| `splines` | ortho / curved / polyline | 连线风格 |
| `compound` | true | 允许子图间连线 |

**灰度配色规范（经济学/社科默认）：**

| 层级 | 填充色 | 边框色 | 用途 |
|------|--------|--------|------|
| 最浅 | #F8F8F8 | #AAAAAA | 背景/外部输入 |
| 浅 | #F0F0F0 | #888888 | 初级节点 |
| 中浅 | #E8E8E8 | #777777 | 二级节点 |
| 中 | #E0E0E0 | #666666 | 核心节点 |
| 中深 | #D8D8D8 | #555555 | 重要节点 |
| 深 | #CCCCCC | #333333 | 强调节点/终点 |

子图分组用 `subgraph cluster_xxx {}`，核心分组用 style=solid，次要分组用 style=dashed。
节点内换行使用 HTML-like label：`label=<行1<br/>行2>`

### 第四步：生成三线表（Python 函数调用）

**核心原则**：AI 只传表格数据和格式参数（表头、数据行、注释、宽度），不碰任何底层实现——不做像素坐标、不写 HTML 标签、不调 CSS。渲染引擎自动完成排版。

**适用场景**：实验结果表、数据汇总表、对比分析表、统计描述表、政策任务分工表等

#### 4.1 调用方式

把 `references/gen_three_line_table_v2.py` 复制到工作目录，修改其中的数据和参数后直接运行：

```python
# 1. 复制脚本到工作目录
import shutil
shutil.copy('skills/paper-figure-generator/references/gen_three_line_table_v2.py', './gen_three_line.py')

# 2. 编辑数据（只改数据，不改渲染逻辑）
rows_data = [
    ('第一类\n（N项）', '任务1<br/>任务2<br/>任务3'),
    ('第二类\n（N项）', '任务A<br/>任务B'),
]

note_text = '注：说明文字'

# 3. 运行
exec(open('./gen_three_line.py', encoding='utf-8').read())
```

**实际使用中**，直接把 `gen_three_line_table_v2.py` 复制到工作目录，修改 `rows_data`、`note_text` 和 `TABLE_W_CM` 三个变量即可。不需要修改其他任何代码。

**传入参数说明：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `rows_data` | 表格数据，每项为(第一列文本, 第二列文本)的元组。第二列多行用 `<br/>` 分隔 | 必填 |
| `note_text` | 表注文本 | 必填 |
| `TABLE_W_CM` | 表格宽度（cm），单栏=8.0，双栏=17.0 | 17.0 |
| `FONT_PATH` | 中文字体路径 | NotoSerifCJK-Regular.ttc |
| `output_path` | 输出 PNG 路径 | 自动生成 |

#### 4.2 输出

脚本自动完成：
1. 构建表格 HTML（内部自动完成，AI 不碰）
2. WeasyPrint 渲染为 PDF
3. pdftoppm 转为 300dpi PNG
4. PIL 自动裁剪白边
5. 输出最终图片路径 + 尺寸校验结果

#### 4.3 渲染规范（AI 不需要管，引擎自动处理）

渲染引擎内部固定使用以下规范（记录在此供排查问题用，运行时不需手动配置）：

**三线规则：** 顶线 1.5pt / 表头线 1.0pt / 底线 1.5pt，仅三条横线，无竖线
**字体：** 中文 Noto Serif CJK SC（衬线），表头加粗；英文 Arial
**字号：** 正文 9pt，注释 7.5pt
**列对齐：** 第一列居中（19%宽度），第二列左对齐（81%宽度）
**行高：** 1.4 倍
**间距：** 顶线到表头文字 ≈ 底线到最后文字（视觉对称）
**注释：** 紧随表格下方，7.5pt，两端对齐，CSS 自动换行

#### 4.4 失败处理
- WeasyPrint / pdftoppm 未安装：自动安装
- 字体加载失败：回退到 Noto Sans CJK SC
- 生成后校验宽度：误差 < 0.2cm

### 第五步：输出与交付

1. **统计图表**：输出 `.png` 图像文件路径，同时说明尺寸、分辨率、样式
2. **示意图**：输出 `.png` 图片文件路径，说明尺寸、分辨率、配色方案
3. **三线表**：输出裁剪后的 `.png` 图片文件路径，标注尺寸（宽×高 cm @300dpi）、字体、线宽参数，供用户核验
4. 每次生成后，简要标注关键格式参数以供用户核验
5. 三线表产出后自动上传到项目文件系统

## 示例场景

### 示例 1：生成论文折线图
> 用户："用示例数据生成一张折线图，对比两组实验结果"
> 输出：science样式折线图，x轴"时间 (s)"，y轴"幅值"，300dpi，单栏宽度

### 示例 2：生成示意图
> 用户："画一个简单的模型架构图：输入→特征提取→分类器→输出"
> 输出：标准 PNG 图片，16.9cm宽，300dpi，灰度配色，4节点+3箭头

### 示例 3：生成三线表
> 用户："把这几组实验数据做成三线表：方法A 85.2±1.3, 方法B 91.5±0.8, 方法C 88.7±1.1"
> 输出：gen_three_line_table_v2.py 调用 → PNG，17.0cm 双栏宽，300dpi，标准三线表

## 边界情况处理

- **数据量过大**（>10000点）：随机采样或聚合后再绘图，标注采样方法
- **缺失数据**：在图中标注缺失区域，用虚线连接
- **负值数据**：柱状图用不同颜色区分正负
- **用户无数据**：使用 `generate_sample_data()` 生成示例数据，标注"示例数据"
- **SciencePlots / graphviz / WeasyPrint / pdftoppm 未安装**：各函数内部自动安装，无需手动处理
- **期刊要求不明确**：默认使用通用学术规范（science样式，单栏）
- **三线表字体加载失败**：自动回退到 Noto Sans CJK SC
- **DOT 语法错误**：检查括号和引号是否闭合；Graphviz 会报告具体错误行号
- **经济学/社科论文**：默认灰度配色方案；用户明确要求彩色时使用低饱和度配色
- **渲染后尺寸过大**：超过 A4 页面高度（27cm）时改用横向布局（rankdir=LR）
- **三线表产出尺寸校验**：gen_three_line_table_v2.py 自动完成，误差 < 0.2cm

## 注意事项

- 所有图表文件生成在 Agent 工作目录下，文件名带时间戳和图表类型标识
- 不要猜测期刊格式要求——如果用户未指定期刊，使用通用规范
- 三线表**禁止使用 matplotlib text() 手搓像素坐标**（用户明确反对此方案），统一使用 gen_three_line_table_v2.py 的函数调用方案
- 三线表严格遵守三条横线规则（顶线 1.5pt / 表头线 1.0pt / 底线 1.5pt），不加竖线
- 示意图使用论文友好的灰度配色（经济学/社科默认）或低饱和度彩色配色
- 示意图渲染依赖本地 `dot` 命令（Graphviz），无需 GPU/浏览器/X11
- 涉及中文的 DOT 描述必须指定 fontname="Noto Sans CJK SC"，英文内容使用 Arial
