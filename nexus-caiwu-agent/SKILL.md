---
name: nexus-caiwu-agent
description: A股市场智能财务分析技能。提供财务数据获取、标准化分析、健康评估和报告生成能力。支持杜邦分析、现金流分析、五维度健康评分。当用户需要进行股票财务分析、财务报表解读、投资健康评估、A股分析时使用此技能。支持上海主板、深圳主板、创业板、科创板、北交所。
---

# Nexus 财务分析技能

基于 [Nexus-caiwu-agent](https://github.com/hhhh124hhhh/Nexus-caiwu-agent) 项目的 A 股市场智能财务分析技能。

## 元数据

- **GitHub**: https://github.com/hhhh124hhhh/Nexus-caiwu-agent.git
- **Commit Hash**: c6252038986d6f77bfed2b3401c9783712079e38
- **版本**: 0.1.0

## 核心脚本

### scripts/fetch_data.py（推荐使用）

**独立的数据获取脚本**，无需克隆原始项目。

**自动环境检测**：首次运行时自动检测 Python 环境并安装缺失的依赖。

**网络模式支持**：
- `auto` - 自动检测网络状态（默认）
- `direct` - 国内直连模式
- `proxy` - 代理模式（支持 HTTP/HTTPS/SOCKS5）

```bash
# 检查环境状态
python scripts/fetch_data.py --check

# 自动安装依赖
python scripts/fetch_data.py --install

# 检测网络模式
python scripts/fetch_data.py --detect-network

# 获取财务数据（自动模式）
python scripts/fetch_data.py 600519 贵州茅台

# 指定网络模式
python scripts/fetch_data.py 600519 --mode direct
python scripts/fetch_data.py 600519 --mode proxy --proxy http://127.0.0.1:7890

# 获取数据并分析
python scripts/fetch_data.py 600519 贵州茅台 --analyze --save
```

**输出示例**：
```json
{
  "stock_code": "600519",
  "stock_name": "贵州茅台",
  "key_metrics": {
    "revenue_billion": 1275.5,
    "net_profit_billion": 653.8,
    "net_profit_margin": 51.26,
    "debt_ratio": 21.5
  },
  "health_score": 60,
  "risk_level": "低风险"
}
```

### scripts/wrapper.py

完整版包装器，需要先克隆原始项目。适合需要完整功能的场景。

## 核心能力

- **财务比率计算**：盈利能力、偿债能力、运营效率、成长能力、现金流质量
- **杜邦分析**：ROE 分解（净利率 × 周转率 × 杠杆）
- **现金流分析**：经营现金流质量、自由现金流评估
- **健康评估**：五维度综合评分、风险等级
- **趋势分析**：多年趋势分析、CAGR 计算
- **报告生成**：D3.js 交互式 HTML 报告
- **数据持久化**：JSON 格式存储，支持后续分析

## 支持的市场

- 上海主板（600xxx, 601xxx, 602xxx, 603xxx, 605xxx）
- 深圳主板（000xxx, 001xxx）
- 创业板（300xxx）
- 科创板（688xxx）
- 北交所（8xxx, 43xxx）

## 使用方法

### 方式一：独立脚本（推荐）

```bash
# 检查环境（可选）
python scripts/fetch_data.py --check

# 自动安装依赖（或首次运行时自动安装）
python scripts/fetch_data.py --install

# 分析股票
python scripts/fetch_data.py 600519 贵州茅台 --analyze
```

**特性**：
- 自动检测 Python 版本（需要 3.8+）
- 自动检测并安装缺失的依赖包（akshare, pandas）
- 无需手动配置环境

### 方式二：直接对话

```
帮我分析贵州茅台（600519）的财务状况
分析 600248 陕西建工的投资价值
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
| 80-100 | 低风险 ✅ | 可考虑配置 |
| 60-79 | 中低风险 | 适度配置 |
| 40-59 | 中等风险 ⚠️ | 谨慎配置 |
| 20-39 | 中高风险 | 不建议重仓 |
| 0-19 | 高风险 ❌ | 回避 |

### 杜邦分析

```
ROE = 净利率 × 总资产周转率 × 权益乘数

分析维度:
- 净利率 → 盈利能力
- 资产周转率 → 运营效率
- 权益乘数 → 财务杠杆
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `data/[代码]_[名称].json` | 财务数据 JSON |
| `reports/[代码]_financial_report.html` | D3.js 交互报告 |

## 相关资源

- [原始项目](https://github.com/hhhh124hhhh/Nexus-caiwu-agent)
- [使用指南](references/usage-guide.md)
- [财务分析专业知识](references/financial-analysis-guide.md) ⭐
- [网络配置指南](references/network-guide.md) ⭐ **[NEW]**
- [AKShare 文档](https://github.com/akfamily/akshare)
