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
import subprocess
from pathlib import Path

# 颜色输出
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")


def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")


def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")


def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")


def is_in_venv():
    """检查是否在虚拟环境中"""
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))


def get_venv_python():
    """获取虚拟环境的 Python 解释器路径"""
    script_dir = Path(__file__).parent.absolute()
    venv_path = script_dir / ".venv"

    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def create_venv():
    """创建虚拟环境"""
    script_dir = Path(__file__).parent.absolute()
    venv_path = script_dir / ".venv"

    if venv_path.exists():
        print_warning("虚拟环境已存在")
        return venv_path

    print_info("正在创建虚拟环境...")

    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)],
                       check=True, capture_output=True)
        print_success(f"虚拟环境已创建: {venv_path}")
        return venv_path
    except Exception as e:
        print_error(f"创建虚拟环境失败: {e}")
        return None


def install_dependencies(venv_python: Path):
    """在虚拟环境中安装依赖"""
    print_info("正在安装依赖...")

    # 安装依赖
    packages = [
        "fastmcp>=2.0.0",
        "pygame>=2.0.0",
        "mutagen>=1.47.0",
        "sqlalchemy>=2.0.0",
        "python-dotenv>=1.0.0",
    ]

    try:
        subprocess.run([str(venv_python), "-m", "pip", "install", "-e", "."],
                       check=True, capture_output=True)
        print_success("依赖安装成功!")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"依赖安装失败: {e.stderr.decode() if e.stderr else e}")
        return False


def get_venv_mcp_config(venv_python: Path, script_path: str) -> dict:
    """生成使用虚拟环境的 MCP 配置"""
    # 从虚拟环境获取项目路径
    project_dir = str(venv_python.parent)

    return {
        "mcpServers": {
            "ai-music-player": {
                "command": str(venv_python),
                "args": [script_path],
                "env": {}
            }
        }
    }


def configure_claude_desktop(python_path: str, script_path: str, env_config: dict = None):
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

    server_config = {
        "command": python_path,
        "args": [script_path]
    }

    # 添加环境变量
    if env_config:
        server_config["env"] = env_config

    config["mcpServers"]["ai-music-player"] = server_config

    # 确保目录存在
    config_dir.mkdir(parents=True, exist_ok=True)

    # 写入配置
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print_success(f"Claude Desktop 配置已更新")
    print(f"  配置文件: \"{config_file}\"")
    print(f"  Python: \"{python_path}\"")
    print(f"  脚本: \"{script_path}\"")


def configure_cherry_studio(python_path: str, script_path: str, env_config: dict = None):
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

    server_config = {
        "type": "command",
        "command": python_path,
        "args": [script_path],
        "enabled": True
    }

    # 添加环境变量
    if env_config:
        server_config["env"] = env_config

    config["servers"]["ai-music-player"] = server_config

    # 确保目录存在
    config_dir.mkdir(parents=True, exist_ok=True)

    # 写入配置
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print_success(f"Cherry Studio 配置已更新")
    print(f"  配置文件: \"{config_file}\"")
    print(f"  Python: \"{python_path}\"")
    print(f"  脚本: \"{script_path}\"")


