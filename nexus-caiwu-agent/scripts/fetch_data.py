#!/usr/bin/env python3
"""
A股财务数据获取脚本（增强版）
- 自动检测 Python 环境
- 自动安装缺失的依赖包
- 支持国内直连和代理两种模式
- 支持数据持久化保存
- 支持 Baidu AI 技能增强（PPT生成、资讯获取、深度分析）

用法:
  # 基本使用
  python fetch_data.py <股票代码> [股票名称] [--analyze] [--save] [--output DIR]

  # 网络模式选项
  python fetch_data.py 600519 --mode auto         # 自动检测（默认）
  python fetch_data.py 600519 --mode direct       # 国内直连
  python fetch_data.py 600519 --mode proxy --proxy http://127.0.0.1:7890
  python fetch_data.py 600519 --mode proxy --proxy socks5://127.0.0.1:1080

  # 增强分析选项
  python fetch_data.py 600519 --analyze --enhance # 启用增强文字分析
  python fetch_data.py 600519 --analyze --html    # 生成 HTML 报告
  python fetch_data.py 600519 --analyze --ppt     # 生成 PPT 报告
  python fetch_data.py 600519 --analyze --news    # 获取最新资讯
  python fetch_data.py 600519 --analyze --baike   # 获取公司百科信息
  python fetch_data.py 600519 --analyze --deep-analysis  # 深度行业分析

  # 综合使用
  python fetch_data.py 600519 --analyze --enhance --html --ppt --news

  # 环境变量方式
  export NET_MODE=proxy
  export HTTP_PROXY=http://127.0.0.1:7890
  python fetch_data.py 600519

  # 网络检测
  python fetch_data.py --detect-network
  python fetch_data.py --test-proxy http://127.0.0.1:7890
"""

import sys
import os
import subprocess
import json
from datetime import datetime

# 尝试导入网络模块，如果失败则使用 fallback
try:
    from network_client import NetworkClient, get_config
    HAS_NETWORK_CLIENT = True
except ImportError:
    HAS_NETWORK_CLIENT = False
    print("[提示] 网络增强模块不可用，使用基本模式")

# 尝试导入行业分析模块
try:
    from industry_classifier import IndustryClassifier
    from industry_scorer import IndustryScorer
    HAS_INDUSTRY_ANALYSIS = True
except ImportError:
    HAS_INDUSTRY_ANALYSIS = False
    print("[提示] 行业分析模块不可用")

# 尝试导入 Baidu 技能包装模块
try:
    from baidu_skills_wrapper import BaiduSkillsWrapper, create_baidu_wrapper
    HAS_BAIDU_SKILLS = True
except ImportError:
    HAS_BAIDU_SKILLS = False
    print("[提示] Baidu 技能模块不可用，--ppt/--news/--baike/--deep-analysis 功能将不可用")

# 尝试导入视频生成模块
try:
    from video_generator import VideoGenerator, create_video_generator
    HAS_VIDEO_GENERATOR = True
except ImportError:
    HAS_VIDEO_GENERATOR = False
    print("[提示] 视频生成模块不可用，--video 功能将不可用")

