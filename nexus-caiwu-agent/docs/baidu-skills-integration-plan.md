# Baidu 技能集成到 nexus-caiwu-agent 方案

## 一、集成概述

将 7 个 Baidu AI 技能集成到财务分析系统中，增强以下能力：

| 能力增强 | 对应技能 | 应用场景 |
|---------|---------|---------|
| 自动生成财报PPT | `ai-ppt-generator` | 一键生成可视化财报报告 |
| 获取最新资讯 | `baidu-search` | 实时新闻、公告、市场动态 |
| 公司背景查询 | `baidu-baike-search` | 企业基本信息、行业知识 |
| 学术研究支持 | `baidu-scholar-search-skill` | 财务理论、行业研究论文 |
| 深度行业分析 | `deepresearch-conversation` | 多维度行业研究报告 |

---

## 二、架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                     nexus-caiwu-agent                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ fetch_data.py │───▶│  HTML Report │───▶│   PPT Report │      │
│  │   (核心)     │    │   (现有)     │    │   (新增)     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                                       │               │
│         ▼                                       ▼               │
│  ┌───────────────────────────────────────────────────────┐     │
│  │              baidu_skills_wrapper.py (新增)           │     │
│  ├───────────────────────────────────────────────────────┤     │
│  │  • search_latest_news()      │  • get_company_info()  │     │
│  │  • generate_ppt_report()     │  • academic_research() │     │
│  │  • deep_industry_analysis()  │  • video_notes()       │     │
│  └───────────────────────────────────────────────────────┘     │
│                          │                                     │
│                          ▼                                     │
│  ┌───────────────────────────────────────────────────────┐     │
│  │                  Baidu Skills API                      │     │
│  │  (clawhub.ai - via HTTP requests)                    │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、新增模块设计

### 3.1 `baidu_skills_wrapper.py`

核心包装模块，统一调用 Baidu 技能 API。

```python
#!/usr/bin/env python3
"""
Baidu 技能包装器
统一调用 clawhub.ai 的 Baidu 技能 API
"""

import requests
import json
from typing import Dict, List, Optional
from pathlib import Path

class BaiduSkillsWrapper:
    """Baidu 技能包装器"""

    def __init__(self, api_base: str = "https://clawhub.ai/ide-rea"):
        self.api_base = api_base
        self.timeout = 60

    def search_latest_news(self, company_name: str, stock_code: str) -> List[Dict]:
        """
        搜索公司最新资讯

        Args:
            company_name: 公司名称
            stock_code: 股票代码

        Returns:
            最新资讯列表
        """
        query = f"{company_name} {stock_code} 最新 财报 公告"
        # 调用 baidu-search 技能
        return self._call_skill("baidu-search", {"query": query})

    def get_company_info(self, company_name: str) -> Dict:
        """
        获取公司百科信息

        Args:
            company_name: 公司名称

        Returns:
            公司百科信息
        """
        # 调用 baidu-baike-search 技能
        return self._call_skill("baidu-baike-search", {"query": company_name})

    def generate_ppt_report(self, analysis_data: Dict, output_path: str) -> str:
        """
        生成财报分析PPT

        Args:
            analysis_data: 财务分析数据
            output_path: 输出路径

        Returns:
            PPT文件路径
        """
        # 构建PPT主题和内容
        theme = f"{analysis_data['stock_name']}({analysis_data['stock_code']})财务分析报告"
        content = self._build_ppt_content(analysis_data)

        # 调用 ai-ppt-generator 技能
        result = self._call_skill("ai-ppt-generator", {
            "theme": theme,
            "content": content,
            "style": "商务"
        })

        # 保存PPT
        ppt_path = Path(output_path) / f"{analysis_data['stock_code']}_financial_report.pptx"
        self._save_ppt(result, ppt_path)

        return str(ppt_path)

    def academic_research(self, topic: str, limit: int = 5) -> List[Dict]:
        """
        学术研究检索

        Args:
            topic: 研究主题
            limit: 返回数量

        Returns:
            相关论文列表
        """
        # 调用 baidu-scholar-search-skill 技能
        return self._call_skill("baidu-scholar-search-skill", {
            "query": topic,
            "limit": limit
        })

    def deep_industry_analysis(self, industry: str, aspects: List[str]) -> Dict:
        """
        深度行业分析

        Args:
            industry: 行业名称
            aspects: 分析维度

        Returns:
            行业分析报告
        """
        # 调用 deepresearch-conversation 技能
        return self._call_skill("deepresearch-conversation", {
            "topic": f"{industry}行业分析",
            "aspects": aspects
        })

    def _call_skill(self, skill_name: str, params: Dict) -> Dict:
        """调用技能API"""
        url = f"{self.api_base}/{skill_name}"
        try:
            response = requests.post(url, json=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "skill": skill_name}

    def _build_ppt_content(self, data: Dict) -> str:
        """构建PPT内容大纲"""
        content = f"""
# {data['stock_name']}财务分析报告

## 1. 公司概况
- 股票代码：{data['stock_code']}
- 行业：{data.get('industry', 'N/A')}

## 2. 核心财务指标
- 营业收入：{data.get('revenue_billion', 'N/A')}亿元
- 净利润：{data.get('net_profit_billion', 'N/A')}亿元
- 净利率：{data.get('net_profit_margin', 'N/A')}%
- ROE：{data.get('roe', 'N/A')}%

## 3. 健康评分
- 总评分：{data.get('health_score', 'N/A')}/100
- 风险等级：{data.get('risk_level', 'N/A')}

## 4. 行业对比
- 盈利能力：{data.get('profitability_rating', 'N/A')}
- 偿债能力：{data.get('solvency_rating', 'N/A')}
- 运营效率：{data.get('efficiency_rating', 'N/A')}

## 5. 投资建议
{chr(10).join(data.get('recommendations', []))}
"""
        return content

    def _save_ppt(self, ppt_data: Dict, path: Path):
        """保存PPT文件"""
        # 实现PPT保存逻辑
        pass
```

