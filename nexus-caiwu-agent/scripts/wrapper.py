#!/usr/bin/env python3
"""
Nexus 财务分析技能包装器

提供命令行接口来调用 Nexus-caiwu-agent 的财务分析功能。
"""

import sys
import os
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# 默认项目路径
DEFAULT_PROJECT_PATH = os.path.expanduser("~/projects/Nexus-caiwu-agent")


def check_environment():
    """检查环境是否正确配置"""
    required_vars = [
        "UTU_LLM_TYPE",
        "UTU_LLM_MODEL",
        "UTU_LLM_API_KEY",
        "UTU_LLM_BASE_URL"
    ]

    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        print(f"错误: 缺少环境变量: {', '.join(missing)}")
        print("请设置以下环境变量:")
        for var in missing:
            print(f"  export {var}='your_value'")
        return False
    return True


def check_project_path(project_path: str) -> bool:
    """检查项目路径是否存在"""
    if not os.path.exists(project_path):
        print(f"错误: 项目路径不存在: {project_path}")
        print(f"请先克隆项目:")
        print(f"  git clone https://github.com/hhhh124hhhh/Nexus-caiwu-agent {project_path}")
        return False
    return True


def run_analysis(project_path: str, stock_code: str, stock_name: str = None, stream: bool = True):
    """
    运行财务分析

    Args:
        project_path: Nexus-caiwu-agent 项目路径
        stock_code: 股票代码（如 600248）
        stock_name: 股票名称（可选）
        stream: 是否使用流式输出
    """
    if not check_project_path(project_path):
        return None

    # 切换到项目目录
    os.chdir(project_path)

    # 构建命令
    cmd = ["python", "examples/stock_analysis/main.py"]
    if stream:
        cmd.append("--stream")

    # 设置分析任务
    task = f"分析 {stock_name or stock_code}({stock_code}.SH) 的最新财报数据"
    os.environ["ANALYSIS_TASK"] = task

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"运行分析时出错: {e}")
        return False


def run_quick_chat(project_path: str, message: str, stream: bool = True):
    """
    运行快速聊天模式

    Args:
        project_path: Nexus-caiwu-agent 项目路径
        message: 分析请求消息
        stream: 是否使用流式输出
    """
    if not check_project_path(project_path):
        return None

    os.chdir(project_path)

    cmd = [
        "uv", "run", "scripts/cli_chat.py",
        "--config_name", "agents/examples/stock_analysis_final"
    ]
    if stream:
        cmd.append("--stream")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"运行聊天模式时出错: {e}")
        return False


def get_financial_data(project_path: str, stock_code: str, stock_name: str = None):
    """
    获取财务数据（使用 Python API）

    Args:
        project_path: Nexus-caiwu-agent 项目路径
        stock_code: 股票代码
        stock_name: 股票名称
    """
    if not check_project_path(project_path):
        return None

    # 动态导入项目模块
    sys.path.insert(0, project_path)

    try:
        from utu.tools.akshare_financial_tool import get_financial_reports, get_key_metrics
        from utu.tools.financial_analysis_toolkit import calculate_ratios, analyze_trends, assess_health

        # 获取财务数据
        name = stock_name or stock_code
        financial_data = get_financial_reports(stock_code, name)

        # 计算财务比率
        ratios = calculate_ratios(financial_data)

        # 分析趋势
        trends = analyze_trends(financial_data, 4)

        # 健康评估
        health = assess_health(ratios, trends)

        return {
            "stock_code": stock_code,
            "stock_name": name,
            "ratios": ratios,
            "trends": trends,
            "health": health,
            "timestamp": datetime.now().isoformat()
        }
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装项目依赖:")
        print(f"  cd {project_path} && uv sync --all-extras --all-packages --group dev")
        return None
    except Exception as e:
        print(f"获取财务数据时出错: {e}")
        return None


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="Nexus 财务分析技能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析股票
  python wrapper.py analyze --code 600248 --name "陕西建工"

  # 获取财务数据
  python wrapper.py data --code 600248

  # 快速聊天
  python wrapper.py chat --message "分析贵州茅台的财务状况"

  # 检查环境
  python wrapper.py check
        """
    )

    parser.add_argument(
        "--project-path",
        default=os.environ.get("NEXUS_PROJECT_PATH", DEFAULT_PROJECT_PATH),
        help="Nexus-caiwu-agent 项目路径"
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="运行财务分析")
    analyze_parser.add_argument("--code", required=True, help="股票代码")
    analyze_parser.add_argument("--name", help="股票名称")
    analyze_parser.add_argument("--no-stream", action="store_true", help="禁用流式输出")

    # data 命令
    data_parser = subparsers.add_parser("data", help="获取财务数据")
    data_parser.add_argument("--code", required=True, help="股票代码")
    data_parser.add_argument("--name", help="股票名称")
    data_parser.add_argument("--output", "-o", help="输出文件路径（JSON 格式）")

    # chat 命令
    chat_parser = subparsers.add_parser("chat", help="快速聊天模式")
    chat_parser.add_argument("--message", "-m", help="分析消息")
    chat_parser.add_argument("--no-stream", action="store_true", help="禁用流式输出")

    # check 命令
    subparsers.add_parser("check", help="检查环境和项目配置")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "check":
        print("检查环境配置...")
        env_ok = check_environment()
        print(f"环境变量: {'✓' if env_ok else '✗'}")

        print(f"\n检查项目路径: {args.project_path}")
        path_ok = check_project_path(args.project_path)
        print(f"项目路径: {'✓' if path_ok else '✗'}")

        return 0 if (env_ok and path_ok) else 1

    elif args.command == "analyze":
        if not check_environment():
            return 1

        success = run_analysis(
            args.project_path,
            args.code,
            args.name,
            stream=not args.no_stream
        )
        return 0 if success else 1

    elif args.command == "data":
        if not check_environment():
            return 1

        data = get_financial_data(args.project_path, args.code, args.name)
        if data:
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"数据已保存到: {args.output}")
            else:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        return 1

    elif args.command == "chat":
        if not check_environment():
            return 1

        success = run_quick_chat(
            args.project_path,
            args.message,
            stream=not args.no_stream
        )
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