# ===== 环境检测和依赖安装 =====

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[错误] Python 版本过低: {version.major}.{version.minor}")
        print("需要 Python 3.8 或更高版本")
        return False
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_package(package_name: str) -> bool:
    """检查包是否已安装"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def get_package_version(package_name: str) -> str:
    """获取已安装包的版本"""
    try:
        import importlib.metadata
        return importlib.metadata.version(package_name)
    except:
        return "未知"

def install_package(package_name: str, quiet: bool = True) -> bool:
    """安装 Python 包"""
    print(f"[安装] 正在安装 {package_name}...")
    try:
        cmd = [sys.executable, "-m", "pip", "install", package_name]
        if quiet:
            cmd.append("-q")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] {package_name} 安装成功")
            return True
        else:
            print(f"[错误] {package_name} 安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"[错误] 安装过程出错: {e}")
        return False

def ensure_dependencies(auto_install: bool = True) -> bool:
    """
    确保所有依赖都已安装

    Args:
        auto_install: 如果为 True，自动安装缺失的依赖

    Returns:
        是否所有依赖都可用
    """
    required_packages = [
        ("akshare", "akshare>=1.12.0"),
        ("pandas", "pandas>=2.0.0"),
    ]

    all_ok = True
    missing = []

    print("\n" + "="*50)
    print("[检查] 依赖环境")
    print("="*50)

    for import_name, pip_name in required_packages:
        if check_package(import_name):
            version = get_package_version(import_name)
            print(f"[OK] {import_name} ({version})")
        else:
            print(f"[缺失] {import_name}")
            missing.append(pip_name)
            all_ok = False

    if missing:
        if auto_install:
            print("\n[安装] 正在安装缺失的依赖...")
            for package in missing:
                if not install_package(package):
                    return False
            # 重新检查
            for import_name, _ in required_packages:
                if not check_package(import_name):
                    print(f"[错误] {import_name} 安装后仍无法导入")
                    return False
            print("\n[OK] 所有依赖已安装")
            return True
        else:
            print("\n[提示] 请手动安装缺失的依赖:")
            print(f"  pip install {' '.join(missing)}")
            return False

    return True

def check_environment(auto_install: bool = True) -> dict:
    """
    检查完整的环境状态

    Returns:
        环境状态字典
    """
    status = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_executable": sys.executable,
        "packages": {},
        "all_ok": False
    }

    packages_to_check = ["akshare", "pandas", "numpy"]

    for pkg in packages_to_check:
        if check_package(pkg):
            status["packages"][pkg] = {
                "installed": True,
                "version": get_package_version(pkg)
            }
        else:
            status["packages"][pkg] = {
                "installed": False,
                "version": None
            }

    status["all_ok"] = all(p["installed"] for p in status["packages"].values())

    return status

# ===== 核心功能 =====

def convert_stock_code(stock_code: str) -> str:
    """转换股票代码格式为 AKShare 需要的格式"""
    stock_code = stock_code.strip()
    if stock_code.startswith('6'):
        return f"SH{stock_code}"
    elif stock_code.startswith('0') or stock_code.startswith('3'):
        return f"SZ{stock_code}"
    elif stock_code.startswith('68'):
        return f"SH{stock_code}"
    elif stock_code.startswith('8') or stock_code.startswith('4'):
        return f"BJ{stock_code}"
    else:
        return stock_code

def safe_float(value, default=0.0):
    """安全转换为浮点数"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def get_financial_data(stock_code: str, stock_name: str = None,
                      network_mode: str = None, proxy_url: str = None) -> dict:
    """
    获取股票财务数据

    Args:
        stock_code: 股票代码，如 '600519'
        stock_name: 股票名称，可选
        network_mode: 网络模式 ('auto', 'direct', 'proxy')
        proxy_url: 代理地址 (如 'http://127.0.0.1:7890' 或 'socks5://127.0.0.1:1080')

    Returns:
        包含财务数据的字典
    """
    if stock_name is None:
        stock_name = f"股票{stock_code}"

    # 使用增强网络客户端（如果可用）
    if HAS_NETWORK_CLIENT:
        client = NetworkClient(mode=network_mode or "auto", proxy_url=proxy_url)
        return client.fetch_financial_data(stock_code, stock_name)

    # Fallback: 原始实现
    import akshare as ak

    symbol = convert_stock_code(stock_code)
    print(f"\n[获取] {stock_name}({stock_code}) 的财务数据...")
    print(f"[代码] AKShare symbol: {symbol}")

    result = {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "symbol": symbol,
        "fetch_time": datetime.now().isoformat(),
        "data": {},
        "success": False
    }

    try:
        # 1. 获取利润表
        print("  [1/3] 利润表...")
        try:
            income_df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
            result["data"]["income"] = income_df.head(4).to_dict(orient="records")
            print(f"        OK ({len(income_df)} 条)")
        except Exception as e:
            print(f"        失败: {e}")
            result["data"]["income"] = []

        # 2. 获取资产负债表
        print("  [2/3] 资产负债表...")
        try:
            balance_df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
            result["data"]["balance"] = balance_df.head(4).to_dict(orient="records")
            print(f"        OK ({len(balance_df)} 条)")
        except Exception as e:
            print(f"        失败: {e}")
            result["data"]["balance"] = []

        # 3. 获取现金流量表
        print("  [3/3] 现金流量表...")
        try:
            cashflow_df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
            result["data"]["cashflow"] = cashflow_df.head(4).to_dict(orient="records")
            print(f"        OK ({len(cashflow_df)} 条)")
        except Exception as e:
            print(f"        失败: {e}")
            result["data"]["cashflow"] = []

        # 4. 提取关键指标
        print("  [提取] 关键指标...")
        if result["data"]["income"]:
            latest = result["data"]["income"][0]
            balance = result["data"]["balance"][0] if result["data"].get("balance") else {}
            result["key_metrics"] = extract_key_metrics(latest, balance)
            print(f"        OK ({len(result['key_metrics'])} 个)")
        else:
            result["key_metrics"] = {}

        result["success"] = True
        print(f"\n[完成] 数据获取成功!")

    except Exception as e:
        result["error"] = str(e)
        print(f"\n[错误] {e}")

    return result

def extract_key_metrics(income: dict, balance: dict) -> dict:
    """从财务数据中提取关键指标"""
    metrics = {}

    # 营业收入（亿元）
    for col in ['TOTAL_OPERATE_INCOME', '营业收入', 'operating_revenue', '营业总收入']:
        if col in income and income[col] is not None:
            metrics['revenue_billion'] = safe_float(income[col]) / 1e8
            break

    # 净利润（亿元）
    for col in ['NETPROFIT', '净利润', 'net_profit', '归属于母公司所有者的净利润']:
        if col in income and income[col] is not None:
            metrics['net_profit_billion'] = safe_float(income[col]) / 1e8
            break

    # 净利率
    if 'revenue_billion' in metrics and 'net_profit_billion' in metrics:
        if metrics['revenue_billion'] > 0:
            metrics['net_profit_margin'] = round(
                metrics['net_profit_billion'] / metrics['revenue_billion'] * 100, 2
            )

    # 总资产（亿元）
    for col in ['TOTAL_ASSETS', '资产总计', 'total_assets']:
        if col in balance and balance[col] is not None:
            metrics['total_assets_billion'] = safe_float(balance[col]) / 1e8
            break

    # 总负债（亿元）
    for col in ['TOTAL_LIABILITIES', '负债合计', 'total_liabilities']:
        if col in balance and balance[col] is not None:
            metrics['total_liabilities_billion'] = safe_float(balance[col]) / 1e8
            break

    # 资产负债率
    if 'total_assets_billion' in metrics and 'total_liabilities_billion' in metrics:
        if metrics['total_assets_billion'] > 0:
            metrics['debt_ratio'] = round(
                metrics['total_liabilities_billion'] / metrics['total_assets_billion'] * 100, 2
            )

    return metrics

