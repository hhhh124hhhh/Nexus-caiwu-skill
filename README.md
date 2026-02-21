# Nexus Caiwu Skill

A股市场智能财务分析技能，作为 [Nexus-caiwu-agent](https://github.com/hhhh124hhhh/Nexus-caiwu-agent) 的 Skill 仓库，提供增强的财务分析能力。

## 功能特性

- **财务数据获取** - 支持 A 股全市场股票数据获取
- **多维度分析** - 杜邦分析、现金流分析、五维度健康评估
- **多公司对比** - 支持多家公司财务指标对比分析，生成可视化报告
- **智能报告生成** - D3.js 交互式 HTML 报告
- **PPT 自动生成** - 基于百度 AI 的精美 PPT 生成

## 支持的市场

- 上海主板（600xxx, 601xxx, 602xxx, 603xxx, 605xxx）
- 深圳主板（000xxx, 001xxx）
- 创业板（300xxx）
- 科创板（688xxx）
- 北交所（8xxx, 43xxx）

## 快速开始

### 环境要求

- Python 3.8+

### 安装

```bash
# 克隆仓库
git clone https://github.com/hhhh124hhhh/Nexus-caiwu-skill.git
cd Nexus-caiwu-skill

# 安装 Python 依赖
pip install akshare pandas

# 可选：安装视频生成依赖
cd nexus-caiwu-agent/remotion-financial-videos
npm install
```

### 使用示例

#### 单股分析

```bash
# 分析股票
python nexus-caiwu-agent/scripts/fetch_data.py 600519 贵州茅台 --analyze

# 生成 HTML 报告
python nexus-caiwu-agent/scripts/fetch_data.py 600519 --analyze --save

# 生成 PPT（需要 BAIDU_API_KEY）
export BAIDU_API_KEY=your_api_key
python nexus-caiwu-agent/scripts/fetch_data.py 600519 --ai-ppt
```

#### 多公司对比分析

```python
from nexus-caiwu-agent.scripts.comparison_template import generate_comparison_html_report

# 准备对比数据
companies = [
    {
        "stock_code": "601668",
        "stock_name": "中国建筑",
        "key_metrics": {
            "revenue_billion": 15582.20,
            "net_profit_billion": 493.42,
            "net_profit_margin": 3.17,
            "roe": 6.04,
            "debt_ratio": 76.07,
            "ending_cash_billion": 3039.69,
        },
        "health_score": 60,
        "risk_level": "中等风险"
    },
    {
        "stock_code": "601186",
        "stock_name": "中国铁建",
        "key_metrics": {
            "revenue_billion": 7284.03,
            "net_profit_billion": 172.29,
            "net_profit_margin": 2.37,
            "roe": 4.0,
            "debt_ratio": 79.14,
            "ending_cash_billion": 1541.45,
        },
        "health_score": 52,
        "risk_level": "中等风险"
    },
]

# 可选：添加行业和宏观数据
industry_data = {"total_output": "32万亿", "new_infrastructure_ratio": "40%"}
macro_data = {"gdp": "140.19万亿", "gdp_growth": "+5.0%"}

# 生成对比报告
html = generate_comparison_html_report(
    companies,
    industry_data=industry_data,
    macro_data=macro_data
)

# 保存报告
with open("comparison_report.html", "w", encoding="utf-8") as f:
    f.write(html)
```

## 分析框架

### 五维度健康评估 (100分制)

| 维度 | 权重 | 核心指标 | 满分条件 |
|------|------|----------|----------|
| 盈利能力 | 25% | ROE | > 15% |
| 偿债能力 | 25% | 资产负债率 | < 40% |
| 运营效率 | 20% | 资产周转率 | > 1.0 |
| 成长能力 | 15% | 营收增长率 | > 20% |
| 现金流质量 | 15% | 现金流/净利润 | > 1.2 |

### 风险等级

| 评分 | 风险等级 | 投资建议 |
|------|----------|----------|
| 80-100 | 低风险 | 可考虑配置 |
| 60-79 | 中低风险 | 适度配置 |
| 40-59 | 中等风险 | 谨慎配置 |
| 20-39 | 中高风险 | 不建议重仓 |
| 0-19 | 高风险 | 回避 |

## 项目结构

```
nexus-caiwu-skill/
├── nexus-caiwu-agent/
│   ├── scripts/                  # 核心脚本
│   │   ├── fetch_data.py         # 数据获取与分析
│   │   ├── comparison_template.py # 多公司对比报告模板
│   │   ├── ppt_generator.py
│   │   └── baidu_skills_wrapper.py
│   ├── skills/                   # 子技能
│   │   └── ai-ppt-generator/
│   ├── references/               # 参考文档
│   └── docs/                     # 文档
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## 对比报告特性

多公司对比报告生成器 (`comparison_template.py`) 提供：

- **完全离线** - 纯 SVG 图表，无外部 CDN 依赖
- **A股配色** - 红涨绿跌，符合国内投资者习惯
- **独立图表** - 收入对比、利润对比、ROE 排名、现金分布
- **响应式设计** - 支持手机、平板、电脑多端查看

## 相关项目

- [Nexus-caiwu-agent](https://github.com/hhhh124hhhh/Nexus-caiwu-agent) - 原始项目

## 许可证

[Apache-2.0](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！请阅读 [贡献指南](CONTRIBUTING.md)。
