#!/usr/bin/env python3
"""
行业分类器
根据股票代码、公司名称或申万行业分类识别股票所属行业
"""

import re
from typing import Optional, Dict, List, Tuple

from industry_benchmarks import (
    INDUSTRY_BENCHMARKS,
    SW_INDUSTRY_MAPPING,
    get_industry_info,
    get_industry_by_sw
)


class IndustryClassifier:
    """行业分类器"""

    def __init__(self):
        self.benchmarks = INDUSTRY_BENCHMARKS
        self.sw_mapping = SW_INDUSTRY_MAPPING

    def classify_by_stock_code(self, stock_code: str) -> Optional[str]:
        """
        根据股票代码分类

        Args:
            stock_code: 股票代码（6位数字）

        Returns:
            行业ID，如 'technology', 'manufacturing' 等
        """
        code = stock_code.strip().zfill(6)

        # 科创板：以 688 开头，高科技为主
        if code.startswith("688"):
            return "technology"

        # 创业板：以 300 开头，成长型企业
        if code.startswith("300"):
            # 创业板公司需要结合其他信息判断，默认为科技
            return "technology"

        # 北交所：以 8、4 开头
        if code.startswith(("8", "4")):
            return "manufacturing"

        # 检查各行业的股票示例
        for industry_id, industry_data in self.benchmarks.items():
            if "stock_examples" in industry_data:
                if code in industry_data["stock_examples"]:
                    return industry_id

        # 检查股票代码模式
        for industry_id, industry_data in self.benchmarks.items():
            if "stock_patterns" in industry_data:
                for pattern in industry_data["stock_patterns"]:
                    if code.startswith(pattern):
                        return industry_id

        return None

    def classify_by_name(self, company_name: str) -> Dict[str, float]:
        """
        根据公司名称分类（返回多个行业及置信度）

        Args:
            company_name: 公司名称

        Returns:
            行业ID到置信度的字典
        """
        scores = {}
        name = company_name.lower()

        for industry_id, industry_data in self.benchmarks.items():
            score = 0
            keywords = industry_data.get("keywords", [])

            for keyword in keywords:
                if keyword.lower() in name:
                    score += 1

            # 完全匹配的关键词权重更高
            for keyword in keywords:
                if keyword.lower() == name or name.startswith(keyword.lower()):
                    score += 2

            if score > 0:
                # 归一化分数
                scores[industry_id] = score / len(keywords)

        return scores

    def classify_by_sw_industry(self, sw_industry: str) -> Optional[str]:
        """
        根据申万行业分类

        Args:
            sw_industry: 申万行业名称

        Returns:
            行业ID
        """
        return get_industry_by_sw(sw_industry)

    def classify(
        self,
        stock_code: str,
        company_name: str = None,
        sw_industry: str = None
    ) -> str:
        """
        综合分类

        Args:
            stock_code: 股票代码
            company_name: 公司名称（可选）
            sw_industry: 申万行业分类（可选）

        Returns:
            行业ID (如 'technology', 'manufacturing' 等)
        """
        # 1. 优先使用申万行业分类（最准确）
        if sw_industry:
            industry = self.classify_by_sw_industry(sw_industry)
            if industry and industry != "manufacturing":  # manufacturing 是默认值
                return industry

        # 2. 根据股票代码分类
        industry = self.classify_by_stock_code(stock_code)
        if industry:
            return industry

        # 3. 根据公司名称分类
        if company_name:
            name_scores = self.classify_by_name(company_name)
            if name_scores:
                # 返回置信度最高的行业
                return max(name_scores.items(), key=lambda x: x[1])[0]

        # 4. 默认为制造业
        return "manufacturing"

    def get_industry_info(self, industry_id: str) -> Dict:
        """
        获取行业信息

        Args:
            industry_id: 行业ID

        Returns:
            行业信息字典
        """
        return get_industry_info(industry_id)

    def get_industry_matches(
        self,
        stock_code: str,
        company_name: str = None,
        sw_industry: str = None
    ) -> List[Tuple[str, float, str]]:
        """
        获取所有可能的行业匹配结果

        Args:
            stock_code: 股票代码
            company_name: 公司名称
            sw_industry: 申万行业

        Returns:
            行业匹配列表，每项为 (行业ID, 置信度, 匹配来源)
        """
        matches = []

        # 申万行业分类（权重最高）
        if sw_industry:
            industry = self.classify_by_sw_industry(sw_industry)
            if industry:
                matches.append((industry, 1.0, f"申万行业: {sw_industry}"))

        # 股票代码匹配
        code_industry = self.classify_by_stock_code(stock_code)
        if code_industry:
            confidence = 0.8 if stock_code.startswith("688") else 0.6
            matches.append((code_industry, confidence, "股票代码模式"))

        # 公司名称匹配
        if company_name:
            name_scores = self.classify_by_name(company_name)
            for industry_id, score in sorted(name_scores.items(), key=lambda x: -x[1]):
                matches.append((
                    industry_id,
                    score * 0.5,  # 名称匹配权重较低
                    f"公司名称关键词: {company_name}"
                ))

        return matches

    def get_industry_benchmarks(self, industry_id: str) -> Dict:
        """获取行业基准指标"""
        industry_info = self.get_industry_info(industry_id)
        return industry_info.get("metrics", {})

    def get_industry_special_rules(self, industry_id: str) -> Dict:
        """获取行业特殊规则"""
        industry_info = self.get_industry_info(industry_id)
        return industry_info.get("special_rules", {})


# 便捷函数
def classify_stock(
    stock_code: str,
    company_name: str = None,
    sw_industry: str = None
) -> str:
    """
    便捷函数：分类股票

    Args:
        stock_code: 股票代码
        company_name: 公司名称
        sw_industry: 申万行业

    Returns:
        行业ID
    """
    classifier = IndustryClassifier()
    return classifier.classify(stock_code, company_name, sw_industry)


def get_industry_name(industry_id: str) -> str:
    """获取行业中文名称"""
    info = get_industry_info(industry_id)
    return info.get("name", "未知行业")


def get_all_industries() -> List[str]:
    """获取所有行业ID列表"""
    return list(INDUSTRY_BENCHMARKS.keys())


if __name__ == "__main__":
    # 测试代码
    classifier = IndustryClassifier()

    # 测试案例
    test_cases = [
        ("600519", "贵州茅台", None),  # 消费品
        ("688981", "中芯国际", None),   # 科技
        ("601668", "中国建筑", None),   # 建筑
        ("000001", "平安银行", None),   # 金融
        ("600031", "三一重工", None),   # 制造
        ("000002", "万科A", None),      # 房地产
    ]

    print("=" * 60)
    print("行业分类测试")
    print("=" * 60)

    for code, name, sw in test_cases:
        industry_id = classifier.classify(code, name, sw)
        industry_name = get_industry_name(industry_id)
        matches = classifier.get_industry_matches(code, name, sw)

        print(f"\n【{name} ({code})】")
        print(f"  分类结果: {industry_name} ({industry_id})")

        if matches:
            print(f"  匹配详情:")
            for match_industry, confidence, source in matches:
                match_name = get_industry_name(match_industry)
                print(f"    - {match_name}: {confidence:.2f} ({source})")