def calculate_advanced_metrics(income: dict, balance: dict, cashflow: dict = None) -> dict:
    """
    计算高级财务指标

    Args:
        income: 利润表数据
        balance: 资产负债表数据
        cashflow: 现金流量表数据（可选）

    Returns:
        高级财务指标字典
    """
    metrics = {}

    # 提取基础数据
    revenue = safe_float(income.get('TOTAL_OPERATE_INCOME') or income.get('营业收入') or income.get('营业总收入') or 0)
    cost = safe_float(income.get('TOTAL_OPERATE_COST') or income.get('营业成本') or 0)
    net_profit = safe_float(income.get('NETPROFIT') or income.get('净利润') or income.get('归属于母公司所有者的净利润') or 0)
    operating_profit = safe_float(income.get('OPERATE_PROFIT') or income.get('营业利润') or 0)

    total_assets = safe_float(balance.get('TOTAL_ASSETS') or balance.get('资产总计') or 0)
    total_liabilities = safe_float(balance.get('TOTAL_LIABILITIES') or balance.get('负债合计') or 0)
    current_assets = safe_float(balance.get('TOTAL_CURRENT_ASSETS') or balance.get('流动资产合计') or 0)
    current_liabilities = safe_float(balance.get('TOTAL_CURRENT_LIABILITIES') or balance.get('流动负债合计') or 0)
    inventory = safe_float(balance.get('INVENTORY') or balance.get('存货') or 0)

    # 净资产（股东权益）
    equity = total_assets - total_liabilities

    # 盈利能力指标
    if revenue > 0:
        metrics['gross_margin'] = round((revenue - cost) / revenue * 100, 2) if cost else None
        metrics['operating_margin'] = round(operating_profit / revenue * 100, 2) if operating_profit else None

    if equity > 0:
        metrics['roe'] = round(net_profit / equity * 100, 2) if net_profit else None

    if total_assets > 0:
        metrics['roa'] = round(net_profit / total_assets * 100, 2) if net_profit else None

    # 偿债能力指标
    if current_liabilities > 0:
        metrics['current_ratio'] = round(current_assets / current_liabilities, 2) if current_assets else None
        metrics['quick_ratio'] = round((current_assets - inventory) / current_liabilities, 2) if current_assets else None

    # 财务杠杆
    if equity > 0:
        metrics['equity_multiplier'] = round(total_assets / equity, 2)

    # 资产周转率
    if total_assets > 0:
        metrics['asset_turnover'] = round(revenue / total_assets, 2) if revenue else None

    # 现金流指标（增强版 - 使用 AKShare 实际字段名）
    if cashflow:
        # 1. 经营现金流 - NETCASH_OPERATE
        operating_cf = safe_float(cashflow.get('NETCASH_OPERATE') or 0)

        # 2. 投资现金流 - NETCASH_INVEST (AKShare 实际字段)
        investing_cf = safe_float(cashflow.get('NETCASH_INVEST') or 0)

        # 3. 筹资现金流 - NETCASH_FINANCE (AKShare 实际字段)
        financing_cf = safe_float(cashflow.get('NETCASH_FINANCE') or 0)

        # 4. 资本支出（购建固定资产）- CONSTRUCT_LONG_ASSET
        capex = safe_float(cashflow.get('CONSTRUCT_LONG_ASSET') or 0)

        # 5. 现金及现金等价物净增加额 - CCE_ADD (AKShare 实际字段)
        net_cash_increase = safe_float(cashflow.get('CCE_ADD') or 0)

        # 6. 期末现金及现金等价物余额 - END_CCE (AKShare 实际字段)
        ending_cash = safe_float(cashflow.get('END_CCE') or 0)

        # 7. 分配股利、利润或偿付利息支付的现金 - ASSIGN_DIVIDEND_PORFIT (AKShare 实际字段)
        dividends_paid = safe_float(cashflow.get('ASSIGN_DIVIDEND_PORFIT') or 0)

        # 计算指标
        if net_profit != 0:
            metrics['ocf_to_np'] = round(operating_cf / net_profit * 100, 2) if operating_cf else None

        metrics['operating_cash_flow_billion'] = round(operating_cf / 1e8, 2) if operating_cf else None
        metrics['investing_cash_flow_billion'] = round(investing_cf / 1e8, 2)
        metrics['financing_cash_flow_billion'] = round(financing_cf / 1e8, 2)
        metrics['free_cash_flow_billion'] = round((operating_cf - capex) / 1e8, 2) if operating_cf else None

        # 额外现金流指标
        metrics['capex_billion'] = round(capex / 1e8, 2) if capex else None
        metrics['net_cash_increase_billion'] = round(net_cash_increase / 1e8, 2)
        metrics['ending_cash_billion'] = round(ending_cash / 1e8, 2) if ending_cash else None
        metrics['dividends_paid_billion'] = round(dividends_paid / 1e8, 2) if dividends_paid else None

        # 现金流质量指标
        if operating_cf > 0 and net_profit > 0:
            metrics['cash_quality'] = round(operating_cf / net_profit, 2)
        elif operating_cf < 0:
            metrics['cash_quality'] = -1  # 负值现金流标记

        # 资本支出占比
        if operating_cf != 0:
            metrics['capex_ratio'] = round(abs(capex / operating_cf * 100), 2) if capex else None

    return metrics