def generate_mcp_json(python_path: str, script_path: str, env_config: dict = None):
    """生成 mcp_config.json 文件"""
    config = {
        "mcpServers": {
            "ai-music-player": {
                "command": python_path,
                "args": [script_path]
            }
        }
    }

    # 添加环境变量
    if env_config:
        config["mcpServers"]["ai-music-player"]["env"] = env_config

    with open("mcp_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print_success("已生成 mcp_config.json")
    print(f"\n配置内容:")
    print(json.dumps(config, indent=2, ensure_ascii=False))


def get_env_config():
    """获取环境变量配置"""
    script_dir = Path(__file__).parent.absolute()

    # 优先读取 .env，其次 .env.example
    env_file = script_dir / ".env"
    if not env_file.exists():
        env_file = script_dir / ".env.example"

    env_config = {}

    if env_file.exists():
        print_info(f"从 {env_file.name} 读取配置...")
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key:  # 确保 key 不为空
                            env_config[key] = value
        except Exception as e:
            print_warning(f"读取配置文件失败: {e}")

    return env_config


def main():
    print("=" * 60)
    print("  AI Music Player MCP 安装向导")
    print("=" * 60)

    # 项目路径
    script_dir = Path(__file__).parent.absolute()
    script_path = str(script_dir / "mcp_server.py")
    venv_python = get_venv_python()

    print(f"\n项目目录: {script_dir}")

    # 检查虚拟环境
    if is_in_venv():
        print_info("检测到已在虚拟环境中运行")
        python_path = sys.executable
        use_venv = True
    elif venv_python.exists():
        print_warning("检测到已存在的虚拟环境: .venv")
        print(f"  Python 路径: {venv_python}")
        response = input("\n是否使用现有虚拟环境? [Y/n]: ").strip().lower()
        use_venv = response != "n"
        if use_venv:
            python_path = str(venv_python)
    else:
        print_info("未检测到虚拟环境")
        print("\n建议创建虚拟环境来安装依赖，避免与系统 Python 冲突")
        response = input("是否创建虚拟环境? [Y/n]: ").strip().lower()

        if response == "n":
            print_info("将使用系统 Python 安装依赖")
            python_path = sys.executable
            use_venv = False
        else:
            venv_path = create_venv()
            if venv_path:
                venv_python = get_venv_python()
                python_path = str(venv_python)
                use_venv = True
            else:
                print_error("虚拟环境创建失败，使用系统 Python")
                python_path = sys.executable
                use_venv = False

    # 安装依赖
    if use_venv:
        install_dependencies(venv_python)

        # 检查依赖是否安装成功
        try:
            subprocess.run([str(venv_python), "-c", "import fastmcp; import pygame"],
                           check=True, capture_output=True)
            print_success("依赖检查通过")
        except:
            print_error("依赖安装可能有问题，请检查")
    else:
        # 检查依赖
        print("\n检查依赖...")
        missing = []
        for pkg in ["fastmcp", "pygame", "mutagen", "sqlalchemy", "dotenv"]:
            try:
                __import__(pkg.replace("-", "_"))
            except ImportError:
                missing.append(pkg)

        if missing:
            print_warning(f"缺少依赖: {', '.join(missing)}")
            response = input("是否现在安装? [Y/n]: ").strip().lower()
            if response != "n":
                os.system(f'{python_path} -m pip install {" ".join(missing)}')

    # 获取环境变量配置
    env_config = get_env_config()
    if env_config:
        print_info(f"从 .env 加载了 {len(env_config)} 个配置项")

    print(f"\n使用的 Python: {python_path}")
    print(f"脚本路径: {script_path}")

    # 选择要配置的客户端
    print("\n" + "-" * 40)
    print("请选择要配置的 MCP 客户端:")
    print("-" * 40)
    print("  1. Claude Desktop")
    print("  2. Cherry Studio")
    print("  3. 生成 mcp_config.json (通用)")
    print("  4. 全部配置")
    print("-" * 40)

    choice = input("\n请输入选项 (1-4): ").strip()

    if choice == "1":
        configure_claude_desktop(python_path, script_path, env_config)
    elif choice == "2":
        configure_cherry_studio(python_path, script_path, env_config)
    elif choice == "3":
        generate_mcp_json(python_path, script_path, env_config)
    elif choice == "4":
        configure_claude_desktop(python_path, script_path, env_config)
        configure_cherry_studio(python_path, script_path, env_config)
        generate_mcp_json(python_path, script_path, env_config)
    else:
        print_error("无效选项")
        return

    print("\n" + "=" * 60)
    print_success("安装完成!")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 重启 MCP 客户端 (Cherry Studio / Claude Desktop)")
    print("  2. 开始使用 AI 音乐播放器")
    print("\n使用示例:")
    print("  - '播放周杰伦的歌'")
    print("  - '暂停'")
    print("  - '列出所有歌手'")


if __name__ == "__main__":
    main()
