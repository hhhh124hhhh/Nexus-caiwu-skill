#!/usr/bin/env python3
"""
多公司财务对比分析HTML报告模板
生成完全离线的多公司对比分析报告

特性:
- 完全离线（无外部CDN依赖）
- 纯SVG图表
- 响应式设计（手机/平板/电脑）
- A股配色习惯（红涨绿跌）
- 侧边导航+平滑滚动

使用示例:
    from scripts.comparison_template import generate_comparison_html_report

    companies = [...]
    html = generate_comparison_html_report(companies)
"""

import json
from typing import Dict, Any, List, Optional


def generate_comparison_html_report(
    companies: List[Dict[str, Any]],
    industry_data: Optional[Dict] = None,
    macro_data: Optional[Dict] = None
) -> str:
    """
    生成多公司对比分析HTML报告（完全离线，无外部依赖）

    Args:
        companies: 公司列表，每个包含 {stock_code, stock_name, key_metrics, health_score, risk_level, ...}
        industry_data: 可选的行业数据 {total_output, new_infrastructure_ratio, green_building_ratio, ...}
        macro_data: 可选的宏观数据 {gdp, gdp_growth, infrastructure_investment_change, ...}

    Returns:
        HTML字符串（完全离线，无外部依赖）
    """
    # 提取公司数据
    company_list = []
    for company in companies:
        key_metrics = company.get("key_metrics", {})
        company_list.append({
            "code": company.get("stock_code", ""),
            "name": company.get("stock_name", ""),
            "revenue": key_metrics.get("revenue_billion", 0),
            "profit": key_metrics.get("net_profit_billion", 0),
            "net_margin": key_metrics.get("net_profit_margin", 0),
            "gross_margin": key_metrics.get("gross_margin", 0),
            "roe": key_metrics.get("roe", 0),
            "roa": key_metrics.get("roa", 0),
            "debt_ratio": key_metrics.get("debt_ratio", 0),
            "asset_turnover": key_metrics.get("asset_turnover", 0),
            "cash": key_metrics.get("ending_cash_billion", 0),
            "dividend": key_metrics.get("dividends_paid_billion", 0),
        })

    # 生成JavaScript数据
    companies_json = json.dumps(company_list, ensure_ascii=False)

    # 生成HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>多公司财务对比分析报告</title>
    <style>
        :root {{
            /* A股配色习惯：红涨绿跌 */
            --color-up: #ff4757;      /* 红色 - 上涨/收益 */
            --color-down: #2ecc71;    /* 绿色 - 下跌/成本 */
            --color-neutral: #00d4ff;  /* 蓝色 - 中性 */
            --color-purple: #9b59b6;   /* 紫色 */
            --color-orange: #f39c12;   /* 橙色 */

            --primary-gradient: linear-gradient(135deg, #00d4ff, #7c3aed);
            --secondary-gradient: linear-gradient(135deg, #ff4757, #ff6b35);
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --card-glow: 0 0 30px rgba(0, 212, 255, 0.1);
            --text-primary: #e0e0e0;
            --text-secondary: #888;
            --text-muted: #666;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: var(--text-primary);
            overflow-x: hidden;
        }}

        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background:
                radial-gradient(circle at 20% 50%, rgba(255, 71, 87, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(0, 212, 255, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }}

        .nav-toggle {{
            display: none;
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            cursor: pointer;
            z-index: 1001;
            backdrop-filter: blur(10px);
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }}

        .nav-toggle span {{
            width: 24px;
            height: 2px;
            background: var(--text-primary);
            border-radius: 2px;
            transition: all 0.3s;
        }}

        .nav-toggle.active span:nth-child(1) {{ transform: rotate(45deg) translate(6px, 6px); }}
        .nav-toggle.active span:nth-child(2) {{ opacity: 0; }}
        .nav-toggle.active span:nth-child(3) {{ transform: rotate(-45deg) translate(6px, -6px); }}

        .sidebar {{
            position: fixed;
            top: 0;
            left: 0;
            width: 260px;
            height: 100vh;
            background: rgba(15, 15, 26, 0.95);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--glass-border);
            z-index: 1000;
            padding: 30px 20px;
            transform: translateX(0);
            transition: transform 0.3s ease;
        }}

        .sidebar.collapsed {{ transform: translateX(-100%); }}

        .sidebar-brand {{
            font-size: 18px;
            font-weight: bold;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .nav-menu {{ list-style: none; }}

        .nav-item {{ margin-bottom: 8px; }}

        .nav-link {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s;
            font-size: 14px;
        }}

        .nav-link:hover, .nav-link.active {{
            background: var(--glass-bg);
            color: var(--color-neutral);
        }}

        .nav-link .icon {{ font-size: 18px; }}

        .main-content {{
            margin-left: 260px;
            transition: margin-left 0.3s ease;
            position: relative;
            z-index: 1;
        }}

        .main-content.expanded {{ margin-left: 0; }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }}

        .header {{
            background: var(--glass-bg);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            box-shadow: var(--card-glow);
            opacity: 0;
            animation: fadeInUp 0.6s ease forwards;
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .header h1 {{
            font-size: clamp(24px, 4vw, 36px);
            background: var(--secondary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
            font-weight: 700;
        }}

        .header .meta {{
            color: var(--text-secondary);
            font-size: 14px;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .section {{ margin-bottom: 40px; opacity: 0; animation: fadeInUp 0.6s ease forwards; }}
        .section:nth-child(2) {{ animation-delay: 0.1s; }}
        .section:nth-child(3) {{ animation-delay: 0.2s; }}
        .section:nth-child(4) {{ animation-delay: 0.3s; }}

        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }}

        .section-title {{
            font-size: 20px;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .card {{
            background: var(--glass-bg);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 25px;
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            box-shadow: var(--card-glow);
            transition: all 0.3s ease;
        }}

        .card:hover {{
            border-color: rgba(255, 71, 87, 0.3);
            box-shadow: 0 0 40px rgba(255, 71, 87, 0.15);
        }}

        .card h3 {{
            font-size: 16px;
            color: var(--color-neutral);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}

        .summary-card {{
            background: linear-gradient(135deg, rgba(255,71,87,0.1), rgba(255,107,53,0.05));
            border-radius: 16px;
            padding: 18px;
            border: 1px solid var(--glass-border);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .summary-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--secondary-gradient);
            opacity: 0;
            transition: opacity 0.3s;
        }}

        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(255, 71, 87, 0.2);
        }}

        .summary-card:hover::before {{ opacity: 1; }}

        .summary-card .company {{ font-size: 12px; color: var(--text-secondary); margin-bottom: 6px; }}
        .summary-card .label {{ font-size: 10px; color: var(--text-muted); }}
        .summary-card .value {{ font-size: 18px; font-weight: bold; margin-top: 6px; }}
        .summary-card.leader .value {{ color: var(--color-up); }}

        .chart-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .chart-container {{
            width: 100%;
            height: 280px;
            position: relative;
        }}

        .bar {{ transition: all 0.3s; cursor: pointer; }}
        .bar:hover {{ filter: brightness(1.2); }}
        .grid-line {{ stroke: rgba(255,255,255,0.1); stroke-dasharray: 4,4; }}

        .tooltip {{
            position: fixed;
            background: rgba(0,0,0,0.95);
            color: #fff;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 13px;
            pointer-events: none;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.2s;
            z-index: 2000;
            border: 1px solid var(--glass-border);
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }}
        .tooltip.visible {{ opacity: 1; transform: translateY(0); }}

        .table-container {{ overflow-x: auto; border-radius: 16px; }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            padding: 14px;
            text-align: left;
            border-bottom: 1px solid var(--glass-border);
            white-space: nowrap;
        }}

        th {{
            color: var(--color-neutral);
            font-weight: 600;
            font-size: 13px;
            background: rgba(0, 212, 255, 0.05);
        }}

        td {{ font-size: 13px; }}

        tr:hover {{ background: rgba(255,255,255,0.03); }}

        .rank-1 {{ color: var(--color-up); }}
        .rank-2 {{ color: var(--color-orange); }}
        .rank-3 {{ color: var(--color-neutral); }}

        .rank-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            font-size: 11px;
            font-weight: bold;
            margin-right: 8px;
        }}
        .rank-1-badge {{ background: var(--color-up); color: #fff; }}
        .rank-2-badge {{ background: var(--color-orange); color: #fff; }}
        .rank-3-badge {{ background: var(--color-neutral); color: #fff; }}

        .section-divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,71,87,0.5), transparent);
            margin: 40px 0;
        }}

        .divider-title {{
            font-size: 22px;
            background: var(--secondary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 25px;
            font-weight: 700;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }}

        .info-card {{
            background: linear-gradient(135deg, rgba(255,71,87,0.1), rgba(247,147,30,0.05));
            border-radius: 14px;
            padding: 16px;
            border: 1px solid rgba(255,71,87,0.2);
            text-align: center;
            transition: all 0.3s;
        }}

        .info-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(255,71,87,0.2);
        }}

        .info-card .icon {{ font-size: 28px; margin-bottom: 8px; }}
        .info-card .label {{ font-size: 11px; color: var(--text-secondary); }}
        .info-card .value {{ font-size: 20px; font-weight: bold; color: var(--color-up); }}
        .info-card .sub {{ font-size: 10px; color: var(--text-muted); margin-top: 6px; }}

        .policy-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 12px;
        }}

        .policy-card {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 16px;
            border-left: 3px solid var(--color-up);
            transition: all 0.3s;
        }}

        .policy-card:hover {{
            background: rgba(255,255,255,0.05);
        }}

        .policy-card .title {{
            font-size: 13px;
            color: var(--color-up);
            margin-bottom: 8px;
            font-weight: bold;
        }}

        .policy-card .content {{
            font-size: 12px;
            color: #aaa;
            line-height: 1.6;
        }}

        .policy-card .highlight {{ color: var(--color-down); font-weight: bold; }}

        .macro-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }}

        .macro-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 14px;
        }}

        .macro-item .indicator-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }}
        .macro-item .indicator-icon.positive {{ background: rgba(255,71,87,0.15); }}
        .macro-item .indicator-icon.negative {{ background: rgba(46,204,113,0.15); }}
        .macro-item .indicator-icon.neutral {{ background: rgba(0,212,255,0.15); }}

        .macro-item .info {{ flex: 1; }}
        .macro-item .name {{ font-size: 11px; color: var(--text-secondary); }}
        .macro-item .value {{ font-size: 14px; font-weight: bold; }}
        .macro-item .value.positive {{ color: var(--color-up); }}
        .macro-item .value.negative {{ color: var(--color-down); }}
        .macro-item .value.neutral {{ color: var(--color-neutral); }}

        .data-source {{
            font-size: 10px;
            color: var(--text-muted);
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid rgba(255,255,255,0.05);
        }}

        .footer {{
            text-align: center;
            padding: 25px;
            color: var(--text-muted);
            font-size: 12px;
            border-top: 1px solid var(--glass-border);
            margin-top: 40px;
        }}

        .scroll-top {{
            position: fixed;
            bottom: 25px;
            right: 25px;
            width: 45px;
            height: 45px;
            background: var(--secondary-gradient);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s;
            z-index: 999;
            box-shadow: 0 5px 25px rgba(255, 71, 87, 0.4);
        }}

        .scroll-top.visible {{
            opacity: 1;
            visibility: visible;
        }}

        @media (max-width: 1024px) {{
            .chart-row {{ grid-template-columns: 1fr; }}
        }}

        @media (max-width: 768px) {{
            .nav-toggle {{ display: flex; }}
            .sidebar {{ transform: translateX(-100%); }}
            .sidebar.active {{ transform: translateX(0); }}
            .main-content {{ margin-left: 0; }}
            .main-content.expanded {{ margin-left: 0; }}

            .container {{ padding: 20px 15px; }}
            .header {{ padding: 25px 20px; }}
            .summary-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .info-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .policy-grid {{ grid-template-columns: 1fr; }}
            .macro-list {{ grid-template-columns: 1fr; }}
            .chart-container {{ height: 240px; }}
        }}

        @media (max-width: 480px) {{
            .summary-grid {{ grid-template-columns: 1fr; }}
            .info-grid {{ grid-template-columns: 1fr; }}
            th, td {{ padding: 10px 6px; font-size: 11px; }}
        }}
    </style>
