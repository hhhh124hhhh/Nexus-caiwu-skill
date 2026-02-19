#!/usr/bin/env python3
"""
财务分析文字模板库
定义各类分析场景的文字模板
"""

# 评级到中文的映射
RATING_MAP = {
    "excellent": "优秀",
    "good": "良好",
    "neutral": "一般",
    "concern": "较差",
    "critical": "很差"
}

# 按维度组织的分析模板
ANALYSIS_TEMPLATES = {
    "profitability": {
        "excellent": [
            "{metric}达到{value}%，远超行业平均水平({industry_avg}%)，显示出强大的{ability}。",
            "公司{metric}表现卓越，在行业内处于领先地位。",
            "{metric}的优秀表现反映了公司在{aspect}方面的核心竞争力。",
            "凭借{metric}的优势，公司具备较强的盈利能力和市场地位。",
            "在当前市场环境下，{metric}达到{value}%是非常出色的成绩。"
        ],
        "good": [
            "{metric}为{value}%，高于行业平均水平，表现良好。",
            "公司{metric}稳健，显示出较好的{ability}。",
            "{metric}处于良性水平，说明公司{ability}较强。",
            "{metric}表现良好，为公司发展提供了有力支撑。"
        ],
        "neutral": [
            "{metric}为{value}%，处于行业平均水平附近。",
            "公司{metric}表现一般，还有提升空间。",
            "{metric}处于合理区间，符合行业特征。"
        ],
        "concern": [
            "{metric}为{value}%，低于行业平均水平，需要关注。",
            "{metric}偏低，建议分析原因并制定改善计划。",
            "公司{metric}有待提升，建议关注{aspect}方面的优化。"
        ],
        "critical": [
            "{metric}仅为{value}%，远低于行业平均水平，存在较大风险。",
            "{metric}持续低迷，严重影响公司盈利能力，需要立即采取措施。",
            "{metric}处于极低水平，公司的{ability}面临严重挑战。"
        ],
        # 特定指标模板
        "net_margin": {
            "excellent_drivers": [
                "高毛利率是净利率优异的主要驱动因素",
                "出色的费用控制能力显著提升了净利率",
                "产品溢价能力强，带动净利率提升"
            ],
            "concern_reasons": [
                "毛利率下降是净利率偏低的主要原因",
                "期间费用率过高侵蚀了利润空间",
                "成本压力增大导致净利率下滑"
            ]
        },
        "roe": {
            "excellent_drivers": [
                "高净利率是ROE优异的核心驱动力",
                "资产周转效率良好，助力ROE提升",
                "财务杠杆运用得当，放大了股东回报"
            ],
            "dupont_breakdown": {
                "margin_driver": "净利率贡献",
                "turnover_driver": "周转率贡献",
                "leverage_driver": "杠杆贡献"
            }
        },
        "gross_margin": {
            "excellent": [
                "高毛利率显示出强大的产品定价能力和品牌溢价",
                "成本控制优秀，毛利率处于行业领先水平",
                "产品结构优化，高附加值产品占比提升"
            ],
            "concern": [
                "毛利率偏低，产品定价能力较弱",
                "成本上升压力导致毛利率承压",
                "行业竞争加剧影响毛利率表现"
            ]
        }
    },

    "solvency": {
        "excellent": [
            "资产负债率仅{value}%，财务结构极为稳健。",
            "公司负债水平很低，财务风险极小，具备充足的融资空间。",
            "低负债策略为公司提供了强大的抗风险能力。"
        ],
        "good": [
            "资产负债率为{value}%，处于健康水平。",
            "公司财务结构稳健，偿债压力较小。",
            "负债水平适中，平衡了风险和收益。"
        ],
        "neutral": [
            "资产负债率为{value}%，处于行业平均水平。",
            "负债水平合理，财务状况基本稳定。"
        ],
        "concern": [
            "资产负债率达到{value}%，处于较高水平，需要关注。",
            "负债率偏高，建议优化资本结构，降低财务风险。",
            "偿债压力较大，需关注现金流对债务的覆盖能力。"
        ],
        "critical": [
            "资产负债率高达{value}%，财务风险较大，需要警惕。",
            "负债水平过高，存在一定的偿债风险，建议谨慎对待。",
            "高负债经营模式面临较大挑战，需要关注债务违约风险。"
        ],
        # 特定指标模板
        "debt_service": {
            "strong": [
                "经营现金流对利息支出的覆盖倍数超过{value}倍，偿债能力极强。",
                "充足的现金流完全能够覆盖债务本息，违约风险极低。"
            ],
            "weak": [
                "经营现金流对债务的覆盖能力不足，存在流动性风险。",
                "建议关注债务期限结构，避免短期偿债压力集中。"
            ]
        }
    },

    "efficiency": {
        "excellent": [
            "资产周转率达到{value}次/年，远超行业平均水平，运营效率卓越。",
            "公司资产利用效率极高，体现了出色的运营管理能力。",
            "高周转率表明公司资产使用效率优秀，盈利能力强劲。"
        ],
        "good": [
            "资产周转率为{value}次/年，高于行业平均水平，运营效率良好。",
            "公司资产使用效率较好，运营管理能力较强。"
        ],
        "neutral": [
            "资产周转率为{value}次/年，处于行业平均水平。",
            "周转率表现一般，资产利用效率有提升空间。"
        ],
        "concern": [
            "资产周转率仅为{value}次/年，低于行业平均水平，运营效率有待提升。",
            "周转率偏低，建议优化资产结构，提高资产使用效率。"
        ],
        "critical": [
            "资产周转率低至{value}次/年，远低于行业平均水平，运营效率严重不足。",
            "资产利用效率低下，严重影响盈利能力，需要重点改善。"
        ],
        # 行业特定模板
        "high_margin_low_turnover": [
            "公司采用高毛利低周转的商业模式，这是{industry}行业的典型特征。",
            "在{industry}行业，高毛利率是核心竞争力，周转率相对较低属于正常现象。",
            "公司的盈利模式侧重于产品溢价而非规模效应。"
        ],
        "low_margin_high_turnover": [
            "公司采用低毛利高周转的商业模式，通过规模效应获取利润。",
            "薄利多销是{industry}行业的常见策略，周转率是关键成功因素。"
        ]
    },

    "cashflow": {
        "excellent": [
            "经营现金流占净利润{value}%，现金创造能力强劲。",
            "现金流质量优异，利润含金量高，为持续发展提供保障。",
            "强劲的经营现金流显示出健康的盈利质量和良好的现金回收能力。"
        ],
        "good": [
            "经营现金流占净利润{value}%，现金流状况良好。",
            "现金流与利润匹配度较高，盈利质量较好。"
        ],
        "neutral": [
            "经营现金流占净利润{value}%，处于合理区间。",
            "现金流状况基本稳定，但仍有改善空间。"
        ],
        "concern": [
            "经营现金流占净利润{value}%，低于理想水平，需关注现金回收情况。",
            "现金流偏弱，建议加强应收账款管理，改善现金回收。"
        ],
        "critical": [
            "经营现金流为负，现金回收严重不足，存在流动性风险。",
            "现金流质量很差，需要警惕资金链断裂风险。"
        ],
        # 自由现金流
        "free_cash_flow": {
            "positive_strong": [
                "自由现金流达到{value}亿元，现金创造能力强劲，可用于分红、回购或扩张投资。",
                "充沛的自由现金流为公司提供了充足的财务灵活性和投资能力。"
            ],
            "negative": [
                "自由现金流为{value}亿元，主要由于资本支出较大，需关注投资回报情况。",
                "自由现金流为负，需评估资本支出的必要性和回报预期。"
            ]
        },
        # 现金流结构
        "structure": {
            "healthy": "现金流结构健康，经营现金流入足以覆盖投资和筹资需求。",
            "investing_heavy": "投资现金流流出较大，公司处于扩张期，需关注投资回报。",
            "financing_heavy": "筹资现金流流出较大，主要用于分红或偿债，需评估可持续性。"
        }
    },

    "growth": {
        "excellent": [
            "{metric}增长{value}%，增速远超行业平均水平，成长性突出。",
            "公司处于快速成长阶段，{metric}增长强劲。",
            "优异的增长速度显示出强大的市场竞争力和发展潜力。"
        ],
        "good": [
            "{metric}增长{value}%，高于行业平均水平，成长性良好。",
            "公司保持稳健增长，发展势头良好。"
        ],
        "neutral": [
            "{metric}增长{value}%，处于行业平均水平。",
            "增长速度平稳，符合市场预期。"
        ],
        "concern": [
            "{metric}增长{value}%，增速低于行业平均水平，成长性有待提升。",
            "增长放缓，需要关注市场环境和竞争态势。"
        ],
        "negative": [
            "{metric}下降{abs_value}%，出现负增长，需要警惕。",
            "业务下滑，建议分析原因并制定应对策略。"
        ]
    }
}