def dupont_analysis(income: dict, balance: dict) -> dict:
    """
    杜邦分析 - 分解 ROE

    ROE = 净利率 × 总资产周转率 × 权益乘数

    Args:
        income: 利润表数据
        balance: 资产负债表数据

    Returns:
        杜邦分析结果
    """
    # 提取数据
    revenue = safe_float(income.get('TOTAL_OPERATE_INCOME') or income.get('营业收入') or 0)
    net_profit = safe_float(income.get('NETPROFIT') or income.get('净利润') or 0)
    total_assets = safe_float(balance.get('TOTAL_ASSETS') or balance.get('资产总计') or 0)
    total_liabilities = safe_float(balance.get('TOTAL_LIABILITIES') or balance.get('负债合计') or 0)
    equity = total_assets - total_liabilities

    dupont = {}

    # 净利率
    if revenue > 0:
        dupont['net_margin'] = round(net_profit / revenue * 100, 2)

    # 总资产周转率
    if total_assets > 0:
        dupont['asset_turnover'] = round(revenue / total_assets, 2)

    # 权益乘数
    if equity > 0:
        dupont['equity_multiplier'] = round(total_assets / equity, 2)

    # ROE (杜邦计算)
    if all(k in dupont for k in ['net_margin', 'asset_turnover', 'equity_multiplier']):
        dupont['roe_dupont'] = round(
            dupont['net_margin'] * dupont['asset_turnover'] * dupont['equity_multiplier'] / 100,
            2
        )

    return dupont

def calculate_health_score_v2(metrics: dict) -> dict:
    """
    五维度健康评分系统 (100分制)

    Args:
        metrics: 财务指标字典

    Returns:
        评分详情和总分
    """
    scores = {
        'profitability': {'score': 0, 'max': 25, 'detail': ''},
        'solvency': {'score': 0, 'max': 25, 'detail': ''},
        'efficiency': {'score': 0, 'max': 20, 'detail': ''},
        'growth': {'score': 0, 'max': 15, 'detail': ''},
        'cashflow': {'score': 0, 'max': 15, 'detail': ''}
    }

    # 1. 盈利能力 (25分) - 基于 ROE
    roe = metrics.get('roe') or 0
    if roe > 15:
        scores['profitability']['score'] = 25
        scores['profitability']['detail'] = '优秀 (ROE>15%)'
    elif roe > 10:
        scores['profitability']['score'] = 20
        scores['profitability']['detail'] = '良好 (ROE 10-15%)'
    elif roe > 5:
        scores['profitability']['score'] = 15
        scores['profitability']['detail'] = '一般 (ROE 5-10%)'
    elif roe > 0:
        scores['profitability']['score'] = 10
        scores['profitability']['detail'] = '较弱 (ROE 0-5%)'
    else:
        scores['profitability']['detail'] = '亏损'

    # 2. 偿债能力 (25分) - 基于资产负债率
    debt_ratio = metrics.get('debt_ratio') or 100
    if debt_ratio < 40:
        scores['solvency']['score'] = 25
        scores['solvency']['detail'] = '低风险 (负债率<40%)'
    elif debt_ratio < 50:
        scores['solvency']['score'] = 20
        scores['solvency']['detail'] = '适中 (负债率40-50%)'
    elif debt_ratio < 60:
        scores['solvency']['score'] = 15
        scores['solvency']['detail'] = '需关注 (负债率50-60%)'
    elif debt_ratio < 70:
        scores['solvency']['score'] = 10
        scores['solvency']['detail'] = '较高 (负债率60-70%)'
    else:
        scores['solvency']['score'] = 5
        scores['solvency']['detail'] = '高风险 (负债率>70%)'

    # 3. 运营效率 (20分) - 基于资产周转率
    turnover = metrics.get('asset_turnover') or 0
    if turnover > 1.0:
        scores['efficiency']['score'] = 20
        scores['efficiency']['detail'] = '高效 (周转率>1.0)'
    elif turnover > 0.7:
        scores['efficiency']['score'] = 15
        scores['efficiency']['detail'] = '良好 (周转率0.7-1.0)'
    elif turnover > 0.5:
        scores['efficiency']['score'] = 10
        scores['efficiency']['detail'] = '一般 (周转率0.5-0.7)'
    elif turnover > 0.3:
        scores['efficiency']['score'] = 5
        scores['efficiency']['detail'] = '较低 (周转率0.3-0.5)'
    else:
        scores['efficiency']['detail'] = '低效 (周转率<0.3)'

    # 4. 成长能力 (15分) - 默认给中等分（需要历史数据）
    # 暂时基于净利率判断
    npm = metrics.get('net_profit_margin') or 0
    if npm > 10:
        scores['growth']['score'] = 12
        scores['growth']['detail'] = '良好 (需历史数据确认)'
    elif npm > 5:
        scores['growth']['score'] = 8
        scores['growth']['detail'] = '一般 (需历史数据确认)'
    else:
        scores['growth']['score'] = 5
        scores['growth']['detail'] = '待评估'

    # 5. 现金流质量 (15分)
    ocf_ratio = metrics.get('ocf_to_np') or 0
    if ocf_ratio > 1.2:
        scores['cashflow']['score'] = 15
        scores['cashflow']['detail'] = '优秀 (现金流/净利润>1.2)'
    elif ocf_ratio > 1.0:
        scores['cashflow']['score'] = 12
        scores['cashflow']['detail'] = '良好 (现金流/净利润>1.0)'
    elif ocf_ratio > 0.8:
        scores['cashflow']['score'] = 8
        scores['cashflow']['detail'] = '一般 (现金流/净利润 0.8-1.0)'
    elif ocf_ratio > 0.5:
        scores['cashflow']['score'] = 4
        scores['cashflow']['detail'] = '需关注 (现金流/净利润 0.5-0.8)'
    elif ocf_ratio > 0:
        scores['cashflow']['score'] = 2
        scores['cashflow']['detail'] = '较差 (现金流/净利润<0.5)'
    else:
        scores['cashflow']['score'] = 0
        scores['cashflow']['detail'] = '很差 (经营现金流为负)'

    # 计算总分
    total_score = sum(s['score'] for s in scores.values())

    # 风险等级
    if total_score >= 80:
        risk_level = "低风险"
    elif total_score >= 60:
        risk_level = "中低风险"
    elif total_score >= 40:
        risk_level = "中等风险"
    elif total_score >= 20:
        risk_level = "中高风险"
    else:
        risk_level = "高风险"

    return {
        'total_score': total_score,
        'risk_level': risk_level,
        'dimensions': scores
    }