</head>
<body>
    <div class="nav-toggle" id="navToggle">
        <span></span>
        <span></span>
        <span></span>
    </div>

    <nav class="sidebar" id="sidebar">
        <div class="sidebar-brand">
            <span>📊</span>
            <span>财务对比分析</span>
        </div>
        <ul class="nav-menu">
            <li class="nav-item">
                <a href="#overview" class="nav-link active">
                    <span class="icon">📈</span>
                    <span>财务概览</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="#charts" class="nav-link">
                    <span class="icon">📊</span>
                    <span>图表分析</span>
                </a>
            </li>
            <li class="nav-item">
                <a href="#table" class="nav-link">
                    <span class="icon">📋</span>
                    <span>详细数据</span>
                </a>
            </li>
        </ul>
    </nav>

    <main class="main-content" id="mainContent">
        <div class="container">
            <header class="header" id="overview">
                <h1>多公司财务对比分析</h1>
                <div class="meta">
                    <span>📊 对比公司数: {len(company_list)}家</span>
                    <span>📅 生成时间: <span id="generateTime"></span></span>
                </div>
            </header>

            <section class="section">
                <div class="summary-grid" id="summaryCards"></div>
            </section>

            <section class="section" id="charts">
                <div class="section-header">
                    <h2 class="section-title">📊 图表分析</h2>
                </div>

                <div class="chart-row">
                    <div class="card">
                        <h3>💰 营业收入对比</h3>
                        <div class="chart-container" id="revenueChart"></div>
                    </div>
                    <div class="card">
                        <h3>📈 净利润对比</h3>
                        <div class="chart-container" id="profitChart"></div>
                    </div>
                </div>

                <div class="chart-row">
                    <div class="card">
                        <h3>🎯 盈利能力排名 (ROE)</h3>
                        <div class="chart-container" id="roeChart"></div>
                    </div>
                    <div class="card">
                        <h3>💎 现金储备分布</h3>
                        <div class="chart-container" id="cashChart"></div>
                    </div>
                </div>
            </section>

            <section class="section" id="table">
                <div class="section-header">
                    <h2 class="section-title">📋 详细财务指标</h2>
                </div>
                <div class="card">
                    <div class="table-container">
                        <table id="detailTable">
                            <thead>
                                <tr>
                                    <th>公司</th>
                                    <th>营收(亿)</th>
                                    <th>净利润(亿)</th>
                                    <th>净利率%</th>
                                    <th>ROE%</th>
                                    <th>资产负债率%</th>
                                    <th>现金储备(亿)</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </section>'''

    # 添加行业和宏观分析部分（如果有数据）
    if industry_data or macro_data:
        html += '''
            <div class="section-divider">
                <div class="divider-title">🏗️ 行业与宏观分析</div>
            </div>'''

    if industry_data:
        html += f'''
            <section class="section" id="industry">
                <div class="section-header">
                    <h2 class="section-title">🏗️ 行业概况</h2>
                </div>
                <div class="card">
                    <div class="info-grid">
                        <div class="info-card">
                            <div class="icon">🏗️</div>
                            <div class="label">建筑业总产值</div>
                            <div class="value">{industry_data.get("total_output", "N/A")}</div>
                        </div>
                        <div class="info-card">
                            <div class="icon">🔧</div>
                            <div class="label">新基建占比</div>
                            <div class="value">{industry_data.get("new_infrastructure_ratio", "N/A")}</div>
                        </div>
                        <div class="info-card">
                            <div class="icon">🌿</div>
                            <div class="label">绿色建筑占比</div>
                            <div class="value">{industry_data.get("green_building_ratio", "N/A")}</div>
                        </div>
                    </div>
                </div>
            </section>'''

    if macro_data:
        html += f'''
            <section class="section" id="macro">
                <div class="section-header">
                    <h2 class="section-title">🌍 宏观经济环境</h2>
                </div>
                <div class="card">
                    <div class="macro-list">
                        <div class="macro-item">
                            <div class="indicator-icon positive">📈</div>
                            <div class="info">
                                <div class="name">GDP总量</div>
                                <div class="value positive">{macro_data.get("gdp", "N/A")} ({macro_data.get("gdp_growth", "N/A")})</div>
                            </div>
                        </div>
                        <div class="macro-item">
                            <div class="indicator-icon neutral">🏗️</div>
                            <div class="info">
                                <div class="name">基础设施投资</div>
                                <div class="value neutral">{macro_data.get("infrastructure_investment_change", "N/A")}</div>
                            </div>
                        </div>
                    </div>
                    <div class="data-source">
                        📍 数据来源: 国家统计局、住建部、央行、财政部
                    </div>
                </div>
            </section>'''

    html += f'''
            <footer class="footer">
                <p>📊 仅供学习参考，不构成投资建议</p>
            </footer>
        </div>
    </main>

    <div class="tooltip" id="tooltip"></div>

    <div class="scroll-top" id="scrollTop">↑</div>

    <script>
        const financialData = {companies_json};

        // A股配色：红涨绿跌
        const colors = {{
            {', '.join([f'"{d["name"]}": "{["#ff4757", "#00d4ff", "#9b59b6", "#f39c12", "#e74c3c", "#3498db"][i]}"' for i, d in enumerate(company_list[:6])])}
        }};

        function formatNum(num) {{ return num.toLocaleString('zh-CN', {{maximumFractionDigits: 2}}); }}
        document.getElementById('generateTime').textContent = new Date().toLocaleString('zh-CN');

        const tooltip = document.getElementById('tooltip');
        function showTooltip(e, content) {{
            tooltip.innerHTML = content;
            tooltip.style.left = Math.min(e.pageX + 15, window.innerWidth - 200) + 'px';
            tooltip.style.top = e.pageY - 15 + 'px';
            tooltip.classList.add('visible');
        }}
        function hideTooltip() {{ tooltip.classList.remove('visible'); }}

        function createSVG(containerId) {{
            const container = document.getElementById(containerId);
            if (!container) return null;
            container.innerHTML = '';
            const width = container.clientWidth;
            const height = container.clientHeight;
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', width);
            svg.setAttribute('height', height);
            container.appendChild(svg);
            return {{ svg, width, height, margin: {{ top: 20, right: 25, bottom: 40, left: 60 }} }};
        }}

        // 营业收入对比图（独立）
        function drawRevenueChart() {{
            const chart = createSVG('revenueChart');
            if (!chart) return;
            const {{ svg, width, height, margin }} = chart;
            const chartWidth = width - margin.left - margin.right;
            const chartHeight = height - margin.top - margin.bottom;

            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('transform', `translate(${{margin.left}},${{margin.top}})`);
            svg.appendChild(g);

            const maxRevenue = Math.max(...financialData.map(d => d.revenue));

            // 网格线
            for (let i = 0; i <= 4; i++) {{
                const y = chartHeight - (i / 4) * chartHeight * 0.85;
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', 0);
                line.setAttribute('x2', chartWidth);
                line.setAttribute('y1', y);
                line.setAttribute('y2', y);
                line.setAttribute('class', 'grid-line');
                g.appendChild(line);

                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', -10);
                text.setAttribute('y', y + 4);
                text.setAttribute('text-anchor', 'end');
                text.setAttribute('fill', '#666');
                text.setAttribute('font-size', '10');
                text.textContent = (maxRevenue * i / 4 / 1000).toFixed(0) + 'k亿';
                g.appendChild(text);
            }}

            const barWidth = Math.min(50, chartWidth / financialData.length * 0.5);

            financialData.forEach((d, i) => {{
                const x = (i * chartWidth / financialData.length) + chartWidth / financialData.length / 2 - barWidth / 2;
                const y = chartHeight - (d.revenue / maxRevenue) * chartHeight * 0.85;
                const h = chartHeight - y;

                const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
                gradient.setAttribute('id', `gradRev${{i}}`);
                gradient.setAttribute('x1', '0%');
                gradient.setAttribute('y1', '0%');
                gradient.setAttribute('x2', '0%');
                gradient.setAttribute('y2', '100%');
                gradient.innerHTML = `<stop offset="0%" style="stop-color:${{colors[d.name]}};stop-opacity:1" /><stop offset="100%" style="stop-color:${{colors[d.name]}};stop-opacity:0.6" />`;
                svg.appendChild(gradient);

                const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                rect.setAttribute('x', x);
                rect.setAttribute('y', y);
                rect.setAttribute('width', barWidth);
                rect.setAttribute('height', h);
                rect.setAttribute('fill', `url(#gradRev${{i}})`);
                rect.setAttribute('class', 'bar');
                rect.setAttribute('rx', 6);
                rect.addEventListener('mousemove', (e) => showTooltip(e, `<b>${{d.name}}</b><br>营收: ${{formatNum(d.revenue)}}亿`));
                rect.addEventListener('mouseout', hideTooltip);
                g.appendChild(rect);

                const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                label.setAttribute('x', x + barWidth / 2);
                label.setAttribute('y', chartHeight + 20);
                label.setAttribute('text-anchor', 'middle');
                label.setAttribute('fill', '#999');
                label.setAttribute('font-size', '11');
                label.textContent = d.name;
                g.appendChild(label);

                // 数值标签
                const valueLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                valueLabel.setAttribute('x', x + barWidth / 2);
                valueLabel.setAttribute('y', y - 8);
                valueLabel.setAttribute('text-anchor', 'middle');
                valueLabel.setAttribute('fill', colors[d.name]);
                valueLabel.setAttribute('font-size', '11');
                valueLabel.setAttribute('font-weight', 'bold');
                valueLabel.textContent = (d.revenue / 1000).toFixed(1) + 'k';
                g.appendChild(valueLabel);
            }});
        }}

        // 净利润对比图（独立）
        function drawProfitChart() {{
            const chart = createSVG('profitChart');
            if (!chart) return;
            const {{ svg, width, height, margin }} = chart;
            const chartWidth = width - margin.left - margin.right;
            const chartHeight = height - margin.top - margin.bottom;

            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('transform', `translate(${{margin.left}},${{margin.top}})`);
            svg.appendChild(g);

            const maxProfit = Math.max(...financialData.map(d => d.profit));

            // 网格线
            for (let i = 0; i <= 4; i++) {{
                const y = chartHeight - (i / 4) * chartHeight * 0.85;
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', 0);
                line.setAttribute('x2', chartWidth);
                line.setAttribute('y1', y);
                line.setAttribute('y2', y);
                line.setAttribute('class', 'grid-line');
                g.appendChild(line);

                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', -10);
                text.setAttribute('y', y + 4);
                text.setAttribute('text-anchor', 'end');
                text.setAttribute('fill', '#666');
                text.setAttribute('font-size', '10');
                text.textContent = (maxProfit * i / 4).toFixed(0) + '亿';
                g.appendChild(text);
            }}

            const barWidth = Math.min(50, chartWidth / financialData.length * 0.5);

            financialData.forEach((d, i) => {{
                const x = (i * chartWidth / financialData.length) + chartWidth / financialData.length / 2 - barWidth / 2;
                const y = chartHeight - (d.profit / maxProfit) * chartHeight * 0.85;
                const h = chartHeight - y;

                const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
                gradient.setAttribute('id', `gradProf${{i}}`);
                gradient.setAttribute('x1', '0%');
                gradient.setAttribute('y1', '0%');
                gradient.setAttribute('x2', '0%');
                gradient.setAttribute('y2', '100%');
                gradient.innerHTML = `<stop offset="0%" style="stop-color:${{colors[d.name]}};stop-opacity:1" /><stop offset="100%" style="stop-color:${{colors[d.name]}};stop-opacity:0.6" />`;
                svg.appendChild(gradient);

                const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                rect.setAttribute('x', x);
                rect.setAttribute('y', y);
                rect.setAttribute('width', barWidth);
                rect.setAttribute('height', h);
                rect.setAttribute('fill', `url(#gradProf${{i}})`);
                rect.setAttribute('class', 'bar');
                rect.setAttribute('rx', 6);
                rect.addEventListener('mousemove', (e) => showTooltip(e, `<b>${{d.name}}</b><br>净利润: ${{formatNum(d.profit)}}亿`));
                rect.addEventListener('mouseout', hideTooltip);
                g.appendChild(rect);

                const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                label.setAttribute('x', x + barWidth / 2);
                label.setAttribute('y', chartHeight + 20);
                label.setAttribute('text-anchor', 'middle');
                label.setAttribute('fill', '#999');
                label.setAttribute('font-size', '11');
                label.textContent = d.name;
                g.appendChild(label);

                const valueLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                valueLabel.setAttribute('x', x + barWidth / 2);
                valueLabel.setAttribute('y', y - 8);
                valueLabel.setAttribute('text-anchor', 'middle');
                valueLabel.setAttribute('fill', colors[d.name]);
                valueLabel.setAttribute('font-size', '11');
                valueLabel.setAttribute('font-weight', 'bold');
                valueLabel.textContent = d.profit.toFixed(0);
                g.appendChild(valueLabel);
            }});
        }}

        // ROE排名图
        function drawRoeChart() {{
            const chart = createSVG('roeChart');
            if (!chart) return;
            const {{ svg, width, height, margin }} = chart;
            const chartWidth = width - margin.left - margin.right;
            const chartHeight = height - margin.top - margin.bottom;

            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('transform', `translate(${{margin.left}},${{margin.top}})`);
            svg.appendChild(g);

            const barHeight = 30;
            const gap = 20;
            const maxRoe = Math.max(...financialData.map(d => d.roe)) * 1.2;

            const sortedData = [...financialData].sort((a, b) => b.roe - a.roe);

            sortedData.forEach((d, i) => {{
                const y = i * (barHeight + gap) + 10;
                const barWidth = (d.roe / maxRoe) * chartWidth * 0.8;

                const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                bg.setAttribute('x', 0);
                bg.setAttribute('y', y);
                bg.setAttribute('width', chartWidth);
                bg.setAttribute('height', barHeight);
                bg.setAttribute('fill', 'rgba(255,255,255,0.03)');
                bg.setAttribute('rx', 6);
                g.appendChild(bg);

                const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
                gradient.setAttribute('id', `roeGrad${{i}}`);
                gradient.setAttribute('x1', '0%');
                gradient.setAttribute('y1', '0%');
                gradient.setAttribute('x2', '100%');
                gradient.setAttribute('y2', '0%');
                gradient.innerHTML = `<stop offset="0%" style="stop-color:${{colors[d.name]}};stop-opacity:0.8" /><stop offset="100%" style="stop-color:${{colors[d.name]}};stop-opacity:1" />`;
                svg.appendChild(gradient);

                const bar = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                bar.setAttribute('x', 0);
                bar.setAttribute('y', y);
                bar.setAttribute('width', barWidth);
                bar.setAttribute('height', barHeight);
                bar.setAttribute('fill', `url(#roeGrad${{i}})`);
                bar.setAttribute('rx', 6);
                bar.setAttribute('class', 'bar');
                bar.addEventListener('mousemove', (e) => showTooltip(e, `<b>${{d.name}}</b><br>ROE: ${{d.roe}}%`));
                bar.addEventListener('mouseout', hideTooltip);
                g.appendChild(bar);

                const name = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                name.setAttribute('x', barWidth + 10);
                name.setAttribute('y', y + barHeight / 2 + 4);
                name.setAttribute('fill', '#ccc');
                name.setAttribute('font-size', '13');
                name.textContent = d.name;
                g.appendChild(name);

                const value = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                value.setAttribute('x', barWidth + 80);
                value.setAttribute('y', y + barHeight / 2 + 4);
                value.setAttribute('fill', colors[d.name]);
                value.setAttribute('font-size', '14');
                value.setAttribute('font-weight', 'bold');
                value.textContent = d.roe + '%';
                g.appendChild(value);
            }});
        }}

        // 现金储备饼图
        function drawCashChart() {{
            const chart = createSVG('cashChart');
            if (!chart) return;
            const {{ svg, width, height }} = chart;
            const cx = width / 2;
            const cy = height / 2;
            const radius = Math.min(width, height) / 2 - 30;

            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            svg.appendChild(g);

            const total = financialData.reduce((sum, d) => sum + d.cash, 0);
            let currentAngle = -Math.PI / 2;

            financialData.forEach((d, i) => {{
                const sliceAngle = (d.cash / total) * Math.PI * 2;
                const endAngle = currentAngle + sliceAngle;

                const x1 = cx + radius * Math.cos(currentAngle);
                const y1 = cy + radius * Math.sin(currentAngle);
                const x2 = cx + radius * Math.cos(endAngle);
                const y2 = cy + radius * Math.sin(endAngle);

                const largeArc = sliceAngle > Math.PI ? 1 : 0;

                const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                path.setAttribute('d', `M ${{cx}} ${{cy}} L ${{x1}} ${{y1}} A ${{radius}} ${{radius}} 0 ${{largeArc}} 1 ${{x2}} ${{y2}} Z`);
                path.setAttribute('fill', colors[d.name]);
                path.setAttribute('class', 'bar');
                path.addEventListener('mousemove', (e) => showTooltip(e, `<b>${{d.name}}</b><br>现金: ${{formatNum(d.cash)}}亿<br>占比: ${{(d.cash/total*100).toFixed(1)}}%`));
                path.addEventListener('mouseout', hideTooltip);
                g.appendChild(path);

                const midAngle = currentAngle + sliceAngle / 2;
                const lx = cx + (radius * 0.65) * Math.cos(midAngle);
                const ly = cy + (radius * 0.65) * Math.sin(midAngle);

                const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                label.setAttribute('x', lx);
                label.setAttribute('y', ly);
                label.setAttribute('text-anchor', 'middle');
                label.setAttribute('dominant-baseline', 'middle');
                label.setAttribute('fill', '#fff');
                label.setAttribute('font-size', '12');
                label.setAttribute('font-weight', 'bold');
                label.textContent = (d.cash / total * 100).toFixed(0) + '%';
                g.appendChild(label);

                currentAngle = endAngle;
            }});

            const innerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            innerCircle.setAttribute('cx', cx);
            innerCircle.setAttribute('cy', cy);
            innerCircle.setAttribute('r', radius * 0.4);
            innerCircle.setAttribute('fill', '#0f0f1a');
            g.appendChild(innerCircle);

            const centerText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            centerText.setAttribute('x', cx);
            centerText.setAttribute('y', cy - 6);
            centerText.setAttribute('text-anchor', 'middle');
            centerText.setAttribute('fill', '#888');
            centerText.setAttribute('font-size', '10');
            centerText.textContent = '现金储备总计';
            g.appendChild(centerText);

            const centerValue = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            centerValue.setAttribute('x', cx);
            centerValue.setAttribute('y', cy + 12);
            centerValue.setAttribute('text-anchor', 'middle');
            centerValue.setAttribute('fill', '#ff4757');
            centerValue.setAttribute('font-size', '14');
            centerValue.setAttribute('font-weight', 'bold');
            centerValue.textContent = (total / 10000).toFixed(2) + '万亿';
            g.appendChild(centerValue);
        }}

        function renderSummaryCards() {{
            const container = document.getElementById('summaryCards');
            const metrics = [
                {{ key: 'revenue', label: '营业收入', unit: '亿' }},
                {{ key: 'profit', label: '净利润', unit: '亿' }},
                {{ key: 'roe', label: 'ROE', unit: '%' }},
                {{ key: 'cash', label: '现金储备', unit: '亿' }}
            ];

            metrics.forEach(metric => {{
                const sorted = [...financialData].sort((a, b) => b[metric.key] - a[metric.key]);
                sorted.forEach((d, i) => {{
                    const card = document.createElement('div');
                    card.className = 'summary-card' + (i === 0 ? ' leader' : '');
                    card.innerHTML = `
                        <div class="company">${{d.name}}</div>
                        <div class="label">${{metric.label}}</div>
                        <div class="value">${{i === 0 ? '🏆 ' : ''}}${{formatNum(d[metric.key])}}</div>
                    `;
                    container.appendChild(card);
                }});
            }});
        }}

        function renderDetailTable() {{
            const tbody = document.querySelector('#detailTable tbody');
            const metrics = ['revenue', 'profit', 'net_margin', 'roe', 'debt_ratio', 'cash'];
            const rankings = {{}};

            metrics.forEach(m => {{
                const sorted = [...financialData].sort((a, b) => b[m] - a[m]);
                rankings[m] = {{}};
                sorted.forEach((d, i) => rankings[m][d.code] = i + 1);
            }});

            financialData.forEach(d => {{
                const row = document.createElement('tr');
                let html = `<td><span class="rank-badge rank-${{rankings.revenue[d.code]}}-badge">${{rankings.revenue[d.code]}}</span>${{d.name}}</td>`;
                html += `<td class="rank-${{rankings.revenue[d.code]}}">${{formatNum(d.revenue)}}</td>`;
                html += `<td class="rank-${{rankings.profit[d.code]}}">${{formatNum(d.profit)}}</td>`;
                html += `<td>${{d.net_margin}}%</td>`;
                html += `<td class="rank-${{rankings.roe[d.code]}}">${{d.roe}}%</td>`;
                html += `<td>${{d.debt_ratio}}%</td>`;
                html += `<td class="rank-${{rankings.cash[d.code]}}">${{formatNum(d.cash)}}</td>`;
                row.innerHTML = html;
                tbody.appendChild(row);
            }});
        }}

        // 导航功能
        const navToggle = document.getElementById('navToggle');
        const sidebar = document.getElementById('sidebar');
        const navLinks = document.querySelectorAll('.nav-link');

        navToggle.addEventListener('click', () => {{
            navToggle.classList.toggle('active');
            sidebar.classList.toggle('active');
        }});

        navLinks.forEach(link => {{
            link.addEventListener('click', (e) => {{
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const target = document.getElementById(targetId);
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    navLinks.forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                    if (window.innerWidth <= 768) {{
                        navToggle.classList.remove('active');
                        sidebar.classList.remove('active');
                    }}
                }}
            }});
        }});

        window.addEventListener('scroll', () => {{
            const sections = ['overview', 'charts', 'table'];
            let current = '';

            sections.forEach(id => {{
                const section = document.getElementById(id);
                if (section) {{
                    const rect = section.getBoundingClientRect();
                    if (rect.top <= 150) {{
                        current = id;
                    }}
                }}
            }});

            navLinks.forEach(link => {{
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {{
                    link.classList.add('active');
                }}
            }});

            const scrollTop = document.getElementById('scrollTop');
            if (window.pageYOffset > 300) {{
                scrollTop.classList.add('visible');
            }} else {{
                scrollTop.classList.remove('visible');
            }}
        }});

        document.getElementById('scrollTop').addEventListener('click', () => {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});

        document.addEventListener('DOMContentLoaded', () => {{
            renderSummaryCards();
            renderDetailTable();
            drawRevenueChart();
            drawProfitChart();
            drawRoeChart();
            drawCashChart();
        }});

        let resizeTimer;
        window.addEventListener('resize', () => {{
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {{
                drawRevenueChart();
                drawProfitChart();
                drawRoeChart();
                drawCashChart();
            }}, 250);
        }});
    </script>