# 行业特定模板
INDUSTRY_SPECIFIC_TEMPLATES = {
    "construction": {
        "debt_analysis": {
            "high_debt_normal": [
                "建筑行业高负债属于常态，主要由于项目垫资和应收账款周期较长。",
                "建筑业资产负债率普遍较高，公司{value}%的负债率符合行业特征。",
                "关键在于经营现金流能否覆盖债务本息，以及项目回款情况。"
            ],
            "monitor": [
                "建议重点关注：(1) 应收账款周转天数 (2) 经营现金流/利息支出 (3) 新签合同额",
                "建筑企业需保持充足的授信额度和融资能力，以支撑项目垫资需求。"
            ]
        },
        "cashflow_analysis": {
            "negative_ocf": [
                "建筑企业现金流波动较大，主要受项目结算周期影响。",
                "负的经营现金流可能对应大量在建项目，需关注项目进度和结算安排。",
                "建议分析现金流季节性特征，不同季度差异可能较大。"
            ]
        }
    },

    "consumer": {
        "brand_value": [
            "高毛利率显示出强大的品牌溢价能力和市场地位。",
            "品牌护城河是消费品企业的核心竞争优势，需要持续投入维护。",
            "品牌价值的维持需要：持续的产品创新、渠道建设、营销投入。"
        ],
        "channel_analysis": [
            "渠道掌控力是消费品企业的关键成功因素。",
            "建议关注渠道库存情况和渠道利润空间，健康的渠道生态是可持续增长的基础。",
            "电商渠道占比提升可能影响毛利率结构，需要平衡线上线下发展。"
        ]
    },

    "technology": {
        "rd_importance": [
            "研发投入是科技企业的核心竞争力，高研发费用率是必要的战略投入。",
            "技术创新能力决定了长期发展潜力，建议关注专利布局和技术壁垒。",
            "研发投入的产出效率（新产品收入占比）是重要评估指标。"
        ],
        "growth_critical": [
            "成长性是科技企业的核心价值来源，高增长预期支撑估值水平。",
            "市场规模和市场份额增长是关键指标，需要关注行业渗透率。",
            "技术迭代速度快，需要持续创新以保持竞争优势。"
        ]
    },

    "finance": {
        "capital_adequacy": [
            "资本充足率是金融机构的关键指标，直接影响风险承担能力。",
            "需关注风险资产质量和拨备覆盖率，评估风险抵御能力。",
            "净息收受利率环境影响较大，需关注利率变化趋势。"
        ]
    },

    "manufacturing": {
        "capacity_utilization": [
            "产能利用率直接影响盈利能力，需关注产能扩张与需求增长的匹配度。",
            "固定资产周转率是评估产能利用效率的重要指标。",
            "建议关注行业景气周期，合理安排产能投资节奏。"
        ],
        "inventory_management": [
            "存货周转率反映运营效率，过高的存货可能存在跌价风险。",
            "需关注存货结构，区分原材料、在制品、产成品的占比和周转情况。",
            "供应链管理能力是制造业的核心竞争力之一。"
        ]
    }
}

