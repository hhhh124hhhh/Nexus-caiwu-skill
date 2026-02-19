#!/usr/bin/env python3
"""
HTML 财务报告模板（完整版）
生成完整的交互式 HTML 财务报告
特性:
- 五维健康评分雷达图
- 营收与净利润柱状图
- 资产负债结构饼图
- 评分仪表盘
- 现金流分析图表
- 杜邦分析流程图
- 动画效果和交互
"""

import json
from typing import Dict, Any, List


def generate_html_report(data: Dict[str, Any], theme: str = "medium") -> str:
    """
    生成 HTML 报告（完整版）

    Args:
        data: 财务分析数据
        theme: 主题 (暂未使用，保留默认样式)

    Returns:
        HTML 字符串
    """
    # 提取数据
    stock_code = data.get("stock_code", "")
    stock_name = data.get("stock_name", "")
    key_metrics = data.get("key_metrics", {})
    health_score = data.get("health_score", 0)
    risk_level = data.get("risk_level", "")
    health_details = data.get("health_details", {})
    dupont_analysis = data.get("dupont_analysis", {})
    industry = data.get("industry", {})
    industry_analysis = data.get("industry_analysis", {})
    fetch_time = data.get("fetch_time", "")

    # 提取增强分析（如果存在）
    analysis = data.get("analysis", {})
    enhanced_analysis = None
    if analysis.get("profitability_detail") or analysis.get("smart_recommendations"):
        enhanced_analysis = analysis

    # 确定风险等级样式
    risk_class = "high" if "高风险" in risk_level or "中高" in risk_level else "medium" if "中等" in risk_level else "low"

    # 准备 JavaScript 数据
    metrics_json = json.dumps(key_metrics, ensure_ascii=False)
    health_json = json.dumps(health_details, ensure_ascii=False)
    dupont_json = json.dumps(dupont_analysis, ensure_ascii=False)

    # 生成完整的 HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_name} ({stock_code}) 财务分析报告</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            /* Lighter color scheme */
            --bg-primary: #1a2332;
            --bg-secondary: #243447;
            --bg-card: #2d3f52;
            --bg-card-hover: #3a4d63;
            --border-color: #4a5a6a;
            --text-primary: #ffffff;
            --text-secondary: #b8c5d6;
            --text-muted: #8a9aac;
            --accent-blue: #4a9eff;
            --accent-blue-light: #7bc0ff;
            --accent-green: #2ecc71;
            --accent-green-light: #58d68d;
            --accent-red: #e74c3c;
            --accent-red-light: #ff6b5b;
            --accent-orange: #f39c12;
            --accent-yellow: #f1c40f;
            --gradient-primary: linear-gradient(135deg, #2d4a6f 0%, #1a2a3f 100%);
            --gradient-card: linear-gradient(180deg, rgba(74, 158, 255, 0.08) 0%, rgba(74, 158, 255, 0) 100%);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'DM Sans', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        /* Header */
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-color);
        }}

        .header-left h1 {{
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
        }}

        .header-left .stock-code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.125rem;
            color: var(--accent-blue-light);
            background: rgba(74, 158, 255, 0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            display: inline-block;
        }}

        .header-right {{
            text-align: right;
        }}

        .risk-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.875rem;
        }}

        .risk-badge.high {{
            background: rgba(231, 76, 60, 0.2);
            color: var(--accent-red-light);
            border: 1px solid rgba(231, 76, 60, 0.4);
        }}

        .risk-badge.medium {{
            background: rgba(243, 156, 18, 0.2);
            color: var(--accent-orange);
            border: 1px solid rgba(243, 156, 18, 0.4);
        }}

        .risk-badge.low {{
            background: rgba(46, 204, 113, 0.2);
            color: var(--accent-green-light);
            border: 1px solid rgba(46, 204, 113, 0.4);
        }}

        /* Score Overview */
        .score-overview {{
            background: var(--gradient-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 3rem;
        }}

        .score-circle {{
            position: relative;
            width: 180px;
            height: 180px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .score-gauge-svg {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            filter: drop-shadow(0 0 20px rgba(74, 158, 255, 0.3));
        }}

        .score-number {{
            position: relative;
            z-index: 2;
            text-align: center;
            animation: fadeInUp 0.8s ease-out 0.3s both;
        }}

        .score-number .value {{
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1;
            background: linear-gradient(135deg, var(--accent-blue-light) 0%, var(--accent-blue) 50%, #ffffff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 30px rgba(74, 158, 255, 0.5);
        }}

        .score-number .label {{
            font-size: 0.875rem;
            color: var(--accent-blue-light);
            text-transform: uppercase;
            letter-spacing: 0.15em;
            font-weight: 600;
            margin-top: 0.25rem;
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes pulse {{
            0%, 100% {{
                filter: drop-shadow(0 0 20px rgba(74, 158, 255, 0.3));
            }}
            50% {{
                filter: drop-shadow(0 0 30px rgba(74, 158, 255, 0.5));
            }}
        }}

        .score-gauge-svg {{
            animation: pulse 3s ease-in-out infinite;
        }}

        .score-breakdown {{
            flex: 1;
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1rem;
        }}

        .score-item {{
            text-align: center;
            padding: 1rem 0.5rem;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }}

        .score-item:hover {{
            transform: translateY(-4px);
            border-color: var(--accent-blue);
            box-shadow: 0 8px 24px rgba(74, 158, 255, 0.2);
        }}

        .score-item .score {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}

        .score-item .score.max {{
            color: var(--accent-green-light);
        }}

        .score-item .score.mid {{
            color: var(--accent-orange);
        }}

        .score-item .score.low {{
            color: var(--accent-red-light);
        }}

        .score-item .label {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            transition: all 0.3s ease;
        }}

        .metric-card:hover {{
            background: var(--bg-card-hover);
            transform: translateY(-2px);
            border-color: var(--accent-blue);
        }}

        .metric-card .label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}

        .metric-card .value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}

        .metric-card .value.positive {{
            color: var(--accent-green-light);
        }}

        .metric-card .value.negative {{
            color: var(--accent-red-light);
        }}

        .metric-card .value.neutral {{
            color: var(--accent-blue-light);
        }}

        .metric-card .sub {{
            font-size: 0.75rem;
            color: var(--text-secondary);
        }}

        /* Section Title */
        .section-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
        }}

        /* Charts Grid */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .chart-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
        }}

        .chart-card.full-width {{
            grid-column: 1 / -1;
        }}

        .chart-card h3 {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-secondary);
        }}

        .chart-container {{
            width: 100%;
            height: 280px;
        }}

        /* Dupont Analysis */
        .dupont-section {{
            margin-bottom: 2rem;
        }}

        .dupont-flow {{
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
            padding: 1.5rem;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
        }}

        .dupont-item {{
            flex: 1;
            min-width: 120px;
            text-align: center;
            padding: 1rem;
            background: var(--bg-secondary);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}

        .dupont-item.dupont-result {{
            background: rgba(74, 158, 255, 0.2);
            border-color: var(--accent-blue);
        }}

        .dupont-item .label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
        }}

        .dupont-item .value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}

        .dupont-item .unit {{
            font-size: 0.75rem;
            color: var(--text-secondary);
        }}

        .dupont-operator {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--accent-blue-light);
            padding: 0 0.5rem;
        }}

        /* Analysis Section */
        .analysis-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .analysis-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
        }}

        .analysis-card h3 {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--accent-blue-light);
        }}

        .analysis-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-color);
        }}

        .analysis-item:last-child {{
            border-bottom: none;
        }}

        .analysis-item .label {{
            color: var(--text-secondary);
        }}

        .analysis-item .value {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        }}

        .analysis-item .value.positive {{
            color: var(--accent-green-light);
        }}

        .analysis-item .value.negative {{
            color: var(--accent-red-light);
        }}

        .analysis-item .value.neutral {{
            color: var(--accent-blue-light);
        }}

        /* Cash Flow Detail */
        .cashflow-detail {{
            margin-top: 1rem;
            padding: 1rem;
            background: var(--bg-secondary);
            border-radius: 8px;
            border-left: 3px solid var(--accent-blue);
        }}

        .cashflow-detail .detail-text {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }}

        /* Tooltip */
        .tooltip {{
            position: absolute;
            padding: 0.75rem 1rem;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}

        .tooltip.show {{
            opacity: 1;
        }}

        .tooltip .title {{
            font-weight: 600;
            margin-bottom: 0.25rem;
            color: var(--accent-blue-light);
        }}

        .tooltip .detail {{
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}

        /* Footer */
        footer {{
            text-align: center;
            padding: 2rem 0;
            color: var(--text-muted);
            font-size: 0.875rem;
            border-top: 1px solid var(--border-color);
            margin-top: 2rem;
        }}

        /* Animation */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .animate-in {{
            animation: fadeInUp 0.6s ease-out forwards;
            opacity: 0;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}

            .header {{
                flex-direction: column;
                gap: 1rem;
            }}

            .score-overview {{
                flex-direction: column;
            }}

            .score-breakdown {{
                grid-template-columns: repeat(3, 1fr);
            }}

            .charts-grid {{
                grid-template-columns: 1fr;
            }}

            .dupont-flow {{
                flex-direction: column;
            }}

            /* 增强分析样式 */
            .analysis-card.enhanced {{
                background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
                border: 1px solid var(--accent-blue);
                box-shadow: 0 4px 20px rgba(74, 158, 255, 0.1);
            }}

            .enhanced-summary {{
                font-size: 0.95rem;
                line-height: 1.6;
                color: var(--text-primary);
                margin-bottom: 1rem;
                padding: 0.75rem;
                background: rgba(74, 158, 255, 0.1);
                border-left: 3px solid var(--accent-blue);
                border-radius: 4px;
            }}

            .enhanced-detail {{
                margin: 1rem 0;
                padding: 1rem;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
            }}

            .enhanced-detail h4 {{
                color: var(--accent-blue-light);
                font-size: 0.9rem;
                margin-bottom: 0.75rem;
            }}

            .enhanced-detail .rating {{
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.85rem;
                font-weight: 600;
                background: var(--accent-blue);
                color: white;
            }}

            .enhanced-detail .comparison {{
                color: var(--accent-green-light);
                font-weight: 500;
            }}

            .enhanced-detail .drivers {{
                list-style: none;
                padding: 0;
                margin: 0.5rem 0 0 0;
            }}

            .enhanced-detail .drivers li {{
                padding: 0.25rem 0 0.25rem 1.5rem;
                position: relative;
            }}

            .enhanced-detail .drivers li:before {{
                content: "✓";
                position: absolute;
                left: 0;
                color: var(--accent-green);
            }}

            .dupont-breakdown {{
                margin-top: 0.75rem;
                padding: 0.75rem;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 6px;
            }}

            .industry-note {{
                font-style: italic;
                color: var(--text-muted);
                font-size: 0.9rem;
                padding: 0.5rem 1rem;
                background: rgba(243, 156, 18, 0.1);
                border-radius: 6px;
                margin-top: 0.75rem;
            }}

            .flexibility {{
                padding: 0.75rem 1rem;
                background: rgba(46, 204, 113, 0.1);
                border-radius: 6px;
                color: var(--accent-green-light);
                margin-top: 0.75rem;
            }}

            /* 智能建议样式 */
            .recommendations-list {{
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }}

            .recommendation-item {{
                padding: 1rem;
                border-radius: 8px;
                border-left: 4px solid;
                background: rgba(255, 255, 255, 0.03);
            }}

            .recommendation-item.positive {{
                border-color: var(--accent-green);
            }}

            .recommendation-item.neutral {{
                border-color: var(--accent-orange);
            }}

            .recommendation-item.negative {{
                border-color: var(--accent-red);
            }}

            .recommendation-item.info {{
                border-color: var(--accent-blue);
            }}

            .recommendation-item.warning {{
                border-color: var(--accent-orange);
            }}

            .recommendation-item h4 {{
                margin: 0 0 0.5rem 0;
                font-size: 0.95rem;
                color: var(--text-primary);
            }}

            .recommendation-item p {{
                margin: 0.25rem 0;
                font-size: 0.9rem;
                color: var(--text-secondary);
            }}

            .recommendation-item .action {{
                color: var(--accent-blue-light);
                font-weight: 500;
            }}

            /* 综合评价样式 */
            .overall-assessment {{
                background: linear-gradient(135deg, rgba(74, 158, 255, 0.1) 0%, rgba(46, 204, 113, 0.1) 100%);
            }}

            .assessment-section {{
                margin: 1rem 0;
            }}

            .assessment-section h4 {{
                font-size: 0.95rem;
                margin-bottom: 0.5rem;
            }}

            .assessment-section h4.positive {{
                color: var(--accent-green);
            }}

            .assessment-section h4.negative {{
                color: var(--accent-red);
            }}

            .assessment-section ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}

            .assessment-section ul li {{
                padding: 0.25rem 0 0.25rem 1.5rem;
                position: relative;
                color: var(--text-secondary);
            }}

            .assessment-section ul li:before {{
                position: absolute;
                left: 0;
            }}

            .assessment-section.positive ul li:before {{
                content: "✓";
                color: var(--accent-green);
            }}

            .assessment-section.negative ul li:before {{
                content: "⚠";
                color: var(--accent-red);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-left">
                <h1>{stock_name}</h1>
                <span class="stock-code">{stock_code}</span>
            </div>
            <div class="header-right">
                <div class="risk-badge {risk_class}">
                    {risk_level}
                </div>
            </div>
        </div>

        <!-- Score Overview -->
        <div class="score-overview animate-in">
            <div class="score-circle">
                <svg id="score-gauge" class="score-gauge-svg" viewBox="0 0 180 180"></svg>
                <div class="score-number">
                    <div class="value" id="score-value">0</div>
                    <div class="label">健康评分</div>
                </div>
            </div>
            <div class="score-breakdown">
                {generate_score_breakdown_html(health_details)}
            </div>
        </div>

        <!-- Metrics Grid -->
        <h2 class="section-title animate-in" style="animation-delay: 0.1s">核心财务指标</h2>
        <div class="metrics-grid animate-in" style="animation-delay: 0.15s">
            {generate_metrics_html(key_metrics)}
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid animate-in" style="animation-delay: 0.3s">
            <div class="chart-card">
                <h3>营收与净利润</h3>
                <div class="chart-container" id="bar-chart"></div>
            </div>
            <div class="chart-card">
                <h3>资产负债结构</h3>
                <div class="chart-container" id="pie-chart"></div>
            </div>
            <div class="chart-card full-width">
                <h3>五维健康评分雷达图</h3>
                <div class="chart-container" id="radar-chart"></div>
            </div>
            <div class="chart-card">
                <h3>评分仪表盘</h3>
                <div class="chart-container" id="gauge-chart"></div>
            </div>
            <div class="chart-card">
                <h3>现金流分析</h3>
                <div class="chart-container" id="cashflow-chart"></div>
            </div>
        </div>

        <!-- Dupont Analysis -->
        <div class="dupont-section animate-in" style="animation-delay: 0.4s">
            <h2 class="section-title">杜邦分析</h2>
            {generate_dupont_html(dupont_analysis)}
        </div>

        <!-- Analysis Section -->
        <div class="analysis-section animate-in" style="animation-delay: 0.5s">
            {generate_analysis_html(key_metrics, health_details, enhanced_analysis)}
        </div>
    </div>

    <!-- Tooltip -->
    <div id="tooltip" class="tooltip">
        <div class="title"></div>
        <div class="detail"></div>
    </div>

    <script>
        // Financial Data
        const financialData = {{
            stock_code: "{stock_code}",
            stock_name: "{stock_name}",
            key_metrics: {metrics_json},
            health_score: {health_score},
            health_details: {health_json},
            dupont_analysis: {dupont_json}
        }};

        // Colors
        const colors = {{
            blue: '#4a9eff',
            blueLight: '#7bc0ff',
            green: '#2ecc71',
            greenLight: '#58d68d',
            red: '#e74c3c',
            redLight: '#ff6b5b',
            orange: '#f39c12',
            yellow: '#f1c40f',
            border: '#4a5a6a',
            textMuted: '#8a9aac'
        }};

        // Tooltip functions
        const tooltip = d3.select('#tooltip');

        function showTooltip(event, title, detail) {{
            tooltip.select('.title').text(title);
            tooltip.select('.detail').text(detail);
            tooltip.classed('show', true)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        }}

        function hideTooltip() {{
            tooltip.classed('show', false);
        }}

        // 1. Score Gauge (Animated circular progress with gradient)
        function drawScoreGauge() {{
            const svg = d3.select("#score-gauge");
            const width = 180, height = 180;
            const radius = 75;
            const strokeWidth = 14;
            const center = {{ x: width / 2, y: height / 2 }};
            const score = financialData.health_score;

            svg.selectAll("*").remove();

            // Create gradient
            const defs = svg.append("defs");
            const gradientId = "score-gradient-" + Math.random().toString(36).substr(2, 9);
            const gradient = defs.append("linearGradient")
                .attr("id", gradientId)
                .attr("gradientUnits", "userSpaceOnUse");

            // Dynamic color based on score
            let startColor, endColor;
            if (score >= 80) {{
                startColor = colors.green;
                endColor = colors.greenLight;
            }} else if (score >= 60) {{
                startColor = colors.blue;
                endColor = colors.blueLight;
            }} else if (score >= 40) {{
                startColor = colors.orange;
                endColor = "#f9ca24";
            }} else {{
                startColor = colors.red;
                endColor = colors.redLight;
            }}

            gradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", endColor)
                .attr("stop-opacity", 0.8);

            gradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", startColor)
                .attr("stop-opacity", 1);

            // Background track
            svg.append("circle")
                .attr("cx", center.x)
                .attr("cy", center.y)
                .attr("r", radius)
                .attr("fill", "none")
                .attr("stroke", "rgba(74, 158, 255, 0.1)")
                .attr("stroke-width", strokeWidth);

            // Score arc
            const endAngle = -Math.PI / 2 + (score / 100) * Math.PI * 2;

            const arc = d3.arc()
                .innerRadius(radius - strokeWidth / 2)
                .outerRadius(radius + strokeWidth / 2)
                .startAngle(-Math.PI / 2)
                .endAngle(-Math.PI / 2);

            const path = svg.append("path")
                .attr("cx", center.x)
                .attr("cy", center.y)
                .attr("fill", "none")
                .attr("stroke", `url(#${{gradientId}})`)
                .attr("stroke-width", strokeWidth)
                .attr("stroke-linecap", "round")
                .attr("transform", `translate(${{center.x}}, ${{center.y}})`);

            // Animate the arc
            path.transition()
                .duration(1500)
                .ease(d3.easeCubicOut)
                .attrTween("d", function() {{
                    const interpolate = d3.interpolate(-Math.PI / 2, endAngle);
                    return function(t) {{
                        return arc({{ startAngle: -Math.PI / 2, endAngle: interpolate(t) }});
                    }};
                }});

            // Animate the score number
            const scoreValue = d3.select("#score-value");
            const currentScore = 0;
            scoreValue.text(currentScore);

            scoreValue.transition()
                .duration(1500)
                .ease(d3.easeCubicOut)
                .tween("number", function() {{
                    const interpolator = d3.interpolateNumber(0, score);
                    return function(t) {{
                        this.textContent = Math.round(interpolator(t));
                    }};
                }});
        }}

        // 2. Bar Chart
        function drawBarChart() {{
            const container = d3.select('#bar-chart');
            const width = 400;
            const height = 280;
            const margin = {{ top: 30, right: 30, bottom: 50, left: 70 }};

            container.selectAll('*').remove();

            const svg = container.append('svg')
                .attr('width', '100%')
                .attr('height', height)
                .attr('viewBox', `0 0 ${{width}} ${{height}}`);

            const revenue = financialData.key_metrics.revenue_billion || 0;
            const profit = financialData.key_metrics.net_profit_billion || 0;

            const data = [
                {{ label: '营业收入', value: revenue / 1000, unit: '千亿' }},
                {{ label: '净利润', value: Math.max(profit / 1000 * 3, 0.1), unit: '千亿(×3)' }}
            ];

            const xScale = d3.scaleBand()
                .domain(data.map(d => d.label))
                .range([margin.left, width - margin.right])
                .padding(0.5);

            const yScale = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.value) * 1.2])
                .range([height - margin.bottom, margin.top]);

            // Grid lines
            svg.append('g')
                .attr('class', 'grid')
                .attr('transform', `translate(${{margin.left}}, 0)`)
                .call(d3.axisLeft(yScale)
                    .tickSize(-(width - margin.left - margin.right))
                    .tickFormat('')
                )
                .selectAll('line')
                .attr('stroke', colors.border)
                .attr('stroke-dasharray', '3,3');

            // Axes
            svg.append('g')
                .attr('transform', `translate(0, ${{height - margin.bottom}})`)
                .call(d3.axisBottom(xScale))
                .selectAll('text')
                .attr('fill', colors.textMuted)
                .style('font-size', '12px');

            svg.append('g')
                .attr('transform', `translate(${{margin.left}}, 0)`)
                .call(d3.axisLeft(yScale).ticks(5))
                .selectAll('text')
                .attr('fill', colors.textMuted)
                .style('font-size', '11px');

            svg.selectAll('.domain').attr('stroke', colors.border);
            svg.selectAll('.tick line').attr('stroke', colors.border);

            // Bars
            svg.selectAll('.bar')
                .data(data)
                .join('rect')
                .attr('x', d => xScale(d.label))
                .attr('y', height - margin.bottom)
                .attr('width', xScale.bandwidth())
                .attr('height', 0)
                .attr('fill', (d, i) => i === 0 ? colors.blue : colors.green)
                .attr('rx', 4)
                .style('cursor', 'pointer')
                .on('mouseover', function(event, d) {{
                    d3.select(this).attr('opacity', 0.8);
                    const realValue = d.label === '营业收入'
                        ? financialData.key_metrics.revenue_billion
                        : financialData.key_metrics.net_profit_billion;
                    showTooltip(event, d.label, `${{realValue ? realValue.toFixed(1) : 'N/A'}} 亿元`);
                }})
                .on('mousemove', event => {{
                    tooltip
                        .style('left', (event.pageX + 15) + 'px')
                        .style('top', (event.pageY - 10) + 'px');
                }})
                .on('mouseout', function() {{
                    d3.select(this).attr('opacity', 1);
                    hideTooltip();
                }})
                .transition()
                .duration(800)
                .delay((d, i) => i * 200)
                .attr('y', d => yScale(d.value))
                .attr('height', d => height - margin.bottom - yScale(d.value));
        }}

        // 3. Pie Chart
        function drawPieChart() {{
            const container = d3.select('#pie-chart');
            const width = 400;
            const height = 280;
            const radius = Math.min(width, height) / 2 - 40;

            container.selectAll('*').remove();

            const svg = container.append('svg')
                .attr('width', '100%')
                .attr('height', height)
                .attr('viewBox', `0 0 ${{width}} ${{height}}`)
                .append('g')
                .attr('transform', `translate(${{width / 2}}, ${{height / 2}})`);

            const assets = financialData.key_metrics.total_assets_billion || 100;
            const liabilities = financialData.key_metrics.total_liabilities_billion || 0;
            const equity = assets - liabilities;

            console.log('[Pie Chart] Data:', {{ assets, liabilities, equity }});

            // Validate data - ensure all values are finite and non-negative
            if (!isFinite(assets) || !isFinite(liabilities) || !isFinite(equity) || assets <= 0) {{
                console.error('[Pie Chart] Invalid data:', {{ assets, liabilities, equity }});
                return;
            }}

            // Ensure liabilities is not negative
            const validLiabilities = Math.max(0, liabilities);
            const validEquity = Math.max(0, equity);

            const data = [
                {{ label: '负债', value: validLiabilities, color: colors.red }},
                {{ label: '净资产', value: validEquity, color: colors.green }}
            ];

            console.log('[Pie Chart] Processed data:', data);

            // Check if all values are valid
            if (data.some(d => !isFinite(d.value) || d.value < 0)) {{
                console.error('[Pie Chart] Invalid data values after processing:', data);
                return;
            }}

            // Check if total is valid
            const total = data.reduce((sum, d) => sum + d.value, 0);
            if (!isFinite(total) || total <= 0) {{
                console.error('[Pie Chart] Invalid total:', total);
                return;
            }}

            const pie = d3.pie()
                .value(d => d.value)
                .sort(null);

            const arc = d3.arc()
                .innerRadius(radius * 0.6)
                .outerRadius(radius);

            const arcs = svg.selectAll('.arc')
                .data(pie(data))
                .join('path')
                .attr('d', arc)
                .attr('fill', d => d.data.color)
                .attr('stroke', colors.border)
                .attr('stroke-width', 2)
                .style('cursor', 'pointer')
                .on('mouseover', function(event, d) {{
                    d3.select(this).attr('opacity', 0.8);
                    const pct = ((d.data.value / assets) * 100).toFixed(1);
                    showTooltip(event, d.data.label, `${{d.data.value.toFixed(1)}} 亿元 (${{pct}}%)`);
                }})
                .on('mousemove', event => {{
                    tooltip
                        .style('left', (event.pageX + 15) + 'px')
                        .style('top', (event.pageY - 10) + 'px');
                }})
                .on('mouseout', function() {{
                    d3.select(this).attr('opacity', 1);
                    hideTooltip();
                }})
                .transition()
                .duration(800)
                .delay((d, i) => i * 200)
                .attrTween('d', function(d) {{
                    const interpolate = d3.interpolate(d.startAngle + 0.1, d.endAngle - 0.1);
                    return function(t) {{
                        return arc({{
                            startAngle: d.startAngle,
                            endAngle: interpolate(t),
                            innerRadius: radius * 0.6,
                            outerRadius: radius
                        }});
                    }};
                }});

            // Labels - bind to pie data for correct positioning
            svg.selectAll('.label')
                .data(pie(data))
                .join('text')
                .attr('transform', d => `translate(${{arc.centroid(d)}})`)
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .attr('fill', '#fff')
                .attr('font-size', '12px')
                .attr('font-weight', '500')
                .text(d => d.data.label);
        }}

        // 4. Radar Chart
        function drawRadarChart() {{
            const container = d3.select('#radar-chart');
            const width = 600;
            const height = 280;
            const radius = Math.min(width, height) / 2 - 50;
            const center = {{ x: width / 2, y: height / 2 }};

            container.selectAll('*').remove();

            const svg = container.append('svg')
                .attr('width', '100%')
                .attr('height', height)
                .attr('viewBox', `0 0 ${{width}} ${{height}}`)
                .attr('preserveAspectRatio', 'xMidYMid meet')
                .append('g')
                .attr('transform', `translate(${{center.x}}, ${{center.y}})`);

            const dimensions = [];
            for (const [key, value] of Object.entries(financialData.health_details)) {{
                const names = {{
                    profitability: '盈利能力',
                    solvency: '偿债能力',
                    efficiency: '运营效率',
                    growth: '成长能力',
                    cashflow: '现金流质量'
                }};
                dimensions.push({{
                    key: key,
                    label: names[key] || key,
                    score: value.score,
                    max: value.max,
                    detail: value.detail
                }});
            }}

            const angleSlice = (Math.PI * 2) / dimensions.length;

            // Grid circles
            for (let i = 1; i <= 4; i++) {{
                svg.append('circle')
                    .attr('r', radius * i / 4)
                    .attr('fill', 'none')
                    .attr('stroke', colors.border)
                    .attr('stroke-dasharray', '3,3');
            }}

            // Axes and labels
            dimensions.forEach((d, i) => {{
                const angle = angleSlice * i - Math.PI / 2;
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius;

                svg.append('line')
                    .attr('x1', 0)
                    .attr('y1', 0)
                    .attr('x2', x)
                    .attr('y2', y)
                    .attr('stroke', colors.border)
                    .attr('stroke-width', 1);

                const labelX = Math.cos(angle) * (radius + 25);
                const labelY = Math.sin(angle) * (radius + 25);
                svg.append('text')
                    .attr('x', labelX)
                    .attr('y', labelY)
                    .attr('text-anchor', 'middle')
                    .attr('dominant-baseline', 'middle')
                    .attr('fill', colors.blueLight)
                    .attr('font-size', '12px')
                    .attr('font-weight', '500')
                    .text(d.label);
            }});

            // Data polygon
            const lineData = dimensions.map((d, i) => {{
                const angle = angleSlice * i - Math.PI / 2;
                const value = (d.score / d.max) * radius;
                return [Math.cos(angle) * value, Math.sin(angle) * value];
            }});

            const radarLine = d3.line()
                .x(d => d[0])
                .y(d => d[1])
                .curve(d3.curveLinearClosed);

            svg.append('path')
                .datum(lineData)
                .attr('d', radarLine)
                .attr('fill', colors.blue)
                .attr('fill-opacity', 0.2)
                .attr('stroke', colors.blueLight)
                .attr('stroke-width', 2);

            // Points
            dimensions.forEach((d, i) => {{
                const angle = angleSlice * i - Math.PI / 2;
                const value = (d.score / d.max) * radius;
                const x = Math.cos(angle) * value;
                const y = Math.sin(angle) * value;

                svg.append('circle')
                    .attr('cx', x)
                    .attr('cy', y)
                    .attr('r', 5)
                    .attr('fill', colors.blueLight)
                    .attr('stroke', colors.blue)
                    .attr('stroke-width', 2)
                    .style('cursor', 'pointer')
                    .on('mouseover', function(event) {{
                        const tooltip = d3.select('#tooltip');
                        tooltip.select('.title').text(d.label);
                        tooltip.select('.detail').text(`${{d.score}}/${{d.max}} - ${{d.detail}}`);
                        tooltip.classed('show', true)
                            .style('left', (event.pageX + 10) + 'px')
                            .style('top', (event.pageY - 10) + 'px');
                    }})
                    .on('mouseout', function() {{
                        d3.select('#tooltip').classed('show', false);
                    }});
            }});
        }}

        // 5. Gauge Chart (Detailed)
        function drawGaugeChart() {{
            const container = d3.select('#gauge-chart');
            const width = 400;
            const height = 280;
            const radius = 100;

            container.selectAll('*').remove();

            const svg = container.append('svg')
                .attr('width', '100%')
                .attr('height', height)
                .attr('viewBox', `0 0 ${{width}} ${{height}}`)
                .append('g')
                .attr('transform', `translate(${{width / 2}}, ${{radius + 20}})`);

            const score = financialData.health_score;
            const maxScore = 100;

            // Background arc
            const backgroundArc = d3.arc()
                .innerRadius(radius - 18)
                .outerRadius(radius)
                .startAngle(-Math.PI / 2)
                .endAngle(Math.PI / 2);

            svg.append('path')
                .attr('d', backgroundArc())
                .attr('fill', '#4a5a6a');

            // Score arc with gradient
            const scoreAngle = (score / maxScore) * Math.PI - Math.PI / 2;

            // Zones
            const zones = [
                {{ start: -Math.PI / 2, end: -Math.PI / 6, color: colors.green }},
                {{ start: -Math.PI / 6, end: Math.PI / 6, color: colors.orange }},
                {{ start: Math.PI / 6, end: Math.PI / 2, color: colors.red }}
            ];

            zones.forEach(zone => {{
                const zoneArc = d3.arc()
                    .innerRadius(radius - 18)
                    .outerRadius(radius)
                    .startAngle(zone.start)
                    .endAngle(zone.end);

                svg.append('path')
                    .attr('d', zoneArc())
                    .attr('fill', zone.color)
                    .attr('opacity', 0.3);
            }});

            // Score arc
            const scoreArc = d3.arc()
                .innerRadius(radius - 18)
                .outerRadius(radius)
                .startAngle(-Math.PI / 2)
                .endAngle(scoreAngle);

            svg.append('path')
                .attr('d', scoreArc())
                .attr('fill', score >= 80 ? colors.green : score >= 60 ? colors.blue : score >= 40 ? colors.orange : colors.red);

            // Score text
            svg.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '0.35em')
                .attr('fill', '#fff')
                .attr('font-size', '2rem')
                .attr('font-weight', '700')
                .text(score);

            svg.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', '1.5em')
                .attr('fill', colors.textMuted)
                .attr('font-size', '0.75rem')
                .text('/100');
        }}

        // 6. Cashflow Chart
        function drawCashflowChart() {{
            const container = d3.select('#cashflow-chart');
            const width = 400;
            const height = 280;
            const margin = {{ top: 30, right: 30, bottom: 60, left: 70 }};

            container.selectAll('*').remove();

            const svg = container.append('svg')
                .attr('width', '100%')
                .attr('height', height)
                .attr('viewBox', `0 0 ${{width}} ${{height}}`);

            // Get cashflow data with fallbacks
            const netProfit = financialData.key_metrics.net_profit_billion || 0;
            const operatingCF = financialData.key_metrics.operating_cash_flow_billion || 0;
            const freeCF = financialData.key_metrics.free_cash_flow_billion || 0;

            const data = [
                {{ label: '净利润', value: netProfit, color: colors.green }},
                {{ label: '经营现金流', value: operatingCF, color: colors.red }},
                {{ label: '自由现金流', value: freeCF, color: colors.orange }}
            ];

            const xScale = d3.scaleBand()
                .domain(data.map(d => d.label))
                .range([margin.left, width - margin.right])
                .padding(0.4);

            const maxValue = Math.max(...data.map(d => Math.abs(d.value))) * 1.2;
            if (maxValue === 0) return;  // Avoid division by zero

            const yScale = d3.scaleLinear()
                .domain([-maxValue, maxValue])
                .range([height - margin.bottom, margin.top]);

            // Zero line
            svg.append('line')
                .attr('x1', margin.left)
                .attr('x2', width - margin.right)
                .attr('y1', yScale(0))
                .attr('y2', yScale(0))
                .attr('stroke', colors.textMuted)
                .attr('stroke-dasharray', '3,3');

            // Axes
            svg.append('g')
                .attr('transform', `translate(0, ${{height - margin.bottom}})`)
                .call(d3.axisBottom(xScale))
                .selectAll('text')
                .attr('fill', colors.textMuted)
                .style('font-size', '11px');

            svg.append('g')
                .attr('transform', `translate(${{margin.left}}, 0)`)
                .call(d3.axisLeft(yScale).ticks(5).tickFormat(d => d + '亿'))
                .selectAll('text')
                .attr('fill', colors.textMuted)
                .style('font-size', '11px');

            svg.selectAll('.domain').attr('stroke', colors.border);
            svg.selectAll('.tick line').attr('stroke', colors.border);

            // Bars
            svg.selectAll('.bar')
                .data(data)
                .join('rect')
                .attr('x', d => xScale(d.label))
                .attr('y', d => d.value >= 0 ? yScale(d.value) : yScale(0))
                .attr('width', xScale.bandwidth())
                .attr('height', d => Math.abs(yScale(d.value) - yScale(0)))
                .attr('fill', d => d.color)
                .attr('rx', 4)
                .style('cursor', 'pointer')
                .on('mouseover', function(event, d) {{
                    d3.select(this).attr('opacity', 0.8);
                    showTooltip(event, d.label, `${{d.value.toFixed(2)}} 亿元`);
                }})
                .on('mousemove', event => {{
                    tooltip
                        .style('left', (event.pageX + 15) + 'px')
                        .style('top', (event.pageY - 10) + 'px');
                }})
                .on('mouseout', function() {{
                    d3.select(this).attr('opacity', 1);
                    hideTooltip();
                }});
        }}

        // Initialize all charts with error handling
        document.addEventListener('DOMContentLoaded', function() {{
            const charts = [
                {{ name: 'ScoreGauge', func: drawScoreGauge }},
                {{ name: 'BarChart', func: drawBarChart }},
                {{ name: 'PieChart', func: drawPieChart }},
                {{ name: 'RadarChart', func: drawRadarChart }},
                {{ name: 'GaugeChart', func: drawGaugeChart }},
                {{ name: 'CashflowChart', func: drawCashflowChart }}
            ];

            charts.forEach(chart => {{
                try {{
                    chart.func();
                    console.log('[Chart] ' + chart.name + ' rendered successfully');
                }} catch (error) {{
                    console.error('[Chart] ' + chart.name + ' failed:', error);
                }}
            }});
        }});
    </script>

    <footer>
        数据来源: AKShare · 本报告仅供参考，不构成投资建议 · 生成时间: {fetch_time[:19] if fetch_time else 'N/A'}
    </footer>