def save_data_to_file(data: dict, output_dir: str = None) -> str:
    """
    保存财务数据到 JSON 文件

    Args:
        data: 财务数据字典
        output_dir: 输出目录，默认为脚本所在目录的 ../reports/

    Returns:
        保存的文件路径
    """
    # 确定输出目录
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "..", "reports")

    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 生成文件名
    stock_code = data.get("stock_code", "unknown")
    stock_name = data.get("stock_name", "unknown")
    # 清理股票名称中的特殊字符
    safe_name = "".join(c for c in stock_name if c.isalnum() or c in ('_', '-'))
    filename = f"{stock_code}_{safe_name}.json"
    filepath = os.path.join(output_dir, filename)

    # 保存数据
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    print(f"[保存] 数据已保存到: {filepath}")
    return filepath


def save_html_report(data: dict, output_dir: str = None, theme: str = "medium") -> str:
    """
    保存 HTML 财务报告

    Args:
        data: 财务分析数据（来自 analyze_stock）
        output_dir: 输出目录，默认为脚本所在目录的 ../reports/
        theme: 主题 (dark/medium/light)

    Returns:
        保存的 HTML 文件路径
    """
    # 确定输出目录
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "..", "reports")

    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 导入 HTML 模板生成函数
    try:
        from html_template import generate_html_report
    except ImportError:
        print("[错误] 无法导入 html_template 模块")
        return None

    # 生成 HTML
    html = generate_html_report(data, theme=theme)

    # 生成文件名
    stock_code = data.get("stock_code", "unknown")
    filename = f"{stock_code}_financial_report.html"
    filepath = os.path.join(output_dir, filename)

    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[保存] HTML 报告已保存到: {filepath}")
    return filepath