# 建议模板
RECOMMENDATION_TEMPLATES = {
    "strength": {
        "titles": [
            "财务状况优异",
            "核心竞争力突出",
            "具备持续发展潜力"
        ],
        "details": [
            "公司各项财务指标表现优秀，具有较强的抗风险能力和持续发展潜力。",
            "凭借{metric}的优势，公司在行业中处于领先地位。",
            "稳健的财务状况为战略执行提供了坚实基础。"
        ],
        "actions": [
            "可持续关注，重点关注长期战略执行。",
            "建议关注新业务发展和市场拓展情况。",
            "可考虑作为长期投资标的进行跟踪。"
        ]
    },

    "moderate": {
        "titles": [
            "财务状况良好",
            "整体表现稳健"
        ],
        "details": [
            "公司财务状况整体健康，但存在部分需要关注的指标。",
            "各项指标表现良好，但仍有改善空间。",
            "基本面稳健，建议关注薄弱环节的改善情况。"
        ],
        "actions": [
            "建议关注{metric}的变化趋势。",
            "需关注行业景气度和竞争态势变化。",
            "建议定期跟踪财务指标改善情况。"
        ]
    },

    "concern": {
        "titles": [
            "存在财务风险",
            "需要关注的风险点"
        ],
        "details": [
            "公司{metric}表现不佳，存在一定的财务风险。",
            "部分指标低于行业平均水平，需要警惕潜在风险。",
            "建议深入分析{metric}不佳的原因，评估影响程度。"
        ],
        "actions": [
            "建议密切关注{metric}的改善情况。",
            "需评估公司的应对措施和执行能力。",
            "建议谨慎对待，等待改善信号明确后再做决策。"
        ]
    },

    "industry_specific": {
        "construction": [
            "建筑行业高负债属于常态，但需重点关注经营现金流对债务的覆盖。",
            "建议监控：(1) 应收账款周转天数 (2) 经营现金流/利息支出 (3) 新签合同额",
            "新签合同额和在手订单是未来业绩的先行指标，需要重点关注。"
        ],
        "consumer": [
            "高毛利率显示出强大的品牌溢价能力，这是核心竞争优势。",
            "关注品牌投入和渠道建设是否能够维持高毛利。",
            "渠道库存和渠道健康度是持续增长的关键因素。"
        ],
        "technology": [
            "研发投入是科技企业的核心竞争力，高研发费用率是必要的战略投入。",
            "技术创新能力决定了长期发展潜力，建议关注专利布局。",
            "关注新产品推出节奏和市场接受度，评估技术转化效率。"
        ]
    }
}

