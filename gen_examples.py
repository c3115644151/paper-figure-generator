"""
示例产出生成脚本 v11
生成全部统计图 + 示意图 + 三线表 PNG 示例
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from main import *
import pandas as pd
import numpy as np

OUT = "/app/data/所有对话/主对话/技能示例输出"
os.makedirs(OUT, exist_ok=True)
try_install_scienceplots()

def gen_stats():
    """生成 11 种统计图表"""
    np.random.seed(42)
    print("=== 统计图表 ===")
    
    # 1. 折线图
    x = np.linspace(0, 10, 60)
    data = {"x": x,
            "y1": 1.5*np.exp(-0.3*x)*np.sin(2*x)+0.5,
            "y2": 1.5*np.exp(-0.25*x)*np.sin(2*x+0.5)+0.3,
            "y3": 1.0*np.exp(-0.2*x)*np.cos(1.5*x)+0.8,
            "xlabel": "Time (s)", "ylabel": "Response",
            "labels": ["Control", "Treatment A", "Treatment B"]}
    p = generate_line_chart(data, output_path=f"{OUT}/line_chart.png")
    print(f"  line_chart: {p}")
    
    # 2. 柱状图
    data = {"categories": ["Control", "Method A", "Method B", "Method C"],
            "values": [12.3, 18.7, 25.1, 15.4],
            "errors": [1.2, 1.5, 2.0, 1.3],
            "ylabel": "Accuracy (%)"}
    p = generate_bar_chart(data, output_path=f"{OUT}/bar_chart.png")
    print(f"  bar_chart: {p}")
    
    # 3. 散点图
    x = np.random.uniform(0, 10, 35)
    y = 2.5 * x + 1 + np.random.randn(35) * 1.0
    data = {"x": x, "y": y, "xlabel": "Feature X", "ylabel": "Observation Y"}
    p = generate_scatter_chart(data, output_path=f"{OUT}/scatter_chart.png")
    print(f"  scatter_chart: {p}")
    
    # 4. 箱线图
    data = {"groups": [np.random.normal(m, s, 30) for m,s in
                       [(5.0,0.6),(6.5,0.5),(4.2,0.7),(7.8,0.4)]],
            "labels": ["Model A", "Model B", "Model C", "Model D"]}
    p = generate_box_chart(data, output_path=f"{OUT}/box_chart.png")
    print(f"  box_chart: {p}")
    
    # 5. 小提琴图
    data = {"groups": [np.random.normal(m, s, 50) for m,s in
                       [(5.0,0.8),(6.5,0.6),(4.2,1.0),(7.8,0.5)]],
            "labels": ["Model A", "Model B", "Model C", "Model D"]}
    p = generate_violin_chart(data, output_path=f"{OUT}/violin_chart.png")
    print(f"  violin_chart: {p}")
    
    # 6. 直方图
    data = {"values": np.random.normal(5.0, 1.2, 200),
            "xlabel": "Measurement", "ylabel": "Frequency"}
    p = generate_histogram(data, output_path=f"{OUT}/histogram.png")
    print(f"  histogram: {p}")
    
    # 7. 热力图
    n = 6
    labels = [f"F{i+1}" for i in range(n)]
    cov = np.random.uniform(-0.3, 0.8, (n, n))
    cov = (cov + cov.T) / 2
    np.fill_diagonal(cov, 1.0)
    data = {"matrix": cov, "labels": labels, "title": "Correlation Matrix"}
    p = generate_heatmap(data, output_path=f"{OUT}/heatmap.png")
    print(f"  heatmap: {p}")
    
    # 8. 分组柱状图
    data = {"categories": ["Dataset A", "Dataset B", "Dataset C"],
            "groups": [
                {"label": "Method 1", "values": [85, 72, 91], "errors": [3,4,3]},
                {"label": "Method 2", "values": [78, 88, 75], "errors": [4,3,4]},
            ],
            "ylabel": "F1 Score (%)"}
    p = generate_paired_bar(data, output_path=f"{OUT}/paired_bar.png")
    print(f"  paired_bar: {p}")
    
    # 9. 面积图
    x = np.linspace(0, 10, 50)
    data = {"x": x,
            "y1": 2 + 0.5*np.sin(x) + 0.2*np.random.randn(50),
            "y2": 1.5 + 0.3*np.cos(x*0.8) + 0.15*np.random.randn(50),
            "y3": 1.0 + 0.4*np.sin(x*1.2) + 0.1*np.random.randn(50),
            "xlabel": "Time (epoch)", "ylabel": "Cumulative Value",
            "labels": ["Component A", "Component B", "Component C"]}
    p = generate_area_chart(data, output_path=f"{OUT}/area_chart.png")
    print(f"  area_chart: {p}")
    
    # 10. 误差棒图
    data = {"conditions": ["Baseline", "Low", "Medium", "High"],
            "means": [10.0, 12.5, 18.3, 15.1],
            "sems": [0.8, 1.2, 1.5, 1.1],
            "ylabel": "Performance"}
    p = generate_errorbar_chart(data, output_path=f"{OUT}/errorbar_chart.png")
    print(f"  errorbar_chart: {p}")
    
    # 11. 多面板组合
    p = generate_panel_chart(output_path=f"{OUT}/panel_chart.png")
    print(f"  panel_chart: {p}")


def gen_tables():
    """生成三线表 PNG 示例"""
    np.random.seed(42)
    print("\n=== 三线表 PNG ===")
    
    # Table 1: 单栏混合列
    df1 = pd.DataFrame({
        'Method': ['CNN', 'ResNet-50', 'ViT-B/16', 'Swin-T', 'DINOv2'],
        'Acc.(%)': [78.3, 82.1, 85.7, 86.2, 88.4],
        'F1': [0.762, 0.814, 0.849, 0.857, 0.879],
        'Params(M)': [1.2, 25.6, 86.0, 28.3, 304.0],
    })
    p = df_to_table_png(df1, caption='Table 1. Comparison of classification methods.',
                        column='single', output_path=f"{OUT}/table_single.png")
    print(f"  table_single: {p}")
    
    # Table 2: 双栏 8 行
    methods = [f'Model {chr(65+i)}' for i in range(8)]
    df2 = pd.DataFrame({
        'Method': methods,
        'Acc.(%)': np.round(np.random.uniform(70, 95, 8), 1),
        'Prec.(%)': np.round(np.random.uniform(65, 92, 8), 1),
        'Rec.(%)': np.round(np.random.uniform(68, 93, 8), 1),
        'F1': np.round(np.random.uniform(0.65, 0.92, 8), 3),
    })
    p = df_to_table_png(df2, caption='Table 2. Comparison of detection methods.',
                        column='double', output_path=f"{OUT}/table_double.png")
    print(f"  table_double: {p}")
    
    # Table 3: 全文本列
    df3 = pd.DataFrame({
        'Dataset': ['ImageNet-1K', 'CIFAR-100', 'COCO 2017', 'ADE20K', 'Cityscapes'],
        'Task': ['Classification', 'Classification', 'Detection', 'Segmentation', 'Segmentation'],
        'Metric': ['Top-1 Acc.', 'Top-1 Acc.', 'mAP@0.5', 'mIoU', 'mIoU'],
        'Domain': ['Natural', 'Natural', 'General', 'Scene', 'Urban'],
    })
    p = df_to_table_png(df3, caption='Table 3. Benchmark datasets summary.',
                        column='single', output_path=f"{OUT}/table_text.png")
    print(f"  table_text: {p}")


def gen_diagrams():
    """生成示意图 PNG（graphviz + 300DPI）"""
    print("\n=== 示意图 (graphviz) ===")
    
    p = generate_flowchart_png(column='single',
                               output_path=f"{OUT}/flowchart_v11.png")
    print(f"  flowchart: {p}")
    
    p = generate_architecture_png(column='single',
                                  output_path=f"{OUT}/architecture_v11.png")
    print(f"  architecture: {p}")
    
    p = generate_pipeline_png(column='single',
                              output_path=f"{OUT}/pipeline_v11.png")
    print(f"  pipeline: {p}")


if __name__ == "__main__":
    gen_stats()
    gen_tables()
    gen_diagrams()
    print("\nDone! All examples generated.")