</body>
</html>'''

    return html


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_companies = [
        dict(
            stock_code="601668",
            stock_name="中国建筑",
            key_metrics=dict(
                revenue_billion=15582.20,
                net_profit_billion=493.42,
                net_profit_margin=3.17,
                gross_margin=4.25,
                roe=6.04,
                roa=1.45,
                debt_ratio=76.07,
                asset_turnover=0.46,
                ending_cash_billion=3039.69,
                dividends_paid_billion=328.15,
            ),
            health_score=60,
            risk_level="中等风险"
        ),
        dict(
            stock_code="601186",
            stock_name="中国铁建",
            key_metrics=dict(
                revenue_billion=7284.03,
                net_profit_billion=172.29,
                net_profit_margin=2.37,
                gross_margin=3.19,
                roe=4.0,
                roa=0.83,
                debt_ratio=79.14,
                asset_turnover=0.35,
                ending_cash_billion=1541.45,
                dividends_paid_billion=208.17,
            ),
            health_score=45,
            risk_level="中等风险"
        ),
        dict(
            stock_code="601390",
            stock_name="中国中铁",
            key_metrics=dict(
                revenue_billion=7760.59,
                net_profit_billion=192.18,
                net_profit_margin=2.48,
                gross_margin=3.35,
                roe=3.62,
                roa=0.8,
                debt_ratio=77.88,
                asset_turnover=0.32,
                ending_cash_billion=1553.51,
                dividends_paid_billion=184.84,
            ),
            health_score=42,
            risk_level="中等风险"
        )
    ]

    test_industry_data = dict(
        total_output="32万亿",
        new_infrastructure_ratio="40%",
        green_building_ratio="70%"
    )

    test_macro_data = dict(
        gdp="140.19万亿",
        gdp_growth="+5.0%",
        infrastructure_investment_change="-2.2%"
    )

    html = generate_comparison_html_report(
        test_companies,
        industry_data=test_industry_data,
        macro_data=test_macro_data
    )

    import os
    os.makedirs("reports", exist_ok=True)
    output_path = "reports/comparison_test_report.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("对比报告已生成!")
    print(f"保存路径: {{output_path}}")
    print(f"文件大小: {{len(html)}} 字符")
