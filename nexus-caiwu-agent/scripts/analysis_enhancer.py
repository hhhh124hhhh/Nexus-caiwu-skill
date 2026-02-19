#!/usr/bin/env python3
"""
财务分析增强模块
提供深度分析文字生成功能
"""

from typing import Dict, List, Optional
from analysis_templates import (
    ANALYSIS_TEMPLATES,
    INDUSTRY_SPECIFIC_TEMPLATES,
    RECOMMENDATION_TEMPLATES,
    OVERVIEW_TEMPLATES,
    get_template,
    get_industry_template,
    format_template,
    RATING_MAP
)


class AnalysisEnhancer:
    """财务分析增强器"""

    def __init__(self):
        """初始化增强器"""
        self.rating_map = RATING_MAP

        # 导入行业基准数据
        try:
            from industry_benchmarks import INDUSTRY_BENCHMARKS
            self.industry_benchmarks = INDUSTRY_BENCHMARKS
        except ImportError:
            self.industry_benchmarks = {}

    def _get_rating(self, value: float, benchmarks: Dict[str, float]) -> str:
        """
        根据数值和基准获取评级

        Args:
            value: 指标值
            benchmarks: 基准值 {"min": x, "max": y, "ideal": z}

        Returns:
            评级 (excellent, good, neutral, concern, critical)
        """
        ideal = benchmarks.get("ideal", 0)
        max_val = benchmarks.get("max", 0)
        min_val = benchmarks.get("min", 0)

        # 对于越大越好的指标（如毛利率、ROE）
        if ideal > min_val:
            if value >= ideal:
                return "excellent"
            elif value >= (ideal + min_val) / 2:
                return "good"
            elif value >= min_val:
                return "neutral"
            elif value >= min_val * 0.7:
                return "concern"
            else:
                return "critical"
        # 对于越小越好的指标（如负债率）
        else:
            if value <= ideal:
                return "excellent"
            elif value <= (ideal + max_val) / 2:
                return "good"
            elif value <= max_val:
                return "neutral"
            elif value <= max_val * 1.2:
                return "concern"
            else:
                return "critical"

    def _format_percent(self, value: float, decimals: int = 2) -> str:
        """格式化百分比"""
        return f"{value:.{decimals}f}%"

    def _format_number(self, value: float, unit: str = "亿元") -> str:
        """格式化数字"""
        return f"{value:.2f}{unit}"

    def enhance_profitability_analysis(
        self,
        metrics: Dict,
        industry_info: Optional[Dict] = None
    ) -> Dict:
        """
        盈利能力深度分析

        Args:
            metrics: 财务指标
            industry_info: 行业信息

        Returns:
            增强分析结果
        """
        result = {
            "summary": "",
            "net_margin_analysis": {},
            "roe_analysis": {},
            "gross_margin_analysis": {}
        }

        industry_id = industry_info.get("id", "") if industry_info else ""

        # 从行业基准数据中获取metrics
        benchmarks = {}
        if industry_id and hasattr(self, 'industry_benchmarks'):
            industry_benchmark = self.industry_benchmarks.get(industry_id, {})
            benchmarks = industry_benchmark.get("metrics", {})
        elif industry_info:
            # 如果industry_info中有metrics（兼容性）
            benchmarks = industry_info.get("metrics", {})

        # 净利率分析
        net_margin = metrics.get("net_profit_margin", 0)
        net_margin_benchmark = benchmarks.get("net_margin", {})
        net_margin_rating = self._get_rating(net_margin, net_margin_benchmark)

        result["net_margin_analysis"] = {
            "value": net_margin,
            "rating": self.rating_map.get(net_margin_rating, "一般"),
            "interpretation": format_template(
                get_template("profitability", net_margin_rating, 0),
                metric="净利率",
                value=self._format_percent(net_margin),
                industry_avg=self._format_percent(net_margin_benchmark.get("ideal", 0)),
                ability="盈利能力和成本控制能力",
                aspect="成本控制"
            )
        }

        # 添加行业对比
        if net_margin_benchmark:
            ideal = net_margin_benchmark.get("ideal", 0)
            diff = net_margin - ideal
            if abs(diff) > 5:
                comparison = "高于" if diff > 0 else "低于"
                result["net_margin_analysis"]["industry_comparison"] = \
                    f"{comparison}行业平均水平{abs(diff):.1f}个百分点"

        # 驱动因素分析
        drivers = []
        gross_margin = metrics.get("gross_margin", 0)
        if gross_margin > 50:
            drivers.append(f"高毛利率({self._format_percent(gross_margin)})")

        operating_margin = metrics.get("operating_margin", 0)
        if operating_margin and operating_margin > net_margin * 1.2:
            drivers.append("期间费用控制优秀")

        if drivers:
            result["net_margin_analysis"]["drivers"] = drivers

        # ROE 分析
        roe = metrics.get("roe", 0)
        roe_benchmark = benchmarks.get("roe", {})
        roe_rating = self._get_rating(roe, roe_benchmark)

        result["roe_analysis"] = {
            "value": roe,
            "rating": self.rating_map.get(roe_rating, "一般"),
            "interpretation": format_template(
                get_template("profitability", roe_rating, 1),
                metric="ROE",
                value=self._format_percent(roe),
                industry_avg=self._format_percent(roe_benchmark.get("ideal", 0)),
                ability="股东资金利用效率",
                aspect="资本回报"
            )
        }

        # 杜邦分解
        dupont = metrics.get("dupont_analysis", {})
        if dupont:
            net_margin_dupont = dupont.get("net_margin", 0)
            asset_turnover = dupont.get("asset_turnover", 0)
            equity_multiplier = dupont.get("equity_multiplier", 0)

            # 判断主要驱动力
            contributors = []
            if net_margin_dupont > 15:
                contributors.append("净利率是主要驱动力")
            elif asset_turnover > 0.8:
                contributors.append("周转率贡献显著")
            elif equity_multiplier > 2:
                contributors.append("财务杠杆放大效应")

            if contributors:
                result["roe_analysis"]["dupont_breakdown"] = {
                    "main_driver": contributors[0],
                    "net_margin": self._format_percent(net_margin_dupont),
                    "turnover": f"{asset_turnover:.2f}次",
                    "leverage": f"{equity_multiplier:.2f}倍"
                }

        # 毛利率分析
        gross_margin_rating = self._get_rating(gross_margin, benchmarks.get("gross_margin", {}))
        result["gross_margin_analysis"] = {
            "value": gross_margin,
            "rating": self.rating_map.get(gross_margin_rating, "一般"),
            "interpretation": self._generate_gross_margin_analysis(
                gross_margin, gross_margin_rating, industry_id
            )
        }

        # 汇总
        strengths = []
        concerns = []

        if net_margin_rating in ["excellent", "good"]:
            strengths.append("净利率优异")
        elif net_margin_rating in ["concern", "critical"]:
            concerns.append("净利率偏低")

        if roe_rating in ["excellent", "good"]:
            strengths.append("ROE出色")
        elif roe_rating in ["concern", "critical"]:
            concerns.append("ROE待提升")

        result["summary"] = self._generate_summary("盈利能力", strengths, concerns)

        return {"profitability_detail": result}

    def _generate_gross_margin_analysis(
        self,
        gross_margin: float,
        rating: str,
        industry_id: str
    ) -> str:
        """生成毛利率分析"""
        if rating == "excellent":
            return "高毛利率显示出强大的产品定价能力和品牌溢价，这是核心竞争优势。"
        elif rating == "good":
            return "毛利率处于良好水平，产品具备一定的市场竞争力。"
        elif rating == "neutral":
            return "毛利率处于行业平均水平，产品定价能力一般。"
        else:
            return "毛利率偏低，产品定价能力较弱，建议优化产品结构或降低成本。"

    def enhance_solvency_analysis(
        self,
        metrics: Dict,
        industry_info: Optional[Dict] = None
    ) -> Dict:
        """偿债能力深度分析"""
        result = {
            "summary": "",
            "debt_level_analysis": {},
            "financial_flexibility": ""
        }

        industry_id = industry_info.get("id", "") if industry_info else ""

        # 从行业基准数据中获取metrics
        benchmarks = {}
        if industry_id and hasattr(self, 'industry_benchmarks'):
            industry_benchmark = self.industry_benchmarks.get(industry_id, {})
            benchmarks = industry_benchmark.get("metrics", {})
        elif industry_info:
            benchmarks = industry_info.get("metrics", {})

        # 负债率分析
        debt_ratio = metrics.get("debt_ratio", 0)
        debt_benchmark = benchmarks.get("debt_ratio", {})
        debt_rating = self._get_rating(debt_ratio, debt_benchmark)

        result["debt_level_analysis"] = {
            "value": debt_ratio,
            "rating": self.rating_map.get(debt_rating, "一般"),
            "interpretation": format_template(
                get_template("solvency", debt_rating, 0),
                value=self._format_percent(debt_ratio)
            )
        }

        # 行业特定分析
        if industry_id == "construction" and debt_ratio > 70:
            result["debt_level_analysis"]["industry_context"] = \
                get_industry_template("construction", "debt_analysis", sub_key="high_debt_normal")

        # 财务灵活性
        if debt_rating in ["excellent", "good"]:
            result["financial_flexibility"] = \
                "低负债为公司提供了良好的融资空间和抗风险能力。"
        else:
            result["financial_flexibility"] = \
                "较高的负债水平限制了财务灵活性，需关注偿债压力。"

        # 汇总
        result["summary"] = self._generate_summary(
            "偿债能力",
            ["财务结构稳健"] if debt_rating in ["excellent", "good"] else [],
            ["负债率较高"] if debt_rating in ["concern", "critical"] else []
        )

        return {"solvency_detail": result}

    def enhance_efficiency_analysis(
        self,
        metrics: Dict,
        industry_info: Optional[Dict] = None
    ) -> Dict:
        """运营效率深度分析"""
        result = {
            "summary": "",
            "turnover_analysis": {},
            "industry_context": ""
        }

        industry_id = industry_info.get("id", "") if industry_info else ""

        # 从行业基准数据中获取metrics
        benchmarks = {}
        if industry_id and hasattr(self, 'industry_benchmarks'):
            industry_benchmark = self.industry_benchmarks.get(industry_id, {})
            benchmarks = industry_benchmark.get("metrics", {})
        elif industry_info:
            benchmarks = industry_info.get("metrics", {})

        # 资产周转率分析
        asset_turnover = metrics.get("asset_turnover", 0)
        turnover_benchmark = benchmarks.get("asset_turnover", {})
        turnover_rating = self._get_rating(asset_turnover, turnover_benchmark)

        result["turnover_analysis"] = {
            "value": asset_turnover,
            "rating": self.rating_map.get(turnover_rating, "一般"),
            "interpretation": format_template(
                get_template("efficiency", turnover_rating, 0),
                value=f"{asset_turnover:.2f}",
                industry_avg=f"{turnover_benchmark.get('ideal', 0):.2f}"
            )
        }

        # 行业特性说明
        gross_margin = metrics.get("gross_margin", 0)
        if gross_margin > 40 and asset_turnover < 0.6:
            result["industry_context"] = \
                get_industry_template("efficiency", "high_margin_low_turnover", 0).format(
                    industry=industry_info.get("name", "该")
                )
        elif gross_margin < 20 and asset_turnover > 0.8:
            result["industry_context"] = \
                get_industry_template("efficiency", "low_margin_high_turnover", 0)

        # 汇总
        result["summary"] = self._generate_summary(
            "运营效率",
            ["资产利用效率高"] if turnover_rating in ["excellent", "good"] else [],
            ["周转率偏低"] if turnover_rating in ["concern", "critical"] else []
        )

        return {"efficiency_detail": result}

    def enhance_cashflow_analysis(
        self,
        metrics: Dict,
        industry_info: Optional[Dict] = None
    ) -> Dict:
        """现金流深度分析"""
        result = {
            "summary": "",
            "quality_analysis": {},
            "structure_analysis": "",
            "free_cashflow_analysis": {}
        }

        # 现金流质量分析
        ocf_to_np = metrics.get("ocf_to_np", 0)

        if ocf_to_np > 100:
            quality_rating = "excellent"
        elif ocf_to_np > 80:
            quality_rating = "good"
        elif ocf_to_np > 50:
            quality_rating = "neutral"
        elif ocf_to_np > 0:
            quality_rating = "concern"
        else:
            quality_rating = "critical"

        result["quality_analysis"] = {
            "value": ocf_to_np,
            "rating": self.rating_map.get(quality_rating, "一般"),
            "interpretation": format_template(
                get_template("cashflow", quality_rating, 0),
                value=f"{ocf_to_np:.1f}"
            )
        }

        # 自由现金流分析
        free_cf = metrics.get("free_cash_flow_billion", 0)
        if free_cf > 0:
            result["free_cashflow_analysis"] = {
                "value": free_cf,
                "interpretation": format_template(
                    get_industry_template("cashflow", "free_cash_flow", "positive_strong"),
                    value=self._format_number(free_cf)
                )
            }
        else:
            result["free_cashflow_analysis"] = {
                "value": free_cf,
                "interpretation": format_template(
                    get_industry_template("cashflow", "free_cash_flow", "negative"),
                    value=self._format_number(free_cf)
                )
            }

        # 汇总
        result["summary"] = self._generate_summary(
            "现金流质量",
            ["现金创造能力强"] if quality_rating in ["excellent", "good"] else [],
            ["现金流偏弱"] if quality_rating in ["concern", "critical"] else []
        )

        return {"cashflow_detail": result}

    def generate_smart_recommendations(
        self,
        health_result: Dict,
        industry_analysis: Optional[Dict],
        metrics: Dict
    ) -> List[Dict]:
        """生成智能建议"""
        recommendations = []

        total_score = health_result.get("total_score", 0)

        # 基于总体评分的建议
        if total_score >= 80:
            recommendations.append({
                "type": "strength",
                "title": "财务状况优异",
                "detail": "公司各项财务指标表现优秀，具有较强的抗风险能力和持续发展潜力。",
                "action": "可持续关注，重点关注长期战略执行。"
            })
        elif total_score >= 60:
            recommendations.append({
                "type": "moderate",
                "title": "财务状况良好",
                "detail": "公司财务状况整体健康，但存在部分需要关注的指标。",
                "action": "建议关注薄弱环节的改善情况。"
            })
        elif total_score >= 40:
            recommendations.append({
                "type": "concern",
                "title": "存在改善空间",
                "detail": "公司财务状况一般，部分指标低于行业平均水平。",
                "action": "建议关注各项指标的改善情况，评估公司的应对措施。"
            })
        else:
            recommendations.append({
                "type": "concern",
                "title": "存在财务风险",
                "detail": "公司多项财务指标表现不佳，存在一定的财务风险。",
                "action": "建议谨慎对待，等待改善信号明确后再做决策。"
            })

        # 行业特定建议
        if industry_analysis:
            industry_id = industry_analysis.get("industry", {}).get("id", "")
            industry_specific = RECOMMENDATION_TEMPLATES.get("industry_specific", {}).get(industry_id, [])
            for template in industry_specific[:2]:  # 最多2条行业建议
                recommendations.append({
                    "type": "industry_specific",
                    "title": "行业特点提示",
                    "detail": template,
                    "action": "请结合行业特性进行综合分析。"
                })

        # 基于各维度评分的针对性建议
        for dimension, detail in health_result.items():
            if isinstance(detail, dict) and "score" in detail:
                score = detail.get("score", 0)
                max_score = detail.get("max", 25)
                detail_text = detail.get("detail", "")

                if score < max_score * 0.5:  # 得分低于50%
                    dimension_name = {
                        "profitability": "盈利能力",
                        "solvency": "偿债能力",
                        "efficiency": "运营效率",
                        "growth": "成长能力",
                        "cashflow": "现金流质量"
                    }.get(dimension, dimension)

                    recommendations.append({
                        "type": "dimension_specific",
                        "title": f"{dimension_name}需关注",
                        "detail": f"{dimension_name}评分较低（{detail_text}），建议分析原因并制定改善计划。",
                        "action": f"重点关注{dimension_name}相关的关键指标变化趋势。"
                    })

        return recommendations

    def generate_comprehensive_assessment(
        self,
        health_result: Dict,
        metrics: Dict,
        industry_info: Optional[Dict] = None
    ) -> Dict:
        """生成综合评价"""
        strengths = []
        concerns = []

        # 基于评分提取优势和关注点
        for dimension, detail in health_result.items():
            if isinstance(detail, dict) and "score" in detail:
                score = detail.get("score", 0)
                max_score = detail.get("max", 25)

                if score >= max_score * 0.8:  # 80%以上为优势
                    dimension_name = {
                        "profitability": "盈利能力",
                        "solvency": "偿债能力",
                        "efficiency": "运营效率",
                        "growth": "成长能力",
                        "cashflow": "现金流质量"
                    }.get(dimension, dimension)

                    if dimension == "profitability":
                        strengths.append("卓越的盈利能力和高ROE水平")
                    elif dimension == "solvency":
                        strengths.append("稳健的财务结构和低财务风险")
                    elif dimension == "cashflow":
                        strengths.append("强劲的现金创造能力")
                    else:
                        strengths.append(f"优秀的{dimension_name}")

                elif score < max_score * 0.5:  # 50%以下为关注点
                    if dimension == "profitability":
                        concerns.append("盈利能力偏弱")
                    elif dimension == "solvency":
                        concerns.append("较高的负债水平")
                    elif dimension == "cashflow":
                        concerns.append("现金流状况不佳")
                    elif dimension == "efficiency":
                        concerns.append("运营效率有待提升")

        # 投资展望
        total_score = health_result.get("total_score", 0)
        if total_score >= 80:
            short_term = "短期业绩稳健，预期保持平稳发展。"
            long_term = "长期发展前景良好，具备持续竞争优势。"
        elif total_score >= 60:
            short_term = "短期业绩基本稳定，需关注市场变化。"
            long_term = "长期发展取决于各项指标的改善情况。"
        elif total_score >= 40:
            short_term = "短期面临一定压力，需谨慎观察。"
            long_term = "长期发展存在不确定性，需关注应对策略。"
        else:
            short_term = "短期存在较大不确定性，建议谨慎对待。"
            long_term = "长期面临挑战，需要密切关注改善措施。"

        return {
            "strengths": strengths if strengths else ["暂无特别优势"],
            "concerns": concerns if concerns else ["整体表现均衡"],
            "investment_outlook": {
                "short_term": short_term,
                "long_term": long_term
            }
        }

    def enhance_analysis(
        self,
        metrics: Dict,
        health_result: Dict,
        industry_analysis: Optional[Dict],
        stock_code: str,
        stock_name: str
    ) -> Dict:
        """
        综合增强分析

        Args:
            metrics: 财务指标
            health_result: 健康评分结果
            industry_analysis: 行业分析结果
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            增强分析结果
        """
        enhanced = {}

        industry_info = industry_analysis.get("industry", {}) if industry_analysis else None

        # 各维度深度分析
        enhanced.update(self.enhance_profitability_analysis(metrics, industry_info))
        enhanced.update(self.enhance_solvency_analysis(metrics, industry_info))
        enhanced.update(self.enhance_efficiency_analysis(metrics, industry_info))
        enhanced.update(self.enhance_cashflow_analysis(metrics, industry_info))

        # 智能建议
        enhanced["smart_recommendations"] = self.generate_smart_recommendations(
            health_result, industry_analysis, metrics
        )

        # 综合评价
        enhanced["overall_assessment"] = self.generate_comprehensive_assessment(
            health_result, metrics, industry_info
        )

        return enhanced

    def _generate_summary(
        self,
        dimension: str,
        strengths: List[str],
        concerns: List[str]
    ) -> str:
        """生成维度汇总"""
        parts = [f"{dimension}分析："]

        if strengths:
            parts.append("优势方面：" + "、".join(strengths) + "。")

        if concerns:
            parts.append("需要关注：" + "、".join(concerns) + "。")
        else:
            parts.append("各项指标表现良好。")

        return "".join(parts)
