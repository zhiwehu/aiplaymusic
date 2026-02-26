# -*- coding: utf-8 -*-
"""
音乐扫描器模块

扫描指定目录下的音频文件，提取元数据并存储到数据库

支持的音频格式: MP3, FLAC, WAV, M4A, OGG
元数据提取: 标题、艺术家、专辑、年份、风格、时长

使用 mutagen 库读取音频文件的 ID3 标签

作者: AI Assistant
"""

import os
import re
from pathlib import Path

# mutagen: Python 音频元数据读取库
# 支持多种音频格式的标签读取
from mutagen import File

import config
import database.db as db

# 从配置文件读取支持的音频格式
SUPPORTED_EXTENSIONS = config.SUPPORTED_FORMATS


# ==================== 辅助函数 ====================

def get_duration(audio):
    """
    从音频文件获取播放时长

    Args:
        audio: mutagen.File 对象

    Returns:
        int: 播放时长（秒），如果获取失败返回 0
    """
    try:
        if hasattr(audio.info, 'length'):
            return int(audio.info.length)
    except Exception:
        pass
    return 0


def get_id3_tag(audio, *keys):
    """
    尝试获取 ID3 标签值

    不同的音频文件可能使用不同的标签键名，此函数尝试多个备选键名

    Args:
        audio: mutagen.File 对象
        *keys: 备选标签键名列表

    Returns:
        str or None: 标签值，如果都不存在则返回 None
    """
    # 确保 audio 有 tags 属性
    if not hasattr(audio, 'tags') or audio.tags is None:
        return None

    tags = audio.tags
    for key in keys:
        if key in tags and tags[key]:
            value = tags[key]
            # 处理列表类型的值（如多个艺术家）
            if isinstance(value, list) and value:
                return str(value[0])
            elif value:
                return str(value)
    return None


# ==================== 核心功能 ====================

def extract_metadata(file_path):
    """
    从音频文件提取元数据

    使用 mutagen 库读取 ID3 标签
    支持多种键名格式（标准 ID3v2 和常见变体）

    Args:
        file_path: 音频文件的绝对路径

    Returns:
        dict or None: 包含元数据的字典，提取失败返回 None

    元数据字段:
        - title: 歌曲标题
        - artist: 艺术家/歌手
        - album: 专辑名称
        - year: 发行年份
        - genre: 音乐风格
        - duration: 播放时长（秒）
        - format: 音频格式
    """
    try:
        # 使用 mutagen 读取音频文件
        audio = File(file_path)
        if audio is None:
            return None

        # 提取标题 (TIT2 是 ID3v2 标准键名)
        title = get_id3_tag(audio, 'TIT2', 'title', '\xa9nam')

        # 提取艺术家 (TPE1 是 ID3v2 标准键名)
        artist = get_id3_tag(audio, 'TPE1', 'TPE2', 'artist', '\xa9ART')

        # 提取专辑 (TALB 是 ID3v2 标准键名)
        album = get_id3_tag(audio, 'TALB', 'album', '\xa9alb')

        # 提取风格 (TCON 是 ID3v2 标准键名)
        genre = get_id3_tag(audio, 'TCON', 'genre', '\xa9gen')

        # 提取年份
        # 尝试多种 ID3 年份标签格式
        year = None
        for key in ['TDRC', 'TYER', 'date', 'year']:
            # 先检查 audio 是否有 tags 属性
            if not hasattr(audio, 'tags') or audio.tags is None:
                continue
            if key in audio.tags:
                value = get_id3_tag(audio, key)
                if value:
                    # 使用正则表达式提取 4 位数年份
                    match = re.search(r'(\d{4})', value)
                    if match:
                        year = int(match.group(1))
                        break

        # 获取播放时长
        duration = get_duration(audio)

        # 获取文件扩展名作为格式
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')

        return {
            'title': title,
            'artist': artist,
            'album': album,
            'year': year,
            'genre': genre,
            'duration': duration,
            'format': ext
        }
    except Exception as e:
        print(f"提取元数据失败 {file_path}: {e}")
        return None


# ==================== 扫描功能 ====================

def scan_directory(directory):
    """
    扫描目录下的所有音乐文件

    递归遍历目录，查找支持的音频文件，提取元数据并添加到数据库

    Args:
        directory: 要扫描的目录路径

    Returns:
        int: 成功添加的歌曲数量
    """
    music_dir = Path(directory)
    if not music_dir.exists():
        print(f"目录不存在: {directory}")
        return 0

    added_count = 0

    # os.walk 递归遍历目录
    for root, dirs, files in os.walk(music_dir):
        for file in files:
            # 获取文件扩展名
            ext = os.path.splitext(file)[1].lower()

            # 只处理支持的音频格式
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            # 完整文件路径
            file_path = os.path.join(root, file)

            # 提取元数据
            metadata = extract_metadata(file_path)

            if metadata:
                # 如果没有标题，使用文件名作为标题
                title = metadata['title'] or os.path.splitext(file)[0]

                # 添加到数据库
                db.add_music(
                    file_path=file_path,
                    title=title,
                    artist=metadata['artist'],
                    album=metadata['album'],
                    year=metadata['year'],
                    genre=metadata['genre'],
                    duration=metadata['duration'],
                    format=metadata['format']
                )
                added_count += 1

    return added_count


def scan_music():
    """
    扫描配置中指定的音乐目录

    从 config.py 中读取 MUSIC_DIR 路径，然后调用 scan_directory 进行扫描

    Returns:
        int: 成功添加的歌曲数量
    """
    print(f"正在扫描音乐目录: {config.MUSIC_DIR}")
    count = scan_directory(config.MUSIC_DIR)
    print(f"扫描完成，共添加 {count} 首歌曲")
    return count
