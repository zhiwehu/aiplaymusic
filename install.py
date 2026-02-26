#!/usr/bin/env python3
"""
AI Music Player MCP 安装脚本

自动配置 MCP 服务器，方便用户在各种 MCP 客户端中使用。

支持的客户端:
- Claude Desktop
- Cherry Studio
- 其他支持 MCP 的客户端
"""

import os
import sys
import json
import shutil
import platform
from pathlib import Path

# 颜色输出
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")


def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")


def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")


def get_python_path():
    """获取当前 Python 解释器路径"""
    return sys.executable


def get_mcp_config(python_path: str, script_path: str) -> dict:
    """生成 MCP 配置"""
    return {
        "mcpServers": {
            "ai-music-player": {
                "command": python_path,
                "args": [script_path]
            }
        }
    }


def detect_mcp_client_config_dir() -> Path:
    """检测 MCP 客户端配置目录"""
    system = platform.system()

    if system == "Darwin":  # macOS
        # Claude Desktop
        claude_dir = Path.home() / "Library" / "Application Support" / "Claude"
        # Cherry Studio
        cherry_dir = Path.home() / "Library" / "Application Support" / "cherry-studio"
        return claude_dir, cherry_dir
    elif system == "Linux":
        claude_dir = Path.home() / ".config" / "Claude"
        cherry_dir = Path.home() / ".config" / "cherry-studio"
        return claude_dir, cherry_dir
    elif system == "Windows":
        claude_dir = Path.home() / "AppData" / "Roaming" / "Claude"
        cherry_dir = Path.home() / "AppData" / "Roaming" / "cherry-studio"
        return claude_dir, cherry_dir

    return Path.home(), Path.home()


def configure_claude_desktop(python_path: str, script_path: str):
    """配置 Claude Desktop"""
    config_dir = Path.home() / "Library" / "Application Support" / "Claude"

    if platform.system() == "Linux":
        config_dir = Path.home() / ".config" / "Claude"
    elif platform.system() == "Windows":
        config_dir = Path.home() / "AppData" / "Roaming" / "Claude"

    config_file = config_dir / "claude_desktop_config.json"

    # 读取现有配置
    config = {}
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
        except:
            pass

    # 添加或更新 MCP 服务器配置
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    config["mcpServers"]["ai-music-player"] = {
        "command": python_path,
        "args": [script_path]
    }

    # 确保目录存在
    config_dir.mkdir(parents=True, exist_ok=True)

    # 写入配置
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print_success(f"Claude Desktop 配置已更新: {config_file}")


def configure_cherry_studio(python_path: str, script_path: str):
    """配置 Cherry Studio"""
    if platform.system() == "Darwin":
        config_dir = Path.home() / "Library" / "Application Support" / "cherry-studio"
    elif platform.system() == "Linux":
        config_dir = Path.home() / ".config" / "cherry-studio"
    elif platform.system() == "Windows":
        config_dir = Path.home() / "AppData" / "Roaming" / "cherry-studio"
    else:
        print_warning(f"不支持的平台: {platform.system()}")
        return

    config_file = config_dir / "mcp-settings.json"

    # 读取现有配置
    config = {}
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
        except:
            pass

    # 添加或更新 MCP 服务器配置
    if "servers" not in config:
        config["servers"] = {}

    config["servers"]["ai-music-player"] = {
        "type": "command",
        "command": python_path,
        "args": [script_path],
        "enabled": True
    }

    # 确保目录存在
    config_dir.mkdir(parents=True, exist_ok=True)

    # 写入配置
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print_success(f"Cherry Studio 配置已更新: {config_file}")


def generate_mcp_json(python_path: str, script_path: str):
    """生成 mcp_config.json 文件"""
    config = get_mcp_config(python_path, script_path)

    with open("mcp_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print_success("已生成 mcp_config.json")
    print(f"  内容: {json.dumps(config, indent=2)}")


def install_package():
    """安装 Python 包"""
    print("\n正在安装 ai-music-player 包...")

    # 检查是否已安装
    result = os.system(f'{sys.executable} -c "import mcp_server" 2>/dev/null')
    if result == 0:
        print_warning("包已安装，跳过安装步骤")
        return

    # 安装当前目录
    result = os.system(f'{sys.executable} -m pip install -e .')
    if result == 0:
        print_success("包安装成功!")
    else:
        print_error("包安装失败")


def main():
    print("=" * 50)
    print("AI Music Player MCP 安装向导")
    print("=" * 50)

    # 获取脚本路径
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        script_path = os.path.dirname(sys.executable)
    else:
        # 开发模式
        script_path = os.path.abspath(__file__)

    # 使用 mcp_server.py 的目录
    script_dir = Path(__file__).parent.absolute()
    script_path = str(script_dir / "mcp_server.py")

    python_path = get_python_path()

    print(f"\n检测到 Python: {python_path}")
    print(f"脚本路径: {script_path}")

    # 检查依赖
    print("\n检查依赖...")
    try:
        import pygame
        print_success("pygame 已安装")
    except ImportError:
        print_warning("pygame 未安装，正在安装...")
        os.system(f'{python_path} -m pip install pygame')

    try:
        import fastmcp
        print_success("fastmcp 已安装")
    except ImportError:
        print_warning("fastmcp 未安装，正在安装...")
        os.system(f'{python_path} -m pip install fastmcp')

    # 选择要配置的客户端
    print("\n请选择要配置的 MCP 客户端:")
    print("  1. Claude Desktop")
    print("  2. Cherry Studio")
    print("  3. 生成 mcp_config.json (通用)")
    print("  4. 全部配置")

    choice = input("\n请输入选项 (1-4): ").strip()

    if choice == "1":
        configure_claude_desktop(python_path, script_path)
    elif choice == "2":
        configure_cherry_studio(python_path, script_path)
    elif choice == "3":
        generate_mcp_json(python_path, script_path)
    elif choice == "4":
        configure_claude_desktop(python_path, script_path)
        configure_cherry_studio(python_path, script_path)
        generate_mcp_json(python_path, script_path)
    else:
        print_error("无效选项")
        return

    print("\n" + "=" * 50)
    print_success("安装完成!")
    print("=" * 50)
    print("\n下一步:")
    print("  1. 重启 MCP 客户端")
    print("  2. 开始使用 AI 音乐播放器")
    print("\n使用示例:")
    print("  - '播放周杰伦的歌'")
    print("  - '暂停'")
    print("  - '列出所有歌手'")


if __name__ == "__main__":
    main()