</body>
</html>'''

    return html


def generate_score_breakdown_html(health_details: Dict) -> str:
    """生成评分细目 HTML"""
    items = []
    names = {
        "profitability": "盈利能力",
        "solvency": "偿债能力",
        "efficiency": "运营效率",
        "growth": "成长能力",
        "cashflow": "现金流质量"
    }

    for key, detail in health_details.items():
        score = detail.get("score", 0)
        max_score = detail.get("max", 25)

        if score >= max_score * 0.8:
            score_class = "max"
        elif score >= max_score * 0.5:
            score_class = "mid"
        else:
            score_class = "low"

        name = names.get(key, key)

        items.append(f'''
                <div class="score-item">
                    <div class="score {score_class}">{score}</div>
                    <div class="label">{name}</div>
                </div>''')

    return "\n".join(items)


def generate_metrics_html(key_metrics: Dict) -> str:
    """生成指标卡片 HTML"""
    metric_config = [
        ("revenue_billion", "营业收入", "亿元"),
        ("net_profit_billion", "净利润", "亿元"),
        ("net_profit_margin", "净利率", "%"),
        ("gross_margin", "毛利率", "%"),
        ("roe", "ROE", "%"),
        ("roa", "ROA", "%"),
        ("debt_ratio", "资产负债率", "%"),
        ("asset_turnover", "资产周转率", ""),
        ("operating_cash_flow_billion", "经营现金流", "亿元"),
        ("investing_cash_flow_billion", "投资现金流", "亿元"),
        ("financing_cash_flow_billion", "筹资现金流", "亿元"),
        ("free_cash_flow_billion", "自由现金流", "亿元"),
        ("ocf_to_np", "现金流/净利润", "%"),
        ("capex_billion", "资本支出", "亿元"),
        ("dividends_paid_billion", "分红支出", "亿元"),
        ("ending_cash_billion", "期末现金", "亿元"),
    ]

    cards = []
    for key, label, unit in metric_config:
        value = key_metrics.get(key)
        if value is None:
            continue

        # 格式化数值
        if isinstance(value, float):
            display_value = f"{value:.2f}"
        else:
            display_value = str(value)

        # 确定数值样式
        value_class = "neutral"
        if isinstance(value, (int, float)):
            if value > 0:
                value_class = "positive" if key in ["operating_cash_flow_billion", "investing_cash_flow_billion", "free_cash_flow_billion"] else "neutral"
            elif value < 0:
                value_class = "negative"

        cards.append(f'''
            <div class="metric-card">
                <div class="label">{label}</div>
                <div class="value {value_class}">{display_value}</div>
                <div class="sub">{unit}</div>
            </div>''')

    return "\n".join(cards)


def generate_dupont_html(dupont_analysis: Dict) -> str:
    """生成杜邦分析 HTML"""
    net_margin = dupont_analysis.get("net_margin", 0)
    asset_turnover = dupont_analysis.get("asset_turnover", 0)
    equity_multiplier = dupont_analysis.get("equity_multiplier", 0)
    roe_dupont = dupont_analysis.get("roe_dupont", 0)

    return f'''
            <div class="dupont-flow">
                <div class="dupont-item">
                    <div class="label">净利率</div>
                    <div class="value">{net_margin:.2f}</div>
                    <div class="unit">%</div>
                </div>
                <div class="dupont-operator">×</div>
                <div class="dupont-item">
                    <div class="label">资产周转率</div>
                    <div class="value">{asset_turnover:.2f}</div>
                    <div class="unit">次</div>
                </div>
                <div class="dupont-operator">×</div>
                <div class="dupont-item">
                    <div class="label">权益乘数</div>
                    <div class="value">{equity_multiplier:.2f}</div>
                    <div class="unit">倍</div>
                </div>
                <div class="dupont-operator">=</div>
                <div class="dupont-item dupont-result">
                    <div class="label">ROE</div>
                    <div class="value">{roe_dupont:.2f}</div>
                    <div class="unit">%</div>
                </div>
            </div>'''


def generate_analysis_html(key_metrics: Dict, health_details: Dict, enhanced_analysis: Dict = None) -> str:
    """生成分析部分 HTML"""

    # 盈利能力分析
    profitability_items = []
    if key_metrics.get("net_profit_margin"):
        margin = key_metrics["net_profit_margin"]
        value_class = "positive" if margin >= 15 else "neutral" if margin >= 5 else "negative"
        profitability_items.append(f'''
                    <span class="label">净利率</span>
                    <span class="value {value_class}">{margin:.2f}%</span>''')

    if key_metrics.get("gross_margin"):
        margin = key_metrics["gross_margin"]
        value_class = "positive" if margin >= 30 else "neutral" if margin >= 15 else "negative"
        profitability_items.append(f'''
                    <span class="label">毛利率</span>
                    <span class="value {value_class}">{margin:.2f}%</span>''')

    profitability_items.append('<span class="value">行业正常水平</span>')

    # 现金流分析
    cashflow_items = []
    ocf_to_np = key_metrics.get("ocf_to_np", 0)
    if ocf_to_np is not None:
        if ocf_to_np >= 120:
            status = "positive"
            status_text = "优秀"
        elif ocf_to_np >= 80:
            status = "neutral"
            status_text = "良好"
        else:
            status = "negative"
            status_text = "需关注"

        cashflow_items.append(f'''
                    <span class="label">现金流/净利润</span>
                    <span class="value {status}">{ocf_to_np:.2f}%</span>''')

        if ocf_to_np >= 120:
            cashflow_items.append(f'''
                    <span class="value">现金流质量{status_text}</span>''')
        elif ocf_to_np > 0 and ocf_to_np < 80:
            cashflow_items.append(f'''
                    <span class="value">现金流一般，建议关注</span>''')
        else:
            cashflow_items.append(f'''
                    <span class="value">现金流质量需改善</span>''')

    html = f'''
            <div class="analysis-card">
                <h3>盈利能力分析</h3>
                {''.join(f'<div class="analysis-item">{item}</div>' for item in profitability_items)}
            </div>
            <div class="analysis-card">
                <h3>现金流分析</h3>
                {''.join(f'<div class="analysis-item">{item}</div>' for item in cashflow_items)}
                {generate_cashflow_detail_html(key_metrics)}
            </div>'''

    # 增强分析
    if enhanced_analysis:
        html += generate_enhanced_analysis_html(enhanced_analysis)

    return html


def generate_cashflow_detail_html(key_metrics: Dict) -> str:
    """生成现金流详细分析 HTML"""
    operating_cf = key_metrics.get("operating_cash_flow_billion", 0)
    investing_cf = key_metrics.get("investing_cash_flow_billion", 0)
    financing_cf = key_metrics.get("financing_cash_flow_billion", 0)
    free_cf = key_metrics.get("free_cash_flow_billion", 0)

    # 现金流质量评估
    if operating_cf > 0 and free_cf > 0:
        detail = "经营现金流和自由现金流均为正，现金流状况良好，盈利质量较高。"
    elif operating_cf > 0 and free_cf < 0:
        detail = "经营现金流为正但自由现金流为负，可能存在较大的资本支出，需关注投资回报率。"
    elif operating_cf < 0:
        detail = "经营现金流为负，现金流状况恶化，需高度关注其持续经营能力。"
    else:
        detail = "现金流数据暂无完整信息。"

    # 投资活动分析
    if investing_cf < 0:
        detail += " 投资活动现金流出，主要为资本支出或对外投资。"
    elif investing_cf > 0:
        detail += " 投资活动现金流入，可能为出售资产或投资回收。"

    # 筹资活动分析
    if financing_cf < 0:
        detail += " 筹资活动现金流出，主要为偿还债务或分配股利。"
    elif financing_cf > 0:
        detail += " 筹资活动现金流入，可能为新增借款或股权融资。"

    return f'''
            <div class="cashflow-detail">
                <div class="detail-text">{detail}</div>
            </div>'''


if __name__ == "__main__":
    # 测试代码
    test_data = {
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "key_metrics": {
            "revenue_billion": 1309.04,
            "net_profit_billion": 668.99,
            "net_profit_margin": 51.11,
            "gross_margin": 68.35,
            "roe": 25.18,
            "roa": 21.95,
            "debt_ratio": 12.81,
            "asset_turnover": 0.43,
            "operating_cash_flow_billion": 381.97,
            "investing_cash_flow_billion": -54.23,
            "financing_cash_flow_billion": -432.44,
            "free_cash_flow_billion": 359.14,
            "ocf_to_np": 57.1,
            "capex_billion": 22.83,
            "dividends_paid_billion": 372.13,
            "ending_cash_billion": 1595.02,
            "total_assets_billion": 3047.38,
            "total_liabilities_billion": 390.33,
        },
        "health_score": 82,
        "risk_level": "低风险",
        "health_details": {
            "profitability": {"score": 25, "max": 25, "detail": "优秀 (ROE>15%)"},
            "solvency": {"score": 25, "max": 25, "detail": "低风险 (负债率<40%)"},
            "efficiency": {"score": 5, "max": 20, "detail": "较低 (周转率0.3-0.5)"},
            "growth": {"score": 12, "max": 15, "detail": "稳定"},
            "cashflow": {"score": 15, "max": 15, "detail": "优秀 (现金流/净利润>1.2)"}
        },
        "dupont_analysis": {
            "net_margin": 51.11,
            "asset_turnover": 0.43,
            "equity_multiplier": 1.15,
            "roe_dupont": 25.18
        },
        "fetch_time": "2026-02-17T20:00:00"
    }

    html = generate_html_report(test_data)
    print("HTML report generated successfully!")
    print(f"Length: {len(html)} characters")

    # Save test file
    import os
    os.makedirs("reports", exist_ok=True)
    with open("reports/test_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Test report saved to: reports/test_report.html")


# ===== 增强分析 HTML 生成函数 =====

def generate_enhanced_analysis_html(enhanced_analysis: Dict) -> str:
    """生成增强分析 HTML"""
    html_parts = []

    # 盈利能力深度分析
    if "profitability_detail" in enhanced_analysis:
        html_parts.append(generate_profitability_detail_html(
            enhanced_analysis["profitability_detail"]
        ))

    # 偿债能力深度分析
    if "solvency_detail" in enhanced_analysis:
        html_parts.append(generate_solvency_detail_html(
            enhanced_analysis["solvency_detail"]
        ))

    # 运营效率深度分析
    if "efficiency_detail" in enhanced_analysis:
        html_parts.append(generate_efficiency_detail_html(
            enhanced_analysis["efficiency_detail"]
        ))

    # 现金流深度分析
    if "cashflow_detail" in enhanced_analysis:
        html_parts.append(generate_cashflow_detail_enhanced_html(
            enhanced_analysis["cashflow_detail"]
        ))

    # 智能建议
    if "smart_recommendations" in enhanced_analysis:
        html_parts.append(generate_smart_recommendations_html(
            enhanced_analysis["smart_recommendations"]
        ))

    # 综合评价
    if "overall_assessment" in enhanced_analysis:
        html_parts.append(generate_overall_assessment_html(
            enhanced_analysis["overall_assessment"]
        ))

    return "\n".join(html_parts)


def generate_profitability_detail_html(profitability_detail: Dict) -> str:
    """生成盈利能力深度分析 HTML"""
    html = '''
            <div class="analysis-card enhanced">
                <h3>盈利能力深度分析</h3>'''

    # 汇总
    if profitability_detail.get("summary"):
        html += f'''
                <p class="enhanced-summary">{profitability_detail["summary"]}</p>'''

    # 净利率分析
    if "net_margin_analysis" in profitability_detail:
        analysis = profitability_detail["net_margin_analysis"]
        html += f'''
                <div class="enhanced-detail">
                    <h4>净利率分析</h4>
                    <p><strong>评级：</strong><span class="rating">{analysis.get("rating", "")}</span></p>
                    <p>{analysis.get("interpretation", "")}</p>'''

        if "industry_comparison" in analysis:
            html += f'''
                    <p class="comparison">{analysis["industry_comparison"]}</p>'''

        if "drivers" in analysis:
            html += '''
                    <p><strong>驱动因素：</strong></p>
                    <ul class="drivers">'''
            for driver in analysis["drivers"]:
                html += f'<li>{driver}</li>'
            html += '''</ul>'''

        html += '''</div>'''

    # ROE 分析
    if "roe_analysis" in profitability_detail:
        analysis = profitability_detail["roe_analysis"]
        html += f'''
                <div class="enhanced-detail">
                    <h4>ROE 分析</h4>
                    <p><strong>评级：</strong><span class="rating">{analysis.get("rating", "")}</span></p>
                    <p>{analysis.get("interpretation", "")}</p>'''

        if "dupont_breakdown" in analysis:
            breakdown = analysis["dupont_breakdown"]
            html += f'''
                    <div class="dupont-breakdown">
                        <p><strong>杜邦分解：</strong></p>
                        <p>主要驱动力：{breakdown.get("main_driver", "")}</p>
                        <p>净利率贡献：{breakdown.get("net_margin", "")}</p>
                        <p>周转率贡献：{breakdown.get("turnover", "")}</p>
                        <p>杠杆贡献：{breakdown.get("leverage", "")}</p>
                    </div>'''

        html += '''</div>'''

    html += '''</div>'''
    return html


def generate_solvency_detail_html(solvency_detail: Dict) -> str:
    """生成偿债能力深度分析 HTML"""
    html = '''
            <div class="analysis-card enhanced">
                <h3>偿债能力深度分析</h3>'''

    if solvency_detail.get("summary"):
        html += f'''
                <p class="enhanced-summary">{solvency_detail["summary"]}</p>'''

    if "debt_level_analysis" in solvency_detail:
        analysis = solvency_detail["debt_level_analysis"]
        html += f'''
                <div class="enhanced-detail">
                    <h4>负债水平分析</h4>
                    <p><strong>评级：</strong><span class="rating">{analysis.get("rating", "")}</span></p>
                    <p>{analysis.get("interpretation", "")}</p>'''

        if "industry_context" in analysis:
            html += f'''
                    <p class="industry-note">{analysis["industry_context"]}</p>'''

        html += '''</div>'''

    if solvency_detail.get("financial_flexibility"):
        html += f'''
                <p class="flexibility">{solvency_detail["financial_flexibility"]}</p>'''

    html += '''</div>'''
    return html


def generate_efficiency_detail_html(efficiency_detail: Dict) -> str:
    """生成运营效率深度分析 HTML"""
    html = '''
            <div class="analysis-card enhanced">
                <h3>运营效率深度分析</h3>'''

    if efficiency_detail.get("summary"):
        html += f'''
                <p class="enhanced-summary">{efficiency_detail["summary"]}</p>'''

    if "turnover_analysis" in efficiency_detail:
        analysis = efficiency_detail["turnover_analysis"]
        html += f'''
                <div class="enhanced-detail">
                    <h4>资产周转率分析</h4>
                    <p><strong>评级：</strong><span class="rating">{analysis.get("rating", "")}</span></p>
                    <p>{analysis.get("interpretation", "")}</p>
                </div>'''

    if efficiency_detail.get("industry_context"):
        html += f'''
                <p class="industry-note">{efficiency_detail["industry_context"]}</p>'''

    html += '''</div>'''
    return html


def generate_cashflow_detail_enhanced_html(cashflow_detail: Dict) -> str:
    """生成现金流深度分析 HTML"""
    html = '''
            <div class="analysis-card enhanced">
                <h3>现金流深度分析</h3>'''

    if cashflow_detail.get("summary"):
        html += f'''
                <p class="enhanced-summary">{cashflow_detail["summary"]}</p>'''

    if "quality_analysis" in cashflow_detail:
        analysis = cashflow_detail["quality_analysis"]
        html += f'''
                <div class="enhanced-detail">
                    <h4>现金流质量</h4>
                    <p><strong>评级：</strong><span class="rating">{analysis.get("rating", "")}</span></p>
                    <p>{analysis.get("interpretation", "")}</p>
                </div>'''

    if "free_cashflow_analysis" in cashflow_detail:
        analysis = cashflow_detail["free_cashflow_analysis"]
        html += f'''
                <div class="enhanced-detail">
                    <h4>自由现金流</h4>
                    <p>{analysis.get("interpretation", "")}</p>
                </div>'''

    html += '''</div>'''
    return html


def generate_smart_recommendations_html(recommendations: List) -> str:
    """生成智能建议 HTML"""
    if not recommendations:
        return ""

    html = '''
            <div class="analysis-card enhanced recommendations">
                <h3>智能建议</h3>
                <div class="recommendations-list">'''

    for rec in recommendations:
        rec_type = rec.get("type", "")
        title = rec.get("title", "")
        detail = rec.get("detail", "")
        action = rec.get("action", "")

        type_class = {
            "strength": "positive",
            "moderate": "neutral",
            "concern": "negative",
            "industry_specific": "info",
            "dimension_specific": "warning"
        }.get(rec_type, "neutral")

        html += f'''
                    <div class="recommendation-item {type_class}">
                        <h4>{title}</h4>
                        <p>{detail}</p>
                        <p class="action">建议：{action}</p>
                    </div>'''

    html += '''
                </div>
            </div>'''
    return html


def generate_overall_assessment_html(assessment: Dict) -> str:
    """生成综合评价 HTML"""
    html = '''
            <div class="analysis-card enhanced overall-assessment">
                <h3>综合评价</h3>'''

    # 优势
    if "strengths" in assessment:
        strengths = assessment["strengths"]
        html += '''
                <div class="assessment-section">
                    <h4 class="positive">核心优势</h4>
                    <ul>'''
        for strength in strengths:
            html += f'<li>{strength}</li>'
        html += '''</ul>
                </div>'''

    # 关注点
    if "concerns" in assessment:
        concerns = assessment["concerns"]
        html += '''
                <div class="assessment-section">
                    <h4 class="negative">需要关注</h4>
                    <ul>'''
        for concern in concerns:
            html += f'<li>{concern}</li>'
        html += '''</ul>
                </div>'''

    # 投资展望
    if "investment_outlook" in assessment:
        outlook = assessment["investment_outlook"]
        html += '''
                <div class="assessment-section">
                    <h4>投资展望</h4>
                    <p><strong>短期：</strong>{}</p>
                    <p><strong>长期：</strong>{}</p>
                </div>'''.format(
            outlook.get("short_term", ""),
            outlook.get("long_term", "")
        )

    html += '''</div>'''
    return html