# 综合评价模板
OVERVIEW_TEMPLATES = {
    "strengths": {
        "high_margin": "强大的盈利能力和高毛利水平",
        "low_debt": "稳健的财务结构和低财务风险",
        "strong_cashflow": "强劲的现金创造能力和充沛的自由现金流",
        "brand_moat": "深厚的品牌护城河和强大的定价能力",
        "leading_position": "行业领先地位和市场份额优势",
        "high_roe": "卓越的股东回报率（ROE）"
    },

    "concerns": {
        "low_turnover": "资产周转率较低（行业特征或需关注效率）",
        "high_debt": "较高的负债水平和财务风险",
        "weak_cashflow": "现金流状况不佳，存在流动性风险",
        "slow_growth": "增长放缓，成长性有待提升",
        "cyclical_risk": "行业周期性波动风险",
        "competition": "行业竞争加剧，市场份额压力"
    },

    "outlooks": {
        "short_term": {
            "positive": "短期业绩稳健，预期保持平稳发展。",
            "neutral": "短期面临一定压力，需关注市场变化。",
            "cautious": "短期存在不确定性，建议谨慎观察。"
        },
        "long_term": {
            "positive": "长期受益于{driver}，发展前景良好。",
            "neutral": "长期发展取决于{factor}的改善情况。",
            "cautious": "长期面临{risk}挑战，需关注应对策略。"
        }
    }
}


def get_template(category: str, rating: str, index: int = 0) -> str:
    """
    获取指定类别和评级的模板

    Args:
        category: 模板类别 (profitability, solvency, etc.)
        rating: 评级 (excellent, good, neutral, concern, critical)
        index: 模板索引（用于多样化）

    Returns:
        模板字符串
    """
    templates = ANALYSIS_TEMPLATES.get(category, {})
    rating_templates = templates.get(rating, [])

    if not rating_templates:
        return "{metric}为{value}%，评级为{rating}。"

    # 循环使用模板
    return rating_templates[index % len(rating_templates)]


def get_industry_template(industry: str, key: str, index: int = 0, sub_key: str = None) -> str:
    """
    获取行业特定模板

    Args:
        industry: 行业ID
        key: 模板key
        index: 模板索引（用于列表）
        sub_key: 子key（用于访问嵌套结构，如 "high_debt_normal"）

    Returns:
        模板字符串或列表
    """
    industry_templates = INDUSTRY_SPECIFIC_TEMPLATES.get(industry, {})
    templates = industry_templates.get(key, [])

    # 如果有子 key，先获取子字典
    if sub_key:
        if isinstance(templates, dict):
            templates = templates.get(sub_key, [])
        else:
            return ""

    if isinstance(templates, list):
        if not templates:
            return ""
        return templates[index % len(templates)]

    return templates


def format_template(template: str, **kwargs) -> str:
    """
    格式化模板字符串

    Args:
        template: 模板字符串
        **kwargs: 模板变量

    Returns:
        格式化后的字符串
    """
    return template.format(**kwargs)
