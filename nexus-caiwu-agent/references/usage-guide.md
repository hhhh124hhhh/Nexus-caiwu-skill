# Nexus 财务分析技能使用指南

## 快速开始

### 1. 环境准备

```bash
# 克隆原始项目
git clone https://github.com/hhhh124hhhh/Nexus-caiwu-agent ~/projects/Nexus-caiwu-agent
cd ~/projects/Nexus-caiwu-agent

# 安装依赖（使用 uv）
uv sync --all-extras --all-packages --group dev

# 激活虚拟环境
source ./.venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

### 2. 配置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# Linux/macOS
export UTU_LLM_TYPE="openai"
export UTU_LLM_MODEL="gpt-4"
export UTU_LLM_API_KEY="your_api_key"
export UTU_LLM_BASE_URL="https://api.openai.com/v1"

# Windows
set UTU_LLM_TYPE=openai
set UTU_LLM_MODEL=gpt-4
set UTU_LLM_API_KEY=your_api_key
set UTU_LLM_BASE_URL=https://api.openai.com/v1
```

### 3. 验证安装

```bash
python scripts/wrapper.py check
```

## 使用方法

### 命令行方式

```bash
# 运行财务分析
python scripts/wrapper.py analyze --code 600248 --name "陕西建工"

# 获取财务数据（JSON 格式）
python scripts/wrapper.py data --code 600519 --name "贵州茅台" -o output.json

# 快速聊天模式
python scripts/wrapper.py chat --message "分析贵州茅台的财务状况"

# 检查环境
python scripts/wrapper.py check
```

### Python API 方式

```python
import sys
sys.path.insert(0, "/path/to/Nexus-caiwu-agent")

from utu.tools.akshare_financial_tool import get_financial_reports, get_key_metrics
from utu.tools.financial_analysis_toolkit import (
    calculate_ratios,
    analyze_trends,
    assess_health,
    generate_report
)

# 获取财务数据
data = get_financial_reports("600248", "陕西建工")

# 计算财务比率
ratios = calculate_ratios(data)
print(f"ROE: {ratios['profitability']['roe']}%")

# 分析趋势（4年）
trends = analyze_trends(data, 4)
print(f"营收 CAGR: {trends['revenue']['cagr']}%")

# 健康评估
health = assess_health(ratios, trends)
print(f"综合评分: {health['overall_score']}")
print(f"风险等级: {health['risk_level']}")

# 生成完整报告
report = generate_report(data, "陕西建工")
```

### 在 Claude Code 中使用

当你需要对 A 股进行财务分析时，只需说：

```
帮我分析陕西建工（600248）的财务状况
```

Claude 会自动识别并使用此技能进行分析。

## 分析能力详解

### 1. 财务比率计算

| 类别 | 指标 | 说明 |
|------|------|------|
| **盈利能力** | 毛利率、净利率、ROE、ROA | 衡量公司赚钱能力 |
| **偿债能力** | 流动比率、资产负债率 | 衡量公司还债能力 |
| **运营效率** | 资产周转率 | 衡量资产使用效率 |
| **成长能力** | 营收增长率、利润增长率 | 衡量公司成长性 |

### 2. 趋势分析

- 多年财务数据趋势（默认 4 年）
- CAGR（复合年增长率）计算
- 趋势方向判断（上升/下降/稳定）

### 3. 健康评估

综合评分（0-100）基于：
- 盈利能力权重：30%
- 偿债能力权重：30%
- 运营效率权重：20%
- 成长能力权重：20%

风险等级：
- 低风险：> 80 分
- 中等风险：60-80 分
- 高风险：< 60 分

## 支持的股票代码格式

| 市场 | 代码格式 | 示例 |
|------|----------|------|
| 上海主板 | 600xxx, 601xxx, 602xxx, 603xxx, 605xxx | 600519 贵州茅台 |
| 深圳主板 | 000xxx, 001xxx | 000858 五粮液 |
| 创业板 | 300xxx | 300750 宁德时代 |
| 科创板 | 688xxx | 688981 中芯国际 |
| 北交所 | 8xxx, 43xxx | 832566 梓撞科技 |

## 常见问题

### Q: 提示缺少环境变量？

确保设置了以下环境变量：
- `UTU_LLM_TYPE`
- `UTU_LLM_MODEL`
- `UTU_LLM_API_KEY`
- `UTU_LLM_BASE_URL`

### Q: 提示项目路径不存在？

```bash
# 设置项目路径环境变量
export NEXUS_PROJECT_PATH="/path/to/Nexus-caiwu-agent"

# 或在命令中指定
python scripts/wrapper.py --project-path /path/to/Nexus-caiwu-agent analyze --code 600248
```

### Q: 导入模块失败？

确保已安装项目依赖：

```bash
cd /path/to/Nexus-caiwu-agent
uv sync --all-extras --all-packages --group dev
source .venv/bin/activate
```

### Q: 数据获取失败？

1. 检查网络连接
2. 确认股票代码正确
3. AKShare 数据源可能暂时不可用，稍后重试

## 性能优化建议

1. **使用缓存**：系统自动缓存已获取的数据，避免重复请求
2. **批量分析**：使用 Python API 进行批量分析更高效
3. **流式输出**：使用 `--stream` 参数实时查看分析进度

## 更新技能

当原始项目有更新时：

```bash
cd /path/to/Nexus-caiwu-agent
git pull origin main
uv sync --all-extras --all-packages --group dev
```

## 相关资源

- [原始项目](https://github.com/hhhh124hhhh/Nexus-caiwu-agent)
- [标准化分析指南](https://github.com/hhhh124hhhh/Nexus-caiwu-agent/blob/main/examples/stock_analysis/STANDARDIZED_ANALYSIS_GUIDE.md)
- [AKShare 文档](https://github.com/akfamily/akshare)
