# Nexus 财务分析技能使用示例

## 第一步：准备环境

```bash
# 1. 克隆原始项目
git clone https://github.com/hhhh124hhhh/Nexus-caiwu-agent
cd Nexus-caiwu-agent

# 2. 安装依赖
uv sync --all-extras --all-packages --group dev

# 3. 激活虚拟环境
.venv\Scripts\activate  # Windows

# 4. 配置 LLM API（任选一种）
# OpenAI
set UTU_LLM_TYPE=openai
set UTU_LLM_MODEL=gpt-4
set UTU_LLM_API_KEY=sk-xxx
set UTU_LLM_BASE_URL=https://api.openai.com/v1

# 或使用其他兼容 API（如智谱、通义等）
set UTU_LLM_TYPE=openai
set UTU_LLM_MODEL=glm-4
set UTU_LLM_API_KEY=your_api_key
set UTU_LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

## 第二步：使用技能

### 方式一：命令行分析

```bash
# 设置项目路径
set NEXUS_PROJECT_PATH=D:\projects\Nexus-caiwu-agent

# 检查环境
python scripts/wrapper.py check

# 分析股票（流式输出）
python scripts/wrapper.py analyze --code 600519 --name "贵州茅台"

# 获取财务数据（JSON 格式）
python scripts/wrapper.py data --code 600519 --name "贵州茅台" -o maotai.json
```

### 方式二：Python API

```python
import sys
sys.path.insert(0, "D:/projects/Nexus-caiwu-agent")

from utu.tools.akshare_financial_tool import get_financial_reports
from utu.tools.financial_analysis_toolkit import (
    calculate_ratios,
    analyze_trends,
    assess_health,
    generate_report
)

# 分析贵州茅台
stock_code = "600519"
stock_name = "贵州茅台"

# 1. 获取财务数据
print(f"正在获取 {stock_name} 的财务数据...")
data = get_financial_reports(stock_code, stock_name)

# 2. 计算财务比率
print("计算财务比率...")
ratios = calculate_ratios(data)
print(f"ROE: {ratios['profitability']['roe']:.2f}%")
print(f"净利率: {ratios['profitability']['net_profit_margin']:.2f}%")

# 3. 分析趋势（4年）
print("分析趋势...")
trends = analyze_trends(data, 4)
print(f"营收 CAGR: {trends['revenue']['cagr']:.2f}%")
print(f"趋势方向: {trends['revenue']['trend_direction']}")

# 4. 健康评估
print("评估健康度...")
health = assess_health(ratios, trends)
print(f"综合评分: {health['overall_score']}")
print(f"风险等级: {health['risk_level']}")
print(f"优势: {health['strengths']}")
print(f"劣势: {health['weaknesses']}")
print(f"建议: {health['recommendations']}")

# 5. 生成完整报告
print("生成报告...")
report = generate_report(data, stock_name)
print(f"报告已生成")
```

### 方式三：在 Claude Code 中直接使用

只需说：

```
帮我分析贵州茅台（600519）的财务状况，包括：
1. 盈利能力分析
2. 偿债能力分析
3. 成长性分析
4. 投资健康评估
```

Claude 会自动识别并使用 nexus-caiwu-agent 技能进行分析。

## 示例输出

### 财务比率
```
盈利能力:
  毛利率: 91.5%
  净利率: 52.3%
  ROE: 31.2%
  ROA: 24.8%

偿债能力:
  流动比率: 4.2
  资产负债率: 21.5%

运营效率:
  资产周转率: 0.5

成长能力:
  营收增长率: 18.5%
```

### 趋势分析
```
营收趋势 (4年):
  CAGR: 15.2%
  方向: 上升
  最新营收: 1275.5 亿元

利润趋势 (4年):
  CAGR: 14.8%
  方向: 上升
  最新利润: 653.8 亿元
```

### 健康评估
```
综合评分: 92.5
风险等级: 低风险

优势:
  - 盈利能力极强
  - 现金流充裕
  - 负债率低

劣势:
  - 增速放缓

投资建议:
  - 适合长期持有
  - 关注渠道改革进展
```