---

### 3.2 新增命令行参数

```python
# 在 fetch_data.py 中添加

parser.add_argument('--ppt', action='store_true',
                   help='生成财报分析PPT（需要ai-ppt-generator技能）')
parser.add_argument('--news', action='store_true',
                   help='获取公司最新资讯')
parser.add_argument('--baike', action='store_true',
                   help='获取公司百科信息')
parser.add_argument('--deep-analysis', action='store_true',
                   help='生成深度行业分析报告')
```

---

## 四、集成流程

### 4.1 基础分析流程（现有）

```
用户输入股票代码
    ↓
fetch_data.py 获取财务数据
    ↓
计算健康评分
    ↓
生成 HTML 报告
```

### 4.2 增强分析流程（新增）

```
用户输入股票代码 + --enhance
    ↓
fetch_data.py 获取财务数据
    ↓
计算健康评分 + 增强分析
    ↓
┌─────────────────────────────────────────┐
│  并行调用 Baidu 技能                    │
├─────────────────────────────────────────┤
│  • baidu-search     → 最新资讯          │
│  • baidu-baike      → 公司百科          │
│  • scholar-search   → 学术研究          │
└─────────────────────────────────────────┘
    ↓
生成增强 HTML 报告
    ↓
[可选] --ppt → 生成 PPT 报告
    ↓
[可选] --deep-analysis → 生成深度研究报告
```

---

## 五、文件结构

```
nexus-caiwu-agent/
├── scripts/
│   ├── fetch_data.py           # 修改：添加新参数
│   ├── analysis_enhancer.py    # 现有
│   ├── baidu_skills_wrapper.py # 新增：Baidu技能包装器
│   └── ...
├── reports/
│   ├── [股票代码]_financial_report.html    # 现有
│   ├── [股票代码]_financial_report.pptx    # 新增
│   └── [股票代码]_deep_analysis.md        # 新增
└── docs/
    └── baidu-skills-integration-plan.md    # 本文档
```

---

## 六、使用示例

### 示例1：基础分析 + PPT

```bash
# 生成财报分析HTML报告和PPT
python scripts/fetch_data.py 600519 贵州茅台 --analyze --enhance --ppt
```

### 示例2：完整增强分析

```bash
# 包含最新资讯、百科信息、学术研究、PPT、深度分析
python scripts/fetch_data.py 600519 贵州茅台 \
    --analyze \
    --enhance \
    --html \
    --ppt \
    --news \
    --baike \
    --deep-analysis
```

### 示例3：仅获取资讯

```bash
# 快速获取公司最新资讯
python scripts/fetch_data.py 600519 贵州茅台 --news
```

---

## 七、输出示例

### 7.1 PPT 报告结构

```
贵州茅台(600519)财务分析报告.pptx
│
├── 第1页：封面
│   └── 标题、公司信息、日期
│
├── 第2页：公司概况
│   ├── 基本信息
│   ├── 行业地位
│   └── 百科摘要（来自 baidu-baike-search）
│
├── 第3页：核心财务指标
│   ├── 营收、利润数据
│   ├── 关键财务比率
│   └── 趋势图表
│
├── 第4页：健康评分
│   ├── 总体评分
│   ├── 分维度评分
│   └── 雷达图
│
├── 第5页：行业对比
│   ├── vs 行业平均水平
│   ├── 优势分析
│   └── 改进建议
│
├── 第6页：最新资讯
│   ├── 近期公告
│   ├── 市场动态（来自 baidu-search）
│   └── 关键事件
│
└── 第7页：投资建议
    ├── 风险评估
    ├── 建议等级
    └── 关注要点
```

### 7.2 深度分析报告结构

