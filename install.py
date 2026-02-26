#!/usr/bin/env python3
"""
AI Music Player MCP 安装脚本

自动配置 MCP 服务器，方便用户在各种 MCP 客户端中使用。

使用方法:
    python install.py

支持的客户端:
- Claude Desktop
- Cherry Studio
- 其他支持 MCP 的客户端
"""

import os
import sys
import json
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

    try:
        subprocess.run([str(venv_python), "-m", "pip", "install", "-e", "."],
                       check=True, capture_output=True)
        print_success("依赖安装成功!")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"依赖安装失败")
        return False


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
                        if key:
                            env_config[key] = value
        except Exception as e:
            print_warning(f"读取配置文件失败: {e}")
    else:
        print_warning("未找到配置文件，使用默认配置")

    return env_config


def generate_mcp_config(python_path: str, script_path: str, env_config: dict, use_uvx: bool = False) -> dict:
    """生成 MCP 配置 (Cherry Studio 格式)"""
    if use_uvx:
        # 使用 uvx 方式
        server_config = {
            "type": "command",
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/zhiwehu/aiplaymusic",
                "ai-music-player"
            ],
            "env": env_config,
            "enabled": True
        }
    else:
        # 使用 Python 脚本方式
        server_config = {
            "type": "command",
            "command": python_path,
            "args": [script_path],
            "env": env_config,
            "enabled": True
        }

    # 如果 env 为空，移除 env 字段
    if not server_config["env"]:
        del server_config["env"]

    # Cherry Studio 格式 - 尝试 mcpServers
    config = {
        "mcpServers": {
            "ai-music-player": server_config
        }
    }

    return config


def main():
    print("=" * 60)
    print("  AI Music Player MCP 安装向导")
    print("=" * 60)

    # 项目路径
    script_dir = Path(__file__).parent.absolute()
    script_path = str(script_dir / "ai_music_player" / "__main__.py")
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
            print_info("将使用系统 Python")
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
        print_info(f"已加载 {len(env_config)} 个配置项")

    # 询问是否使用 uvx
    print("\n" + "-" * 40)
    print("请选择 MCP 运行方式:")
    print("-" * 40)
    print("  1. uvx (推荐，无需安装依赖)")
    print("  2. python (本地运行，需安装依赖)")
    print("-" * 40)

    choice = input("\n请输入选项 (1-2): ").strip()
    use_uvx = choice == "1"

    if use_uvx:
        print_info("将使用 uvx 方式运行")
        # uvx 不需要本地 Python 路径
        python_path = "uvx"
    else:
        print_info("将使用 python 方式运行")

    # 生成配置
    config = generate_mcp_config(python_path, script_path, env_config, use_uvx)

    # 保存到文件
    config_file = script_dir / "mcp_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print_success("MCP 配置已生成!")
    print("=" * 60)

    print(f"\n配置文件: \"{config_file}\"")
    print(f"\n{'='*60}")
    print("MCP 配置内容 (复制到你的 MCP 客户端):")
    print("=" * 60)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print("=" * 60)

    print("\n" + "-" * 60)
    print("使用说明:")
    print("-" * 60)
    print("1. 复制上方 JSON 配置")
    print("2. 打开 MCP 客户端设置")
    print("3. 添加 MCP 服务器，粘贴配置")
    print("-" * 60)

    if use_uvx:
        print("\n安装 uvx (如果还没有):")
        print("  pip install uv")
        print("\nCherry Studio:")
        print("  设置 → MCP 服务器 → 添加 → 粘贴 JSON")
    else:
        print("\nCherry Studio:")
        print("  设置 → MCP 服务器 → 添加 → 粘贴 JSON")

        print("\nClaude Desktop:")
        print("  打开 ~/.config/Claude/claude_desktop_config.json")
        print("  在 mcpServers 中添加配置")

    print("\n" + "=" * 60)
    print("配置参数说明:")
    print("=" * 60)
    if use_uvx:
        print("  运行方式: uvx (从 GitHub 自动下载运行)")
    else:
        print(f"  Python: \"{python_path}\"")
        print(f"  脚本: \"{script_path}\"")
    if env_config:
        for k, v in env_config.items():
            print(f"  {k}: \"{v}\"")
    print("=" * 60)


if __name__ == "__main__":
    main()
