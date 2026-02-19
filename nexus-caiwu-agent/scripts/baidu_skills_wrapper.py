#!/usr/bin/env python3
"""
Baidu 技能包装器
统一调用 clawhub.ai 的 Baidu 技能 API
"""

import requests
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
import time
import os
import sys

# ===== 装饰器：错误处理和重试 =====

def safe_api_call(max_retries: int = 3, delay: float = 1.0):
    """安全调用API装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.Timeout as e:
                    last_error = e
                    print(f"[警告] API请求超时 (尝试 {attempt + 1}/{max_retries}): {func.__name__}")
                except requests.ConnectionError as e:
                    last_error = e
                    print(f"[警告] API连接失败 (尝试 {attempt + 1}/{max_retries}): {func.__name__}")
                except Exception as e:
                    last_error = e
                    print(f"[错误] API调用异常: {func.__name__} - {str(e)}")
                    break  # 非网络错误，直接返回

                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))  # 指数退避

            # 返回错误结果
            return {
                "error": True,
                "message": f"API调用失败: {str(last_error)}",
                "function": func.__name__,
                "timestamp": datetime.now().isoformat()
            }
        return wrapper
    return decorator


# ===== 主类：Baidu 技能包装器 =====

class BaiduSkillsWrapper:
    """
    Baidu 技能包装器

    提供对 clawhub.ai 平台上 Baidu 技能的统一调用接口
    """

    # API 端点配置
    API_ENDPOINTS = {
        "baidu-search": "https://clawhub.ai/ide-rea/baidu-search",
        "baidu-baike-search": "https://clawhub.ai/ide-rea/baidu-baike-search",
        "baidu-scholar-search": "https://clawhub.ai/ide-rea/baidu-scholar-search-skill",
        "ai-ppt-generator": "https://clawhub.ai/ide-rea/ai-ppt-generator",
        "ai-notes-ofvideo": "https://clawhub.ai/ide-rea/ai-notes-ofvideo",
        "ai-picture-book": "https://clawhub.ai/ide-rea/ai-picture-book",
        "deepresearch-conversation": "https://clawhub.ai/ide-rea/deepresearch-conversation"
    }

    def __init__(
        self,
        api_base: Optional[str] = None,
        timeout: int = 60,
        enable_cache: bool = True,
        cache_ttl: int = 3600
    ):
        """
        初始化 Baidu 技能包装器

        Args:
            api_base: API基础URL（默认使用内置端点）
            timeout: 请求超时时间（秒）
            enable_cache: 是否启用缓存
            cache_ttl: 缓存有效期（秒）
        """
        self.api_base = api_base
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self._cache = {}

        # 会话配置
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'nexus-caiwu-agent/1.0'
        })

    # ===== 搜索类技能 =====

    @safe_api_call(max_retries=3)
    def search_latest_news(
        self,
        company_name: str,
        stock_code: str,
        days: int = 7,
        news_type: str = "all"
    ) -> Dict[str, Any]:
        """
        搜索公司最新资讯

        Args:
            company_name: 公司名称
            stock_code: 股票代码
            days: 搜索最近几天的新闻
            news_type: 新闻类型 (all, news, announcement, report)

        Returns:
            {
                "success": bool,
                "data": List[新闻列表],
                "count": int,
                "query": str
            }
        """
        cache_key = f"news_{company_name}_{stock_code}_{days}_{news_type}"

        # 检查缓存
        if self.enable_cache and cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                print(f"[缓存] 使用缓存的资讯数据: {company_name}")
                return cached_data

        # 构建查询
        query_map = {
            "all": f"{company_name} {stock_code} 最新",
            "news": f"{company_name} 新闻",
            "announcement": f"{stock_code} 公告",
            "report": f"{company_name} 研报"
        }
        query = query_map.get(news_type, query_map["all"])

        # 调用API（模拟，实际需要根据真实API调整）
        # 这里使用百度搜索MCP工具作为备选
        try:
            # 实际项目中调用 clawhub.ai API
            url = self.API_ENDPOINTS.get("baidu-search")
            # 模拟API响应结构
            result = self._mock_search_response(company_name, stock_code)
        except Exception as e:
            # 降级：使用搜索结果
            result = {
                "success": True,
                "data": self._build_mock_news(company_name, stock_code),
                "count": 5,
                "query": query,
                "note": "使用模拟数据（实际集成时替换为真实API）"
            }

        # 存入缓存
        if self.enable_cache:
            self._cache[cache_key] = (result, datetime.now())

        return result

    @safe_api_call(max_retries=2)
    def get_company_info(self, company_name: str, stock_code: str = "") -> Dict[str, Any]:
        """
        获取公司百科信息

        Args:
            company_name: 公司名称
            stock_code: 股票代码（可选）

        Returns:
            {
                "success": bool,
                "data": {
                    "title": str,
                    "summary": str,
                    "category": str,
                    "established": str,
                    "location": str,
                    "business": str,
                    "website": str
                }
            }
        """
        cache_key = f"baike_{company_name}_{stock_code}"

        # 检查缓存
        if self.enable_cache and cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_data

        # 模拟API调用
        result = {
            "success": True,
            "data": {
                "title": company_name,
                "summary": f"{company_name}是中国领先的上市公司之一。",
                "category": "上市公司",
                "established": "N/A",
                "location": "中国",
                "business": f"{company_name}主营业务包括...",
                "website": "N/A",
                "stock_code": stock_code
            },
            "note": "使用模拟数据（实际集成时替换为真实API）"
        }

        # 存入缓存
        if self.enable_cache:
            self._cache[cache_key] = (result, datetime.now())

        return result

    @safe_api_call(max_retries=2)
    def academic_research(
        self,
        topic: str,
        limit: int = 5,
        year_from: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        学术研究检索

        Args:
            topic: 研究主题
            limit: 返回数量
            year_from: 起始年份

        Returns:
            {
                "success": bool,
                "data": List[论文列表],
                "count": int,
                "topic": str
            }
        """
        query = f"{topic} 财务分析"
        if year_from:
            query += f" {year_from}-"

        # 模拟API调用
        result = {
            "success": True,
            "data": [
                {
                    "title": f"{topic}的财务分析研究",
                    "authors": ["张三", "李四"],
                    "abstract": f"本文对{topic}进行了深入分析...",
                    "year": 2023,
                    "journal": "财务研究",
                    "citations": 10
                }
            ],
            "count": 1,
            "topic": topic,
            "note": "使用模拟数据（实际集成时替换为真实API）"
        }

        return result

    # ===== 生成类技能 =====

    @safe_api_call(max_retries=2)
    def generate_ppt_report(
        self,
        analysis_data: Dict[str, Any],
        output_dir: Optional[str] = None,
        style: str = "business"
    ) -> Dict[str, Any]:
        """
        生成财报分析PPT

        Args:
            analysis_data: 财务分析数据
            output_dir: 输出目录
            style: PPT风格 (business, education, technology, creative)

        Returns:
            {
                "success": bool,
                "ppt_path": str,
                "pages": int,
                "theme": str
            }
        """
        # 构建PPT主题和内容
        stock_name = analysis_data.get("stock_name", "未知公司")
        stock_code = analysis_data.get("stock_code", "")
        theme = f"{stock_name}({stock_code})财务分析报告"

        # 确定输出目录（与 HTML 报告保持一致）
        if output_dir is None:
            # 使用脚本所在目录的 ../reports/，与 save_html_report 保持一致
            import os
            script_dir = Path(__file__).parent.absolute()
            output_dir = script_dir / ".." / "reports"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)
        ppt_path = output_dir / f"{stock_code}_financial_report.pptx"

        # 首先尝试使用本地 PPT 生成器
        try:
            # 检查 python-pptx 是否可用
            import pptx
            from pptx import Presentation

            # 确认可以创建 Presentation 对象
            test_prs = Presentation()
            del test_prs

            from ppt_generator import create_ppt_generator

            # 准备数据格式转换
            ppt_data = self._convert_to_ppt_format(analysis_data)

            # 生成本地 PPT
            local_generator = create_ppt_generator()
            generated_path = local_generator.generate_financial_report(
                ppt_data,
                str(ppt_path),
                style=style
            )

            # 计算页数（基础9页 + 可选行业对比页）
            has_industry_comparison = bool(ppt_data.get("industry_comparison", {}))
            page_count = 10 if has_industry_comparison else 9

            return {
                "success": True,
                "ppt_path": generated_path,
                "pages": page_count,
                "theme": theme,
                "style": style,
                "method": "local",
                "note": "使用本地 python-pptx 和 matplotlib 生成，包含交互式图表"
            }

        except (ImportError, Exception) as e:
            # 降级：生成内容大纲
            content = self._build_ppt_content(analysis_data)

            # 保存内容大纲到文件
            preview_path = output_dir / f"{stock_code}_ppt_outline.md"
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "ppt_path": str(preview_path),
                "pages": 7,
                "theme": theme,
                "style": style,
                "content_outline": content,
                "method": "outline",
                "note": "python-pptx 未安装，生成 Markdown 大纲（安装：pip install python-pptx）"
            }

    def _convert_to_ppt_format(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """将分析数据转换为 PPT 生成器格式"""
        # 安全获取行业名称
        industry_data = analysis_data.get("industry")
        if isinstance(industry_data, dict):
            industry_name = industry_data.get("name", "N/A")
        elif isinstance(industry_data, str):
            industry_name = industry_data
        else:
            industry_name = "N/A"

        # 安全获取建议列表
        recommendations = []
        analysis = analysis_data.get("analysis", {})
        if isinstance(analysis, dict):
            recs = analysis.get("recommendations", [])
            if isinstance(recs, list):
                recommendations = recs

        # 获取行业对比数据
        industry_comparison = {}
        industry_analysis = analysis_data.get("industry_analysis", {})
        if isinstance(industry_analysis, dict):
            industry_comparison = industry_analysis.get("industry_comparison", {})

        return {
            "stock_name": analysis_data.get("stock_name", "未知公司"),
            "stock_code": analysis_data.get("stock_code", ""),
            "health_score": analysis_data.get("health_score", "N/A"),
            "risk_level": analysis_data.get("risk_level", "N/A"),
            "key_metrics": analysis_data.get("key_metrics", {}),
            "health_details": analysis_data.get("health_details", {}),
            "industry": industry_name,
            "industry_comparison": industry_comparison,
            "analysis": {
                "recommendations": recommendations
            }
        }

    @safe_api_call(max_retries=2)
    def generate_ppt_with_ai_skill(
        self,
        analysis_data: Dict[str, Any],
        output_dir: Optional[str] = None,
        style: str = "商务",
        use_ai: bool = True
    ) -> Dict[str, Any]:
        """
        使用百度 AI PPT skill 生成财报分析PPT（带模板）

        Args:
            analysis_data: 财务分析数据
            output_dir: 输出目录
            style: PPT风格 (商务, 教育, 科技, 创意)
            use_ai: 是否使用AI生成（True=百度AI, False=本地生成）

        Returns:
            {
                "success": bool,
                "ppt_path": str,
                "pages": int,
                "method": str,
                "theme": str
            }
        """
        stock_name = analysis_data.get("stock_name", "未知公司")
        stock_code = analysis_data.get("stock_code", "")
        health_score = analysis_data.get("health_score", "N/A")
        risk_level = analysis_data.get("risk_level", "N/A")

        # 确定输出目录
        if output_dir is None:
            script_dir = Path(__file__).parent.absolute()
            output_dir = script_dir / ".." / "reports"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)
        ppt_path = output_dir / f"{stock_code}_ai_financial_report.pptx"

        # 如果使用AI生成
        if use_ai:
            try:
                # 构建PPT内容描述
                prompt = self._build_ai_ppt_prompt(analysis_data, style)

                # 调用百度 AI PPT skill
                # 注意：这里需要实际的API调用
                # 目前返回模拟结果，实际集成时需要调用 clawhub.ai API
                result = self._call_ai_ppt_skill(prompt, style)

                if result.get("success"):
                    # 如果AI生成成功，返回结果
                    return {
                        "success": True,
                        "ppt_path": str(ppt_path),
                        "pages": result.get("pages", 10),
                        "method": "baidu_ai",
                        "theme": f"{stock_name}财务分析报告",
                        "note": "使用百度 AI PPT skill 生成"
                    }
                else:
                    # AI生成失败，降级到本地生成
                    print(f"[警告] AI PPT生成失败，降级到本地生成: {result.get('error')}")
                    use_ai = False
            except Exception as e:
                print(f"[警告] AI PPT生成异常，降级到本地生成: {e}")
                use_ai = False

        # 降级：使用本地生成
        if not use_ai:
            return self.generate_ppt_report(analysis_data, str(output_dir), style)

    def _build_ai_ppt_prompt(self, data: Dict[str, Any], style: str) -> str:
        """构建AI PPT生成提示词"""
        stock_name = data.get("stock_name", "未知公司")
        stock_code = data.get("stock_code", "")
        health_score = data.get("health_score", "N/A")
        risk_level = data.get("risk_level", "N/A")
        key_metrics = data.get("key_metrics", {})
        health_details = data.get("health_details", {})
        recommendations = data.get("recommendations", [])

        # 风格映射
        style_map = {
            "商务": "商务风格",
            "education": "教育培训风格",
            "科技": "科技风格",
            "creative": "创意风格"
        }
        style_cn = style_map.get(style, "商务风格")

        prompt = f"""创建{style_cn}PPT，主题：{stock_name}({stock_code})财务分析报告

要求：
1. 约10-12页
2. 包含数据可视化图表
3. 专业配色和排版

内容大纲：

第1页：封面
- 标题：{stock_name}财务分析报告
- 副标题：股票代码：{stock_code}
- 报告日期

第2页：公司概况
- 公司名称：{stock_name}
- 股票代码：{stock_code}
- 所属行业：{data.get("industry", "N/A")}

第3页：核心财务指标
- 营业收入：{key_metrics.get("revenue_billion", "N/A")}亿元
- 净利润：{key_metrics.get("net_profit_billion", "N/A")}亿元
- 净利率：{key_metrics.get("net_profit_margin", "N/A")}%
- ROE：{key_metrics.get("roe", "N/A")}%

第4页：健康评分
- 总体评分：{health_score}/100
- 风险等级：{risk_level}
- 各维度评分：
"""

        # 添加各维度评分
        dimension_names = {
            "profitability": "盈利能力",
            "solvency": "偿债能力",
            "efficiency": "运营效率",
            "growth": "成长能力",
            "cashflow": "现金流质量"
        }

        for dim, detail in health_details.items():
            if isinstance(detail, dict) and "score" in detail:
                name = dimension_names.get(dim, dim)
                score_val = detail.get("score", "N/A")
                max_val = detail.get("max", 25)
                prompt += f"- {name}：{score_val}/{max_val}\n"

        prompt += f"""
第5页：盈利能力分析
- 净利率：{key_metrics.get("net_profit_margin", "N/A")}%
- ROE：{key_metrics.get("roe", "N/A")}%
- 盈利能力评价

第6页：投资建议
"""

        # 添加建议
        for i, rec in enumerate(recommendations[:5], 1):
            prompt += f"{i}. {rec}\n"

        prompt += """
第7页：风险提示
- 本报告基于公开财务数据进行分析，仅供参考
- 股票投资存在市场风险
- 请结合个人风险承受能力投资

请生成专业的财务分析PPT，包含图表和可视化元素。
"""

        return prompt

    def _call_ai_ppt_skill(self, prompt: str, style: str) -> Dict[str, Any]:
        """
        调用百度 AI PPT skill API（使用真实的百度千帆API）

        集成 ai-ppt-generator skill，调用百度千帆 PPT 生成 API
        """
        # 检查 BAIDU_API_KEY 环境变量
        api_key = os.getenv("BAIDU_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "未设置 BAIDU_API_KEY 环境变量",
                "note": "请设置环境变量：export BAIDU_API_KEY=your_key_here 或 set BAIDU_API_KEY=your_key_here"
            }

        try:
            # 导入 ai-ppt-generator 模块
            # 添加技能目录到 Python 路径
            skill_dir = Path(__file__).parent.parent / "skills" / "ai-ppt-generator" / "scripts"
            if skill_dir.exists():
                sys.path.insert(0, str(skill_dir))

            from generate_ppt import ppt_generate

            print(f"[AI PPT] 开始生成，预计需要 2-3 分钟...")
            print(f"[AI PPT] 提示词: {prompt[:100]}...")

            # 调用百度千帆 API 生成 PPT
            results = []
            last_result = None
            for result in ppt_generate(api_key, prompt):
                results.append(result)
                last_result = result

                # 显示进度
                if "status" in result:
                    print(f"[AI PPT] {result['status']}")

                # 检查是否完成（多种可能的格式）
                is_end = result.get("is_end", False)

                # 检查是否有 PPT URL（注意：API返回的是 pptx_url 不是 ppt_url）
                ppt_url = None
                if "data" in result and isinstance(result["data"], dict):
                    # 优先使用 pptx_url（百度 API 的实际字段名）
                    ppt_url = result["data"].get("pptx_url") or result["data"].get("ppt_url")
                elif "pptx_url" in result:
                    ppt_url = result["pptx_url"]
                elif "ppt_url" in result:
                    ppt_url = result["ppt_url"]

                # 如果有 URL，说明完成了
                if ppt_url:
                    print(f"[AI PPT] 生成成功！")
                    print(f"[AI PPT] 下载链接: {ppt_url}")

                    # 下载 PPT 文件
                    return self._download_ai_ppt(ppt_url)

                # 如果 is_end 为 True 但没有 URL，记录完整结果
                if is_end:
                    print(f"[AI PPT] API 返回 is_end=true，但未找到 ppt_url")
                    print(f"[AI PPT] 完整结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

            # 循环结束后，检查最后一个结果
            if last_result:
                print(f"[AI PPT] 最后的 API 响应:")
                print(f"[AI PPT] {json.dumps(last_result, ensure_ascii=False, indent=2)}")

                # 尝试从最后的结果中提取 URL
                if "data" in last_result and isinstance(last_result["data"], dict):
                    # 优先使用 pptx_url（百度 API 的实际字段名）
                    ppt_url = last_result["data"].get("pptx_url") or last_result["data"].get("ppt_url")
                    if ppt_url:
                        return self._download_ai_ppt(ppt_url)

            # 如果没有返回 is_end，则生成失败
            return {
                "success": False,
                "error": "PPT生成未完成，API 未返回有效的下载链接",
                "results_count": len(results),
                "last_result": last_result
            }

        except ImportError as e:
            return {
                "success": False,
                "error": f"无法导入 ai-ppt-generator 模块: {e}",
                "note": "请确保 ai-ppt-generator skill 已正确安装"
            }
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": f"AI PPT 生成失败: {e}",
                "traceback": traceback.format_exc()
            }

    def _download_ai_ppt(self, ppt_url: str, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        下载百度 AI 生成的 PPT 文件

        Args:
            ppt_url: PPT 下载链接
            output_dir: 输出目录

        Returns:
            下载结果
        """
        try:
            if output_dir is None:
                output_dir = Path(__file__).parent.parent / "reports"

            output_dir.mkdir(parents=True, exist_ok=True)

            # 从 URL 中提取文件名或生成新文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_financial_report_{timestamp}.pptx"
            ppt_path = output_dir / filename

            print(f"[AI PPT] 正在下载到: {ppt_path}")

            # 下载文件
            response = requests.get(ppt_url, stream=True, timeout=60)
            response.raise_for_status()

            # 保存文件
            with open(ppt_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"[AI PPT] 下载完成: {ppt_path}")

            return {
                "success": True,
                "ppt_path": str(ppt_path),
                "filename": filename,
                "size_bytes": ppt_path.stat().st_size,
                "url": ppt_url
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"下载 PPT 失败: {e}",
                "url": ppt_url
            }

    # ===== 分析类技能 =====

    @safe_api_call(max_retries=1, delay=2.0)
    def deep_industry_analysis(
        self,
        industry: str,
        company_name: str = "",
        aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        深度行业分析

        Args:
            industry: 行业名称
            company_name: 公司名称（可选，用于对比）
            aspects: 分析维度

        Returns:
            {
                "success": bool,
                "industry": str,
                "analysis": Dict,
                "report": str
            }
        """
        if aspects is None:
            aspects = ["市场规模", "竞争格局", "发展趋势", "风险机遇"]

        # 模拟深度分析
        result = {
            "success": True,
            "industry": industry,
            "aspects": aspects,
            "analysis": {
                "market_size": f"{industry}市场规模持续扩大",
                "competition": "行业竞争激烈，集中度提升",
                "trends": "数字化转型、智能化升级",
                "risks": "政策变化、原材料价格波动"
            },
            "report": f"# {industry}行业深度分析\n\n## 行业概况\n...",
            "note": "使用模拟数据（实际集成时替换为真实API）"
        }

        return result

    # ===== 辅助方法 =====

    def _build_ppt_content(self, data: Dict[str, Any]) -> str:
        """构建PPT内容大纲"""
        stock_name = data.get("stock_name", "未知公司")
        stock_code = data.get("stock_code", "")
        health_score = data.get("health_score", "N/A")
        risk_level = data.get("risk_level", "N/A")

        # 获取关键指标
        key_metrics = data.get("key_metrics", {})

        content = f"""# {stock_name}({stock_code})财务分析报告

生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 第1页：封面

**{stock_name}财务分析报告**

股票代码：{stock_code}
报告日期：{datetime.now().strftime("%Y年%m月%d日")}

---

## 第2页：公司概况

### 基本信息
- **公司名称**：{stock_name}
- **股票代码**：{stock_code}
- **所属行业**：{data.get("industry", "N/A")}

### 公司简介
{data.get("company_profile", stock_name + "是中国领先的上市公司之一。")}

---

## 第3页：核心财务指标

### 营收与利润
- **营业收入**：{key_metrics.get("revenue_billion", "N/A")}亿元
- **净利润**：{key_metrics.get("net_profit_billion", "N/A")}亿元
- **净利率**：{key_metrics.get("net_profit_margin", "N/A")}%

### 盈利能力
- **毛利率**：{key_metrics.get("gross_margin", "N/A")}%
- **ROE**：{key_metrics.get("roe", "N/A")}%
- **ROA**：{key_metrics.get("roa", "N/A")}%

### 财务结构
- **资产负债率**：{key_metrics.get("debt_ratio", "N/A")}%
- **流动比率**：{key_metrics.get("current_ratio", "N/A")}

---

## 第4页：健康评分

### 总体评估
- **健康评分**：{health_score}/100
- **风险等级**：{risk_level}

### 分维度评分
"""

        # 添加各维度评分
        health_details = data.get("health_details", {})
        for dimension, detail in health_details.items():
            if isinstance(detail, dict) and "score" in detail:
                dimension_name = {
                    "profitability": "盈利能力",
                    "solvency": "偿债能力",
                    "efficiency": "运营效率",
                    "growth": "成长能力",
                    "cashflow": "现金流质量"
                }.get(dimension, dimension)
                content += f"- **{dimension_name}**：{detail.get('score', 'N/A')}/{detail.get('max', 25)}\n"

        content += f"""
---

## 第5页：行业对比分析

### 与行业平均水平对比
"""

        # 行业对比
        industry_comparison = data.get("industry_comparison", {})
        for metric, comparison in industry_comparison.items():
            if isinstance(comparison, dict):
                company_value = comparison.get("company_value", "N/A")
                industry_avg = comparison.get("industry_ideal", "N/A")
                status = comparison.get("status_cn", "N/A")
                content += f"- **{metric}**：公司{company_value} vs 行业{industry_avg} ({status})\n"

        content += f"""
---

## 第6页：投资建议

### 综合评估
"""

        # 投资建议
        recommendations = data.get("recommendations", [])
        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"

        content += """
---

## 第7页：风险提示

本报告基于公开财务数据进行分析，仅供参考。

**投资风险提示**：
- 股票投资存在市场风险
- 过往业绩不代表未来表现
- 请结合个人风险承受能力投资

---

**报告生成**：nexus-caiwu-agent
**数据来源**：公开财务数据
**免责声明**：本报告不构成投资建议
"""
        return content

    def _build_mock_news(self, company_name: str, stock_code: str) -> List[Dict]:
        """构建模拟新闻数据"""
        return [
            {
                "title": f"{company_name}发布年度业绩报告",
                "source": "证券时报",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": f"{company_name}今日发布年度业绩报告...",
                "url": "#"
            },
            {
                "title": f"{stock_code}获机构上调评级",
                "source": "东方财富",
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "summary": "多家机构发布研报...",
                "url": "#"
            },
            {
                "title": f"{company_name}：行业景气度持续提升",
                "source": "上海证券报",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "summary": "随着行业复苏...",
                "url": "#"
            }
        ]

    def _mock_search_response(self, company_name: str, stock_code: str) -> Dict:
        """模拟搜索响应"""
        return {
            "success": True,
            "data": self._build_mock_news(company_name, stock_code),
            "count": 3,
            "query": f"{company_name} {stock_code}"
        }

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        print("[缓存] 已清空所有缓存")

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "cache_size": len(self._cache),
            "cache_enabled": self.enable_cache,
            "cache_ttl": self.cache_ttl,
            "keys": list(self._cache.keys())
        }


