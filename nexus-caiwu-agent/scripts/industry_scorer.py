#!/usr/bin/env python3
"""
行业特定评分器
根据行业标准计算财务健康评分
"""

from typing import Dict, List, Any, Optional

from industry_classifier import IndustryClassifier
from industry_benchmarks import get_industry_info


def safe_float(value, default=0.0):
    """安全转换为浮点数"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


class IndustryScorer:
    """行业特定评分器"""

    def __init__(self):
        self.classifier = IndustryClassifier()

    def calculate_metric_score(
        self,
        value: float,
        min_val: float,
        max_val: float,
        ideal: float,
        weight: float = 1.0
    ) -> Dict[str, Any]:
        """
        计算单个指标的得分

        Args:
            value: 实际值
            min_val: 最小可接受值
            max_val: 最大可接受值
            ideal: 理想值
            weight: 权重

        Returns:
            包含得分和评价的字典
        """
        if value is None:
            return {
                "score": 0,
                "weighted_score": 0,
                "rating": "无数据",
                "value": None,
                "industry_range": f"{min_val}-{max_val}",
                "industry_ideal": ideal
            }

        # 计算得分（0-100）
        if min_val <= value <= max_val:
            # 在范围内，越接近ideal越好
            range_width = max_val - min_val
            if range_width == 0:
                score = 100 if value == ideal else 50
            else:
                # 距离理想值的偏差
                deviation = abs(value - ideal)
                # 最大允许偏差是范围宽度的一半
                max_deviation = range_width / 2
                score = max(0, 100 * (1 - deviation / max_deviation))
        else:
            # 超出范围
            if value < min_val:
                # 低于最小值
                score = max(0, 100 * (value / min_val)) if min_val != 0 else 0
            else:
                # 高于最大值
                score = max(0, 100 * (max_val / value)) if value != 0 else 0

        score = round(score, 2)
        weighted_score = round(score * weight, 2)

        # 评级
        if score >= 80:
            rating = "优秀"
        elif score >= 60:
            rating = "良好"
        elif score >= 40:
            rating = "一般"
        elif score >= 20:
            rating = "较差"
        else:
            rating = "差"

        return {
            "score": score,
            "weighted_score": weighted_score,
            "rating": rating,
            "value": round(value, 2),
            "industry_range": f"{min_val}-{max_val}",
            "industry_ideal": ideal
        }

    def calculate_industry_adjusted_score(
        self,
        metrics: Dict[str, float],
        stock_code: str = "",
        company_name: str = "",
        sw_industry: str = None
    ) -> Dict[str, Any]:
        """
        计算行业调整后的评分

        Args:
            metrics: 财务指标字典
            stock_code: 股票代码
            company_name: 公司名称
            sw_industry: 申万行业分类

        Returns:
            包含行业调整评分的字典
        """
        # 1. 识别行业
        industry_id = self.classifier.classify(
            stock_code, company_name, sw_industry
        )
        industry_info = self.classifier.get_industry_info(industry_id)

        # 2. 获取行业基准和特殊规则
        industry_metrics = industry_info.get("metrics", {})
        special_rules = industry_info.get("special_rules", {})

        # 3. 计算各指标得分
        dimension_scores = {}
        total_weighted_score = 0
        total_max_score = 0

        for metric_name, config in industry_metrics.items():
            # 获取实际值（支持百分比和数值两种形式）
            value = metrics.get(metric_name)
            if value is None:
                # 尝试其他可能的字段名
                aliases = {
                    "gross_margin": ["gross_margin", "毛利率"],
                    "net_margin": ["net_profit_margin", "net_margin", "净利率"],
                    "roe": ["roe"],
                    "roa": ["roa"],
                    "debt_ratio": ["debt_ratio", "资产负债率"],
                    "asset_turnover": ["asset_turnover", "资产周转率"],
                    "ocf_to_np": ["ocf_to_np", "现金流/净利润"],
                    "rd_ratio": ["rd_ratio", "研发费用率"]
                }
                for alias in aliases.get(metric_name, [metric_name]):
                    if alias in metrics and metrics[alias] is not None:
                        value = metrics[alias]
                        break

            value = safe_float(value, None)
            if value is None:
                continue

            # 计算得分
            weight = config.get("weight", 0)
            result = self.calculate_metric_score(
                value,
                config.get("min", 0),
                config.get("max", 100),
                config.get("ideal", 50),
                weight
            )

            # 添加指标中文名称
            metric_names_cn = {
                "gross_margin": "毛利率",
                "net_margin": "净利率",
                "roe": "净资产收益率(ROE)",
                "roa": "总资产收益率(ROA)",
                "debt_ratio": "资产负债率",
                "asset_turnover": "总资产周转率",
                "ocf_to_np": "现金流/净利润比",
                "rd_ratio": "研发费用率",
                "cost_to_income": "成本收入比"
            }
            result["name_cn"] = metric_names_cn.get(metric_name, metric_name)

            dimension_scores[metric_name] = result
            total_weighted_score += result["weighted_score"]
            total_max_score += 100 * weight

        # 4. 应用行业特殊规则调整
        adjustment_factor = 1.0
        adjustment_notes = []

        # 高负债容忍度调整
        if special_rules.get("debt_tolerance") == "high":
            debt_ratio = safe_float(metrics.get("debt_ratio", 0))
            if debt_ratio > 70:
                adjustment_notes.append(f"{industry_info['name']}行业高负债为常态")

        # 现金流关键调整
        if special_rules.get("cashflow_critical"):
            ocf_ratio = safe_float(metrics.get("ocf_to_np", 1))
            if ocf_ratio < 0.5:
                adjustment_factor *= 0.8
                adjustment_notes.append("现金流严重恶化，扣减评分")

        # 高研发投入奖励
        if special_rules.get("high_rd_bonus"):
            rd_ratio = safe_float(metrics.get("rd_ratio", 0))
            if rd_ratio > 15:
                adjustment_factor *= 1.1
                adjustment_notes.append("研发投入突出，加分奖励")

        # 5. 计算最终得分
        final_score = round(total_weighted_score * adjustment_factor, 2)
        normalized_score = round(
            (final_score / total_max_score * 100) if total_max_score > 0 else 0,
            2
        )

        # 6. 风险等级
        if normalized_score >= 80:
            risk_level = "低风险"
            risk_class = "low"
        elif normalized_score >= 60:
            risk_level = "中低风险"
            risk_class = "medium-low"
        elif normalized_score >= 40:
            risk_level = "中等风险"
            risk_class = "medium"
        elif normalized_score >= 20:
            risk_level = "中高风险"
            risk_class = "medium-high"
        else:
            risk_level = "高风险"
            risk_class = "high"

        # 7. 行业对比
        industry_comparison = self._generate_comparison(
            metrics, industry_metrics
        )

        return {
            "industry": {
                "id": industry_id,
                "name": industry_info.get("name"),
                "name_en": industry_info.get("name_en"),
                "description": industry_info.get("description")
            },
            "dimension_scores": dimension_scores,
            "raw_score": final_score,
            "normalized_score": normalized_score,
            "max_score": total_max_score,
            "adjustment_factor": round(adjustment_factor, 2),
            "adjustment_notes": adjustment_notes,
            "risk_level": risk_level,
            "risk_class": risk_class,
            "industry_comparison": industry_comparison,
            "recommendations": self._generate_recommendations(
                dimension_scores, industry_id, risk_level
            )
        }

    def _generate_comparison(
        self,
        company_metrics: Dict[str, float],
        industry_metrics: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """生成与行业平均的对比"""
        comparison = {}

        for metric_name, config in industry_metrics.items():
            # 获取公司实际值
            value = company_metrics.get(metric_name)
            if value is None:
                continue

            value = safe_float(value)
            industry_ideal = config.get("ideal", 0)

            if industry_ideal == 0:
                continue

            diff = value - industry_ideal
            diff_pct = (diff / industry_ideal * 100) if industry_ideal != 0 else 0

            # 判断状态
            if abs(diff_pct) <= 10:
                status = "at"
                status_cn = "持平"
            elif diff > 0:
                status = "above"
                status_cn = "优于"
            else:
                status = "below"
                status_cn = "低于"

            comparison[metric_name] = {
                "company_value": round(value, 2),
                "industry_ideal": industry_ideal,
                "difference": round(diff, 2),
                "difference_pct": round(diff_pct, 2),
                "status": status,
                "status_cn": status_cn
            }

        return comparison

    def _generate_recommendations(
        self,
        dimension_scores: Dict[str, Dict],
        industry_id: str,
        risk_level: str
    ) -> List[str]:
        """生成投资建议"""
        recommendations = []

        # 基于风险等级的基本建议
        if risk_level == "低风险":
            recommendations.append("财务状况优秀，行业竞争力强，可考虑配置")
        elif risk_level == "中低风险":
            recommendations.append("财务状况良好，部分指标需关注")
        elif risk_level == "中等风险":
            recommendations.append("财务状况一般，建议深入分析薄弱环节")
        elif risk_level == "中高风险":
            recommendations.append("财务状况需警惕，存在明显风险点")
        else:
            recommendations.append("财务状况高风险，建议回避")

        # 基于行业特性的建议
        industry_info = get_industry_info(industry_id)
        special_rules = industry_info.get("special_rules", {})

        if special_rules.get("cashflow_critical"):
            ocf_score = dimension_scores.get("ocf_to_np", {}).get("score", 0)
            if ocf_score < 40:
                recommendations.append("现金流状况需重点关注")

        if special_rules.get("debt_tolerance") == "high":
            recommendations.append("行业高负债为常态，需关注有息负债成本")

        if special_rules.get("high_rd_bonus"):
            rd_score = dimension_scores.get("rd_ratio", {}).get("score", 0)
            if rd_score >= 60:
                recommendations.append("研发投入较高，长期竞争力有保障")

        # 识别薄弱环节
        weak_metrics = [
            (name, data)
            for name, data in dimension_scores.items()
            if data["score"] < 40
        ]

        if weak_metrics:
            weak_names = [data.get("name_cn", name) for name, data in weak_metrics]
            recommendations.append(f"需关注: {', '.join(weak_names[:3])}")

        return recommendations


# 便捷函数
def analyze_stock_by_industry(
    stock_code: str,
    company_name: str,
    metrics: Dict[str, float],
    sw_industry: str = None
) -> Dict[str, Any]:
    """
    便捷函数：分析股票的行业表现

    Args:
        stock_code: 股票代码
        company_name: 公司名称
        metrics: 财务指标
        sw_industry: 申万行业

    Returns:
        行业分析结果
    """
    scorer = IndustryScorer()
    return scorer.calculate_industry_adjusted_score(
        metrics, stock_code, company_name, sw_industry
    )


if __name__ == "__main__":
    # 测试代码
    scorer = IndustryScorer()

    # 测试案例：贵州茅台（消费品）
    test_metrics = {
        "gross_margin": 51.26,
        "net_profit_margin": 51.26,
        "roe": 22.5,
        "roa": 18.2,
        "debt_ratio": 21.5,
        "asset_turnover": 0.85
    }

    result = scorer.calculate_industry_adjusted_score(
        test_metrics,
        "600519",
        "贵州茅台"
    )

    print("=" * 60)
    print("行业评分测试 - 贵州茅台")
    print("=" * 60)

    print(f"\n行业: {result['industry']['name']}")
    print(f"评分: {result['normalized_score']:.2f}/100")
    print(f"风险等级: {result['risk_level']}")

    print(f"\n指标得分:")
    for name, data in result['dimension_scores'].items():
        print(f"  {data.get('name_cn', name)}: {data['score']:.2f}分 ({data['rating']})")

    print(f"\n行业对比:")
    for name, data in result['industry_comparison'].items():
        print(f"  {name}: {data['status_cn']}行业理想值 {data['difference_pct']:.1f}%")

    print(f"\n建议:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
