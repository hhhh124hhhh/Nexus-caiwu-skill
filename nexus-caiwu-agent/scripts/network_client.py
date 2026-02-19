#!/usr/bin/env python3
"""
通用网络请求模块
支持国内直连和代理两种模式

用法:
    from network_client import NetworkClient

    # 自动模式（自动检测）
    client = NetworkClient(mode='auto')
    data = client.fetch_financial_data('600519', '贵州茅台')

    # 国内直连模式
    client = NetworkClient(mode='direct')

    # 代理模式
    client = NetworkClient(mode='proxy', proxy_url='http://127.0.0.1:7890')

    # SOCKS5 代理
    client = NetworkClient(mode='proxy', proxy_url='socks5://127.0.0.1:1080')
"""

import os
import sys
import time
import json
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime


# ===== 配置管理 =====

class NetworkConfig:
    """网络配置管理"""

    # 配置文件路径
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "network.json")

    # 默认配置
    DEFAULT_CONFIG = {
        "mode": "auto",  # auto, direct, proxy
        "proxy": {
            "http": None,
            "https": None,
            "socks5": None
        },
        "timeout": 30,
        "retry": 3,
        "retry_delay": 2,
        "verify_ssl": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._merge_config(user_config)
            except Exception as e:
                print(f"[警告] 加载配置文件失败: {e}")

        # 从环境变量加载
        self._load_from_env()

    def _merge_config(self, user_config: dict):
        """合并用户配置"""
        if "mode" in user_config:
            self.config["mode"] = user_config["mode"]
        if "proxy" in user_config:
            self.config["proxy"].update(user_config["proxy"])
        if "timeout" in user_config:
            self.config["timeout"] = user_config["timeout"]
        if "retry" in user_config:
            self.config["retry"] = user_config["retry"]
        if "retry_delay" in user_config:
            self.config["retry_delay"] = user_config["retry_delay"]
        if "verify_ssl" in user_config:
            self.config["verify_ssl"] = user_config["verify_ssl"]

    def _load_from_env(self):
        """从环境变量加载配置"""
        # 模式
        if os.getenv("NET_MODE"):
            self.config["mode"] = os.getenv("NET_MODE")

        # 代理配置
        if os.getenv("HTTP_PROXY") or os.getenv("http_proxy"):
            self.config["proxy"]["http"] = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        if os.getenv("HTTPS_PROXY") or os.getenv("https_proxy"):
            self.config["proxy"]["https"] = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
        if os.getenv("ALL_PROXY") or os.getenv("all_proxy"):
            proxy = os.getenv("ALL_PROXY") or os.getenv("all_proxy")
            self.config["proxy"]["http"] = proxy
            self.config["proxy"]["https"] = proxy

        # 超时和重试
        if os.getenv("NET_TIMEOUT"):
            self.config["timeout"] = int(os.getenv("NET_TIMEOUT"))
        if os.getenv("NET_RETRY"):
            self.config["retry"] = int(os.getenv("NET_RETRY"))

    def get_proxy_config(self) -> Optional[Dict[str, str]]:
        """获取当前代理配置"""
        mode = self.config["mode"]

        # 直连模式
        if mode == "direct":
            return None

        # 代理模式
        if mode == "proxy":
            proxy = self.config["proxy"]
            # 优先使用 socks5
            if proxy.get("socks5"):
                return {"http": proxy["socks5"], "https": proxy["socks5"]}
            # 使用 http/https
            if proxy.get("http") or proxy.get("https"):
                result = {}
                if proxy.get("http"):
                    result["http"] = proxy["http"]
                if proxy.get("https"):
                    result["https"] = proxy["https"]
                return result if result else None

        # 自动模式：检测环境变量
        if mode == "auto":
            if self.config["proxy"].get("socks5") or self.config["proxy"].get("http"):
                return self.get_proxy_config()
            # 没有代理配置，返回 None（直连）
            return None

        return None

    def save_config(self, config: dict):
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self._merge_config(config)


# 全局配置实例
_global_config = None

def get_config() -> NetworkConfig:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = NetworkConfig()
    return _global_config


# ===== 重试装饰器 =====

def retry_on_error(max_retries: int = None, delay: float = None,
                   exceptions: tuple = (Exception,)):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）
        exceptions: 需要重试的异常类型
    """
    config = get_config()
    if max_retries is None:
        max_retries = config.config["retry"]
    if delay is None:
        delay = config.config["retry_delay"]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_retries:
                        print(f"    [重试] {attempt + 1}/{max_retries} - {e}")
                        time.sleep(delay * (attempt + 1))  # 递增延迟
                    else:
                        print(f"    [失败] 达到最大重试次数 ({max_retries})")
            raise last_error
        return wrapper
    return decorator


# ===== 网络检测 =====

class NetworkDetector:
    """网络连接检测器"""

    # 测试 URL
    TEST_URLS = {
        "domestic": [
            ("https://www.baidu.com", "百度"),
            ("https://api.akshare.xyz", "AKShare API"),
        ],
        "international": [
            ("https://www.google.com", "Google"),
            ("https://github.com", "GitHub"),
        ]
    }

    @staticmethod
    def test_connectivity(url: str, timeout: int = 5) -> bool:
        """测试单个 URL 连接"""
        try:
            import urllib.request
            request = urllib.request.Request(
                url,
                headers={"User-Agent": get_config().config["user_agent"]}
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status == 200
        except Exception:
            return False

    @classmethod
    def detect_network_mode(cls, timeout: int = 5) -> str:
        """
        自动检测网络模式

        Returns:
            "direct" - 国内直连可用
            "proxy" - 需要代理
            "unknown" - 无法确定
        """
        print("[检测] 网络连接状态...")

        # 先测试国内网站
        domestic_ok = False
        for url, name in cls.TEST_URLS["domestic"]:
            if cls.test_connectivity(url, timeout):
                print(f"  [OK] {name} 连接正常")
                domestic_ok = True
                break
            else:
                print(f"  [失败] {name} 连接失败")

        if domestic_ok:
            print("[结论] 国内网络直连可用，建议使用 direct 模式")
            return "direct"

        print("[结论] 国内网络直连不可用，建议使用 proxy 模式")
        return "proxy"

    @classmethod
    def test_proxy(cls, proxy_url: str, timeout: int = 5) -> bool:
        """测试代理连接"""
        try:
            import urllib.request
            proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
            opener = urllib.request.build_opener(proxy_handler)
            request = urllib.request.Request(
                "https://www.baidu.com",
                headers={"User-Agent": get_config().config["user_agent"]}
            )
            with opener.open(request, timeout=timeout) as response:
                return response.status == 200
        except Exception as e:
            print(f"  [失败] 代理测试失败: {e}")
            return False


# ===== AKShare 包装器 =====

class AkShareWrapper:
    """AKShare 包装器，支持代理和重试"""

    def __init__(self, config: NetworkConfig = None):
        self.config = config or get_config()
        self._setup_akshare()

    def _setup_akshare(self):
        """配置 AKShare 使用代理"""
        proxy_config = self.config.get_proxy_config()

        if proxy_config:
            # AKShare 使用 requests 库，需要设置代理
            import requests
            # 设置会话代理
            self._session = requests.Session()
            self._session.proxies.update(proxy_config)
            self._session.verify = self.config.config["verify_ssl"]
            self._session.timeout = self.config.config["timeout"]

            # 设置全局代理（影响 akshare）
            if proxy_config.get("http"):
                os.environ["HTTP_PROXY"] = proxy_config["http"]
            if proxy_config.get("https"):
                os.environ["HTTPS_PROXY"] = proxy_config["https"]

            print(f"[配置] 使用代理: {proxy_config}")
        else:
            print("[配置] 使用直连模式")
            # 清除代理环境变量
            for key in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
                os.environ.pop(key, None)

    @retry_on_error()
    def stock_profit_sheet_by_report_em(self, symbol: str):
        """获取利润表（带重试）"""
        import akshare as ak
        return ak.stock_profit_sheet_by_report_em(symbol=symbol)

    @retry_on_error()
    def stock_balance_sheet_by_report_em(self, symbol: str):
        """获取资产负债表（带重试）"""
        import akshare as ak
        return ak.stock_balance_sheet_by_report_em(symbol=symbol)

    @retry_on_error()
    def stock_cash_flow_sheet_by_report_em(self, symbol: str):
        """获取现金流量表（带重试）"""
        import akshare as ak
        return ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)


# ===== 主网络客户端 =====

class NetworkClient:
    """
    网络客户端主类

    支持三种模式:
    - auto: 自动检测网络模式
    - direct: 强制使用国内直连
    - proxy: 强制使用代理
    """

    def __init__(self, mode: str = "auto", proxy_url: str = None,
                 timeout: int = None, retry: int = None):
        """
        初始化网络客户端

        Args:
            mode: 网络模式 (auto/direct/proxy)
            proxy_url: 代理地址 (如 http://127.0.0.1:7890 或 socks5://127.0.0.1:1080)
            timeout: 请求超时时间（秒）
            retry: 重试次数
        """
        self.config = get_config()

        # 命令行参数优先级更高
        if mode != "auto":
            self.config.config["mode"] = mode

        if proxy_url:
            if proxy_url.startswith("socks5://"):
                self.config.config["proxy"]["socks5"] = proxy_url
            else:
                self.config.config["proxy"]["http"] = proxy_url
                self.config.config["proxy"]["https"] = proxy_url

        if timeout:
            self.config.config["timeout"] = timeout
        if retry:
            self.config.config["retry"] = retry

        # 自动检测模式
        if self.config.config["mode"] == "auto":
            detected_mode = NetworkDetector.detect_network_mode()
            self.config.config["mode"] = detected_mode

        # 初始化 AKShare 包装器
        self.akshare = AkShareWrapper(self.config)

    def fetch_financial_data(self, stock_code: str, stock_name: str = None) -> dict:
        """
        获取股票财务数据

        Args:
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            财务数据字典
        """
        # 导入数据提取函数
        from fetch_data import (
            convert_stock_code,
            extract_key_metrics,
            calculate_advanced_metrics,
            dupont_analysis,
            calculate_health_score_v2,
            safe_float
        )

        if stock_name is None:
            stock_name = f"股票{stock_code}"

        symbol = convert_stock_code(stock_code)
        print(f"\n[获取] {stock_name}({stock_code}) 的财务数据...")
        print(f"[代码] AKShare symbol: {symbol}")
        print(f"[模式] {self.config.config['mode']}")

        result = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "symbol": symbol,
            "fetch_time": datetime.now().isoformat(),
            "network_mode": self.config.config["mode"],
            "data": {},
            "success": False
        }

        try:
            # 1. 获取利润表
            print("  [1/3] 利润表...")
            try:
                income_df = self.akshare.stock_profit_sheet_by_report_em(symbol=symbol)
                result["data"]["income"] = income_df.head(4).to_dict(orient="records")
                print(f"        OK ({len(income_df)} 条)")
            except Exception as e:
                print(f"        失败: {e}")
                result["data"]["income"] = []

            # 2. 获取资产负债表
            print("  [2/3] 资产负债表...")
            try:
                balance_df = self.akshare.stock_balance_sheet_by_report_em(symbol=symbol)
                result["data"]["balance"] = balance_df.head(4).to_dict(orient="records")
                print(f"        OK ({len(balance_df)} 条)")
            except Exception as e:
                print(f"        失败: {e}")
                result["data"]["balance"] = []

            # 3. 获取现金流量表
            print("  [3/3] 现金流量表...")
            try:
                cashflow_df = self.akshare.stock_cash_flow_sheet_by_report_em(symbol=symbol)
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
                cashflow = result["data"]["cashflow"][0] if result["data"].get("cashflow") else {}

                # 基础指标
                basic_metrics = extract_key_metrics(latest, balance)

                # 高级指标（包含现金流量）
                advanced_metrics = calculate_advanced_metrics(latest, balance, cashflow)

                # 合并所有指标
                result["key_metrics"] = {**basic_metrics, **advanced_metrics}
                print(f"        OK ({len(result['key_metrics'])} 个)")
            else:
                result["key_metrics"] = {}

            result["success"] = True
            print(f"\n[完成] 数据获取成功!")

        except Exception as e:
            result["error"] = str(e)
            print(f"\n[错误] {e}")

        return result


# ===== 命令行工具 =====

def main():
    """命令行工具"""
    import argparse

    parser = argparse.ArgumentParser(
        description="网络配置和检测工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 检测网络模式
  python network_client.py --detect

  # 设置代理
  python network_client.py --set-proxy http://127.0.0.1:7890

  # 设置直连模式
  python network_client.py --set-mode direct

  # 测试代理连接
  python network_client.py --test-proxy socks5://127.0.0.1:1080

  # 显示当前配置
  python network_client.py --show-config
        """
    )

    parser.add_argument("--detect", action="store_true", help="自动检测网络模式")
    parser.add_argument("--set-mode", choices=["auto", "direct", "proxy"], help="设置网络模式")
    parser.add_argument("--set-proxy", help="设置代理地址 (如 http://127.0.0.1:7890)")
    parser.add_argument("--test-proxy", help="测试代理连接")
    parser.add_argument("--show-config", action="store_true", help="显示当前配置")
    parser.add_argument("--timeout", type=int, help="设置超时时间（秒）")
    parser.add_argument("--retry", type=int, help="设置重试次数")

    args = parser.parse_args()

    config = get_config()

    # 检测网络模式
    if args.detect:
        mode = NetworkDetector.detect_network_mode()
        print(f"\n检测到的网络模式: {mode}")
        return 0

    # 设置模式
    if args.set_mode:
        config.config["mode"] = args.set_mode
        config.save_config(config.config)
        print(f"[OK] 网络模式已设置为: {args.set_mode}")
        return 0

    # 设置代理
    if args.set_proxy:
        if args.set_proxy.startswith("socks5://"):
            config.config["proxy"]["socks5"] = args.set_proxy
            config.config["proxy"]["http"] = None
            config.config["proxy"]["https"] = None
        else:
            config.config["proxy"]["http"] = args.set_proxy
            config.config["proxy"]["https"] = args.set_proxy
            config.config["proxy"]["socks5"] = None
        config.config["mode"] = "proxy"
        config.save_config(config.config)
        print(f"[OK] 代理已设置为: {args.set_proxy}")
        return 0

    # 测试代理
    if args.test_proxy:
        print(f"[测试] 代理连接: {args.test_proxy}")
        if NetworkDetector.test_proxy(args.test_proxy):
            print("[OK] 代理连接成功")
            return 0
        else:
            print("[失败] 代理连接失败")
            return 1

    # 设置超时
    if args.timeout:
        config.config["timeout"] = args.timeout
        config.save_config(config.config)
        print(f"[OK] 超时时间已设置为: {args.timeout} 秒")
        return 0

    # 设置重试
    if args.retry:
        config.config["retry"] = args.retry
        config.save_config(config.config)
        print(f"[OK] 重试次数已设置为: {args.retry}")
        return 0

    # 显示配置
    if args.show_config:
        print("\n" + "="*50)
        print("[当前网络配置]")
        print("="*50)
        print(json.dumps(config.config, ensure_ascii=False, indent=2))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