def analyze_stock(stock_code: str, stock_name: str = None,
                network_mode: str = None, proxy_url: str = None,
                generate_html: bool = False, output_dir: str = None,
                enhance_analysis: bool = False,
                generate_ppt: bool = False,
                generate_ai_ppt: bool = False,
                fetch_news: bool = False,
                fetch_baike: bool = False,
                deep_analysis: bool = False,
                generate_video: bool = False,
                video_type: str = "summary") -> dict:
    """
    分析股票并生成报告（增强版）

    Args:
        stock_code: 股票代码
        stock_name: 股票名称
        network_mode: 网络模式
        proxy_url: 代理地址
        generate_html: 是否生成 HTML 报告
        output_dir: 输出目录
        enhance_analysis: 是否启用增强文字分析
        generate_ppt: 是否生成 PPT 报告（本地生成，需要python-pptx）
        generate_ai_ppt: 是否使用百度 AI 生成精美 PPT（需要BAIDU_API_KEY）
        fetch_news: 是否获取最新资讯
        fetch_baike: 是否获取公司百科信息
        deep_analysis: 是否生成深度行业分析

    Returns:
        分析结果字典
    """
    data = get_financial_data(stock_code, stock_name)

    if not data.get("success"):
        return {"error": "获取数据失败", "details": data}

    # 基础指标
    basic_metrics = data.get("key_metrics", {})

    # 获取原始数据
    income_data = data.get("data", {}).get("income", [{}])[0] if data.get("data", {}).get("income") else {}
    balance_data = data.get("data", {}).get("balance", [{}])[0] if data.get("data", {}).get("balance") else {}
    cashflow_data = data.get("data", {}).get("cashflow", [{}])[0] if data.get("data", {}).get("cashflow") else {}

    # 计算高级指标
    advanced_metrics = calculate_advanced_metrics(income_data, balance_data, cashflow_data)

    # 杜邦分析
    dupont = dupont_analysis(income_data, balance_data)

    # 合并所有指标
    all_metrics = {**basic_metrics, **advanced_metrics}

    # 五维度健康评分
    health_result = calculate_health_score_v2(all_metrics)

    # ===== 行业分析 =====
    industry_analysis = None
    if HAS_INDUSTRY_ANALYSIS:
        try:
            scorer = IndustryScorer()
            industry_analysis = scorer.calculate_industry_adjusted_score(
                all_metrics,
                stock_code,
                stock_name
            )
            print(f"[行业] {industry_analysis['industry']['name']}")
            print(f"[行业评分] {industry_analysis['normalized_score']:.2f}/100 ({industry_analysis['risk_level']})")
        except Exception as e:
            print(f"[警告] 行业分析失败: {e}")
            industry_analysis = None

    # 构建分析结果
    analysis = {
        "profitability": {
            "net_margin": health_result['dimensions']['profitability']['detail'],
            "roe": f"{all_metrics.get('roe', 0):.2f}%" if all_metrics.get('roe') else None,
            "roa": f"{all_metrics.get('roa', 0):.2f}%" if all_metrics.get('roa') else None,
            "gross_margin": f"{all_metrics.get('gross_margin', 0):.2f}%" if all_metrics.get('gross_margin') else None,
        },
        "solvency": {
            "debt_level": health_result['dimensions']['solvency']['detail'],
            "current_ratio": all_metrics.get('current_ratio'),
            "quick_ratio": all_metrics.get('quick_ratio'),
        },
        "efficiency": {
            "asset_turnover": health_result['dimensions']['efficiency']['detail'],
            "turnover_value": all_metrics.get('asset_turnover'),
        },
        "cashflow": {
            "quality": health_result['dimensions']['cashflow']['detail'],
            "ocf_to_np": all_metrics.get('ocf_to_np'),
            "free_cash_flow_billion": all_metrics.get('free_cash_flow_billion'),
        },
        "dupont": dupont,
        "recommendations": []
    }

    # 生成建议
    if health_result['total_score'] >= 60:
        analysis['recommendations'].append("财务状况良好")
    elif health_result['total_score'] >= 40:
        analysis['recommendations'].append("财务状况一般，建议关注薄弱环节")
    else:
        analysis['recommendations'].append("财务状况需警惕，建议深入分析")

    # 建筑行业特殊提示
    if all_metrics.get('debt_ratio', 0) > 70:
        analysis['recommendations'].append("建筑行业高负债为常态，需关注现金流")

    # 构建返回结果
    result = {
        "stock_code": stock_code,
        "stock_name": data.get("stock_name"),
        "key_metrics": all_metrics,
        "analysis": analysis,
        "health_score": health_result['total_score'],
        "health_details": health_result['dimensions'],
        "risk_level": health_result['risk_level'],
        "dupont_analysis": dupont,
        "fetch_time": data.get("fetch_time")
    }

    # 添加行业分析结果
    if industry_analysis:
        result["industry"] = industry_analysis['industry']
        result["industry_analysis"] = industry_analysis

        # 合并行业建议到总体建议
        industry_recs = industry_analysis.get('recommendations', [])
        for rec in industry_recs:
            if rec not in analysis['recommendations']:
                analysis['recommendations'].append(rec)

    # ===== 增强分析（可选）=====
    if enhance_analysis:
        try:
            from analysis_enhancer import AnalysisEnhancer

            print("[增强分析] 正在生成深度分析...")
            enhancer = AnalysisEnhancer()

            # 生成增强分析
            enhanced = enhancer.enhance_analysis(
                all_metrics,
                health_result,
                industry_analysis,
                stock_code,
                stock_name or data.get("stock_name", "")
            )

            # 更新分析结果
            analysis.update(enhanced)
            result["enhanced_analysis"] = True

            print("[增强分析] 深度分析生成完成")

        except ImportError:
            print("[警告] analysis_enhancer 模块不可用，使用基础分析")
        except Exception as e:
            print(f"[警告] 增强分析失败: {e}")
            import traceback
            traceback.print_exc()

    # 生成 HTML 报告
    if generate_html:
        html_path = save_html_report(result, output_dir=output_dir)
        result["html_report_path"] = html_path

    # ===== Baidu 技能增强（可选）=====
    baidu_results = {}
    stock_name_final = stock_name or data.get("stock_name", "")

    # 检查是否需要使用 Baidu 技能
    use_baidu_skills = (generate_ppt or generate_ai_ppt or fetch_news or fetch_baike or deep_analysis) and HAS_BAIDU_SKILLS

    if use_baidu_skills:
        try:
            print("[Baidu技能] 正在初始化...")
            baidu_wrapper = create_baidu_wrapper(timeout=60, enable_cache=True)

            # 获取最新资讯
            if fetch_news:
                print(f"[Baidu技能] 正在获取 {stock_name_final} 的最新资讯...")
                news_result = baidu_wrapper.search_latest_news(stock_name_final, stock_code)
                baidu_results["news"] = news_result
                if news_result.get("success"):
                    print(f"[Baidu技能] 获取到 {news_result.get('count', 0)} 条资讯")
                result["latest_news"] = news_result

            # 获取公司百科信息
            if fetch_baike:
                print(f"[Baidu技能] 正在获取 {stock_name_final} 的百科信息...")
                baike_result = baidu_wrapper.get_company_info(stock_name_final, stock_code)
                baidu_results["baike"] = baike_result
                if baike_result.get("success"):
                    print(f"[Baidu技能] 百科信息获取成功")
                result["company_baike"] = baike_result

            # 深度行业分析
            if deep_analysis and industry_analysis:
                industry_name = industry_analysis.get("industry", {}).get("name", "")
                if industry_name:
                    print(f"[Baidu技能] 正在生成 {industry_name} 行业深度分析...")
                    deep_result = baidu_wrapper.deep_industry_analysis(
                        industry_name,
                        stock_name_final,
                        aspects=["市场规模", "竞争格局", "发展趋势", "风险机遇"]
                    )
                    baidu_results["deep_analysis"] = deep_result
                    if deep_result.get("success"):
                        print(f"[Baidu技能] 深度分析生成成功")
                    result["deep_industry_analysis"] = deep_result

            # 生成 PPT 报告
            if generate_ai_ppt:
                print(f"[AI PPT] 正在使用百度 AI 生成 {stock_name_final} 财务分析PPT...")
                print(f"[AI PPT] 注意：AI PPT 生成需要 2-3 分钟，请耐心等待...")
                ppt_result = baidu_wrapper.generate_ppt_with_ai_skill(
                    result,
                    output_dir=output_dir,
                    style="商务",
                    use_ai=True  # 使用百度 AI 生成
                )
                baidu_results["ppt"] = ppt_result
                if ppt_result.get("success"):
                    ppt_path = ppt_result.get("ppt_path", "")
                    print(f"[AI PPT] PPT生成完成: {ppt_path}")
                    result["ppt_report_path"] = ppt_path
                    result["ppt_method"] = "baidu_ai"
                else:
                    error = ppt_result.get("error", "未知错误")
                    print(f"[AI PPT] 生成失败: {error}")
                    # 如果 AI 失败，降级到本地生成
                    if generate_ppt:
                        print(f"[AI PPT] 降级到本地 PPT 生成...")
                        ppt_result_local = baidu_wrapper.generate_ppt_report(
                            result,
                            output_dir=output_dir,
                            style="商务"
                        )
                        if ppt_result_local.get("success"):
                            result["ppt_report_path"] = ppt_result_local.get("ppt_path")
                            result["ppt_method"] = "local"
            elif generate_ppt:
                print(f"[PPT] 正在生成 {stock_name_final} 财务分析PPT（本地生成）...")
                ppt_result = baidu_wrapper.generate_ppt_report(
                    result,
                    output_dir=output_dir,
                    style="商务"
                )
                baidu_results["ppt"] = ppt_result
                if ppt_result.get("success"):
                    print(f"[PPT] PPT生成完成: {ppt_result.get('ppt_path')}")
                result["ppt_report_path"] = ppt_result.get("ppt_path")
                result["ppt_method"] = "local"

            # 添加缓存统计
            cache_stats = baidu_wrapper.get_cache_stats()
            baidu_results["cache_stats"] = cache_stats

        except ImportError:
            print("[警告] baidu_skills_wrapper 模块不可用")
            result["baidu_skills_error"] = "模块未安装"
        except Exception as e:
            print(f"[警告] Baidu技能调用失败: {e}")
            result["baidu_skills_error"] = str(e)
            import traceback
            traceback.print_exc()

    # 添加 Baidu 技能结果
    if baidu_results:
        result["baidu_skills"] = baidu_results

    # ===== 视频生成（可选）=====
    if generate_video and HAS_VIDEO_GENERATOR:
        try:
            print(f"[视频] 正在生成财务分析视频...")

            # 确定视频类型
            video_type_map = {
                "summary": "ExecutiveSummary",
                "detailed": "DetailedAnalysis",
                "highlight": "HighlightReel",
            }

            composition = video_type_map.get(video_type, "ExecutiveSummary")

            # 创建视频生成器
            video_gen = create_video_generator()

            # 生成视频
            if video_type == "all":
                video_result = video_gen.generate_all_videos(result, output_dir=output_dir)
            else:
                video_result = video_gen.generate_video(
                    data=result,
                    composition=composition,
                    output_dir=output_dir
                )

            if video_result.get("success"):
                print(f"[视频] 视频生成完成")
                if "video_path" in video_result:
                    print(f"[视频] 文件路径: {video_result['video_path']}")
                    print(f"[视频] 文件大小: {video_result.get('file_size_mb', 'N/A')} MB")
                result["video_result"] = video_result
            else:
                print(f"[视频] 视频生成失败: {video_result.get('error')}")
                result["video_error"] = video_result.get("error")

        except Exception as e:
            print(f"[警告] 视频生成失败: {e}")
            result["video_error"] = str(e)
            import traceback
            traceback.print_exc()

    return result

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="A股财务数据获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python fetch_data.py 600519                    # 获取贵州茅台数据
  python fetch_data.py 600519 贵州茅台            # 指定名称
  python fetch_data.py 600519 --analyze          # 获取并分析
  python fetch_data.py 600519 --analyze --html    # 生成 HTML 报告到 reports/
  python fetch_data.py 600519 --save             # 保存 JSON 数据
  python fetch_data.py --check                   # 检查环境
  python fetch_data.py --install                 # 安装依赖

  # Baidu 技能增强
  python fetch_data.py 600519 --analyze --ppt     # 生成财务分析PPT（本地生成）
  python fetch_data.py 600519 --analyze --ai-ppt  # 使用百度 AI 生成精美 PPT（需要 BAIDU_API_KEY）
  python fetch_data.py 600519 --analyze --news    # 获取最新资讯
  python fetch_data.py 600519 --analyze --baike   # 获取公司百科信息
  python fetch_data.py 600519 --analyze --deep-analysis  # 深度行业分析
  python fetch_data.py 600519 --analyze --enhance --ai-ppt --news  # 综合增强
        """
    )

    parser.add_argument("stock_code", nargs="?", help="股票代码")
    parser.add_argument("stock_name", nargs="?", help="股票名称")
    parser.add_argument("--analyze", action="store_true", help="分析股票")
    parser.add_argument("--save", action="store_true", help="保存数据到文件")
    parser.add_argument("--html", action="store_true", help="生成 HTML 报告")
    parser.add_argument("--enhance", action="store_true", help="启用增强文字分析（更详细的解读和建议）")
    parser.add_argument("--output", type=str, help="指定输出目录")
    parser.add_argument("--check", action="store_true", help="检查环境")
    parser.add_argument("--install", action="store_true", help="安装依赖")
    parser.add_argument("--no-auto-install", action="store_true", help="不自动安装依赖")

    # 网络配置选项
    parser.add_argument("--mode", choices=["auto", "direct", "proxy"],
                       help="网络模式: auto=自动检测, direct=国内直连, proxy=使用代理")
    parser.add_argument("--proxy", help="代理地址 (如 http://127.0.0.1:7890 或 socks5://127.0.0.1:1080)")
    parser.add_argument("--detect-network", action="store_true", help="检测网络连接状态")
    parser.add_argument("--test-proxy", help="测试代理连接")

    # Baidu 技能选项
    parser.add_argument("--ppt", action="store_true", help="生成财报分析PPT（本地python-pptx生成）")
    parser.add_argument("--ai-ppt", action="store_true", help="使用百度 AI 生成精美 PPT（需要 BAIDU_API_KEY，耗时2-3分钟）")
    parser.add_argument("--video", action="store_true", help="生成财务分析视频（需要 Node.js 和 Remotion，耗时2-5分钟）")
    parser.add_argument("--video-type", choices=["summary", "detailed", "highlight", "all"],
                       default="summary", help="视频类型: summary=执行摘要(60秒), detailed=详细分析(180秒), highlight=高亮点(30秒), all=全部")
    parser.add_argument("--news", action="store_true", help="获取公司最新资讯")
    parser.add_argument("--baike", action="store_true", help="获取公司百科信息")
    parser.add_argument("--deep-analysis", action="store_true", help="生成深度行业分析报告")

    args = parser.parse_args()

    # 网络检测模式
    if args.detect_network:
        if HAS_NETWORK_CLIENT:
            from network_client import NetworkDetector
            mode = NetworkDetector.detect_network_mode()
            print(f"\n检测到的网络模式: {mode}")
            return 0
        else:
            print("[错误] 网络增强模块不可用，请确保 network_client.py 存在")
            return 1

    # 测试代理模式
    if args.test_proxy:
        if HAS_NETWORK_CLIENT:
            from network_client import NetworkDetector
            print(f"[测试] 代理连接: {args.test_proxy}")
            if NetworkDetector.test_proxy(args.test_proxy):
                print("[OK] 代理连接成功")
                return 0
            else:
                print("[失败] 代理连接失败")
                return 1
        else:
            print("[错误] 网络增强模块不可用")
            return 1

    # 检查环境模式
    if args.check:
        status = check_environment(auto_install=False)
        print("\n" + "="*50)
        print("[环境状态]")
        print("="*50)
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0 if status["all_ok"] else 1

    # 安装依赖模式
    if args.install:
        print("[安装] 安装依赖...")
        if ensure_dependencies(auto_install=True):
            print("\n[OK] 依赖安装完成")
            return 0
        else:
            print("\n[错误] 依赖安装失败")
            return 1

    # 需要股票代码
    if not args.stock_code:
        parser.print_help()
        return 1

    # 确保依赖可用
    auto_install = not args.no_auto_install
    if not ensure_dependencies(auto_install=auto_install):
        print("\n[错误] 依赖不完整，请运行:")
        print("  python fetch_data.py --install")
        return 1

    # 执行获取或分析
    if args.analyze:
        result = analyze_stock(args.stock_code, args.stock_name,
                              network_mode=args.mode, proxy_url=args.proxy,
                              generate_html=args.html, output_dir=args.output,
                              enhance_analysis=args.enhance,
                              generate_ppt=args.ppt,
                              generate_ai_ppt=args.ai_ppt,
                              fetch_news=args.news,
                              fetch_baike=args.baike,
                              deep_analysis=args.deep_analysis,
                              generate_video=args.video,
                              video_type=args.video_type)
    else:
        result = get_financial_data(args.stock_code, args.stock_name,
                                   network_mode=args.mode, proxy_url=args.proxy)

    # 保存数据到文件
    if args.save and (result.get("success") or result.get("health_score") is not None):
        filepath = save_data_to_file(result, args.output)
        result["saved_to"] = filepath

    # 单独生成 HTML 报告（如果没有通过 analyze 生成）
    if args.html and "html_report_path" not in result and result.get("health_score") is not None:
        html_path = save_html_report(result, output_dir=args.output)
        if html_path:
            result["html_report_path"] = html_path

    print("\n" + "="*50)
    print("[结果]")
    print("="*50)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

    return 0 if result.get("success") or result.get("health_score") else 1

if __name__ == "__main__":
    sys.exit(main())