```markdown
# [行业]深度分析报告

## 执行摘要
[AI生成的行业概要]

## 1. 行业概况
- 行业规模
- 发展阶段
- 主要特征

## 2. 竞争格局
- 市场集中度
- 主要参与者
- 竞争态势

## 3. 财务特征
- 典型财务指标
- 行业基准数据
- 盈利模式分析

## 4. 发展趋势
- 短期趋势（1-2年）
- 长期趋势（3-5年）
- 关键驱动因素

## 5. 风险与机遇
- 主要风险
- 发展机遇
- 政策影响

## 6. 学术观点
- 相关研究摘要
- 专家观点
- 理论框架

## 7. 结论与建议
- 投资建议
- 关注要点
- 研究展望

## 附录
- 数据来源
- 参考资料
```

---

## 八、技术要点

### 8.1 并行请求优化

```python
from concurrent.futures import ThreadPoolExecutor

def fetch_all_baidu_data(company_name: str, stock_code: str) -> Dict:
    """并行获取所有Baidu数据"""
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 并行提交多个请求
        futures = {
            'news': executor.submit(wrapper.search_latest_news, company_name, stock_code),
            'baike': executor.submit(wrapper.get_company_info, company_name),
            'scholar': executor.submit(wrapper.academic_research, f"{company_name} 财务分析")
        }

        # 收集结果
        results = {}
        for key, future in futures.items():
            try:
                results[key] = future.result(timeout=30)
            except Exception as e:
                results[key] = {'error': str(e)}

    return results
```

### 8.2 错误处理

```python
def safe_call_skill(skill_func, *args, **kwargs):
    """安全调用技能，失败时返回默认值"""
    try:
        return skill_func(*args, **kwargs)
    except requests.Timeout:
        return {'error': '请求超时', 'timeout': True}
    except requests.ConnectionError:
        return {'error': '连接失败', 'connection_error': True}
    except Exception as e:
        return {'error': str(e), 'exception': True}
```

### 8.3 缓存策略

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedBaiduWrapper(BaiduSkillsWrapper):
    """带缓存的Baidu技能包装器"""

    def __init__(self, cache_ttl: int = 3600):
        super().__init__()
        self.cache_ttl = cache_ttl  # 缓存1小时
        self._cache = {}

    def search_latest_news(self, company_name: str, stock_code: str):
        cache_key = f"news_{company_name}_{stock_code}"

        # 检查缓存
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_data

        # 调用API
        result = super().search_latest_news(company_name, stock_code)

        # 存入缓存
        self._cache[cache_key] = (result, datetime.now())

        return result
```

---

## 九、实施计划

### 阶段一：基础集成（1-2天）
- [x] 创建 `baidu_skills_wrapper.py`
- [ ] 添加命令行参数
- [ ] 实现基础功能调用

### 阶段二：功能完善（2-3天）
- [ ] 实现并行请求
- [ ] 添加缓存机制
- [ ] 完善错误处理
- [ ] 编写单元测试

### 阶段三：输出增强（1-2天）
- [ ] PPT生成功能
- [ ] 深度分析报告
- [ ] 整合HTML报告

### 阶段四：测试验证（1天）
- [ ] 功能测试
- [ ] 性能测试
- [ ] 文档完善

---

## 十、预期效果

### 10.1 功能对比

| 功能 | 集成前 | 集成后 |
|------|--------|--------|
| 财务数据 | ✅ | ✅ |
| 健康评分 | ✅ | ✅ |
| HTML报告 | ✅ | ✅ |
| 增强分析 | ✅ | ✅ |
| PPT报告 | ❌ | ✅ 新增 |
| 最新资讯 | ❌ | ✅ 新增 |
| 公司百科 | ❌ | ✅ 新增 |
| 学术研究 | ❌ | ✅ 新增 |
| 深度分析 | ❌ | ✅ 新增 |

### 10.2 使用场景扩展

**集成前**：
- 财务数据分析
- 投资健康评估

**集成后**：
- 一站式投资研究平台
- 自动生成研究报告
- 多维度信息整合
- 专业演示文稿输出

---

## 十一、注意事项

1. **API依赖**：需要稳定的网络连接调用 clawhub.ai API
2. **速率限制**：注意API调用频率，避免超限
3. **数据质量**：Baidu技能返回的数据需要验证和清洗
4. **成本控制**：部分API可能有调用成本，需要监控
5. **隐私保护**：不要在API请求中包含敏感信息

---

## 十二、后续优化方向

1. **本地缓存增强**：使用Redis等缓存常用数据
2. **离线模式**：支持离线使用已缓存的数据
3. **批量处理**：支持批量分析多只股票
4. **定时更新**：定期自动更新公司资讯
5. **智能推荐**：基于分析结果智能推荐相关股票
6. **可视化增强**：更丰富的图表和交互式报告
