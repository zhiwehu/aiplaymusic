# -*- coding: utf-8 -*-
"""
配置文件
定义项目路径、支持格式、播放器配置等

作者: AI Assistant
"""

import os
from pathlib import Path

# 从 .env 文件加载环境变量
# 必须在使用 os.getenv 之前调用
from dotenv import load_dotenv
load_dotenv()

# ==================== 项目路径配置 ====================

# 项目根目录（config.py 在 ai_music_player 包中，需要取父目录的父目录）
# 如果被安装为包，BASE_DIR 会在 site-packages 中
_config_dir = Path(__file__).parent
# 判断是开发模式还是已安装的包
if (_config_dir.parent / "pyproject.toml").exists():
    # 开发模式：项目根目录是 ai_music_player 的父目录
    BASE_DIR = _config_dir.parent
else:
    # 已安装的包：使用当前目录
    BASE_DIR = _config_dir

# 音乐文件存放目录
# 可通过环境变量 MUSIC_DIR 自定义，默认为项目根目录下的 music 文件夹
MUSIC_DIR = Path(os.getenv("MUSIC_DIR", BASE_DIR / "music"))

# SQLite 数据库文件路径
# 可通过环境变量 DATABASE_PATH 自定义，默认为项目根目录下的 music.db
# 支持绝对路径和相对路径（相对于 BASE_DIR）
_db_path = os.getenv("DATABASE_PATH", "music.db")
DATABASE_PATH = Path(_db_path) if Path(_db_path).is_absolute() else BASE_DIR / _db_path

# ==================== 支持的音频格式 ====================

# 支持的音频文件格式列表
# MP3: 最常见的音频格式，兼容性好
# FLAC: 无损压缩格式，音质高
# WAV: 无压缩格式，音质最高但文件大
# M4A: 通常为AAC编码，音质和压缩比平衡
# OGG: 开源音频格式，支持 Vorbis 编码
SUPPORTED_FORMATS = [".mp3", ".flac", ".wav", ".m4a", ".ogg"]

# ==================== 播放器配置 ====================

# 默认音量 (0.0 ~ 1.0)
# 可通过环境变量 DEFAULT_VOLUME 自定义，0.0 表示静音，1.0 表示最大音量
DEFAULT_VOLUME = float(os.getenv("DEFAULT_VOLUME", "0.7"))