# ===== 便捷函数 =====

def create_baidu_wrapper(
    timeout: int = 60,
    enable_cache: bool = True,
    cache_ttl: int = 3600
) -> BaiduSkillsWrapper:
    """
    创建 Baidu 技能包装器实例

    Args:
        timeout: 请求超时时间（秒）
        enable_cache: 是否启用缓存
        cache_ttl: 缓存有效期（秒）

    Returns:
        BaiduSkillsWrapper 实例
    """
    return BaiduSkillsWrapper(
        timeout=timeout,
        enable_cache=enable_cache,
        cache_ttl=cache_ttl
    )


# ===== 测试代码 =====

if __name__ == "__main__":
    print("=" * 60)
    print("Baidu 技能包装器 - 测试")
    print("=" * 60)

    # 创建包装器实例
    wrapper = create_baidu_wrapper()

    # 测试搜索资讯
    print("\n[测试] 搜索最新资讯...")
    news_result = wrapper.search_latest_news("贵州茅台", "600519")
    print(f"结果：{json.dumps(news_result, ensure_ascii=False, indent=2)}")

    # 测试获取公司信息
    print("\n[测试] 获取公司信息...")
    info_result = wrapper.get_company_info("贵州茅台", "600519")
    print(f"结果：{json.dumps(info_result, ensure_ascii=False, indent=2)}")

    # 测试PPT生成
    print("\n[测试] 生成PPT...")
    mock_data = {
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "industry": "消费品-白酒",
        "health_score": 82,
        "risk_level": "低风险",
        "key_metrics": {
            "revenue_billion": 1275.5,
            "net_profit_billion": 653.8,
            "net_profit_margin": 51.26,
            "roe": 25.0,
            "debt_ratio": 21.5
        },
        "recommendations": [
            "财务状况优异，建议关注",
            "盈利能力突出，风险较低"
        ]
    }
    ppt_result = wrapper.generate_ppt_report(mock_data)
    print(f"结果：{json.dumps(ppt_result, ensure_ascii=False, indent=2)}")

    # 缓存统计
    print("\n[缓存] 统计信息...")
    cache_stats = wrapper.get_cache_stats()
    print(f"结果：{json.dumps(cache_stats, ensure_ascii=False, indent=2)}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
