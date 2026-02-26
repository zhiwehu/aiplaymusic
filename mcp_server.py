#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Music Player MCP Server

AI 音乐播放器 MCP 服务器
基于 Model Context Protocol (MCP) 的音乐播放控制服务

功能:
- 通过 LLM 解析用户意图
- 控制本地音乐播放
- 智能推荐算法
- 用户偏好学习

使用方式:
1. 作为 MCP 服务运行 (Cherry Studio 等客户端)
2. 直接运行: python mcp_server.py

作者: AI Assistant
"""

# 导入必要的标准库
import os
import sys
import random
import time
from pathlib import Path
from typing import Optional, List

# 抑制 pygame 欢迎信息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# 将项目根目录添加到 Python 路径
# 这样可以正确导入项目内的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入第三方库
from fastmcp import FastMCP

# 导入项目模块
import config
from database.models import init_db, Music
from database import db as database_db

# ==================== MCP 服务器初始化 ====================

# 创建 FastMCP 服务器实例
# MCP 是一种协议，允许 AI 模型与外部服务交互
mcp = FastMCP("AI Music Player")

# ==================== 全局播放器实例 ====================

# 全局单例播放器实例
# 避免重复创建 pygame mixer
_player = None


def get_player():
    """
    获取或创建全局播放器实例

    使用单例模式，确保整个应用只有一个播放器实例
    这是因为 pygame mixer 在同一进程中只能初始化一次

    Returns:
        MusicPlayer: 播放器实例
    """
    global _player
    if _player is None:
        import pygame

        # 初始化 pygame mixer
        # 参数说明:
        # - frequency: 采样率，44100 Hz 是 CD 音质标准
        # - size: 采样位数，-16 表示 16 位有符号
        # - channels: 声道数，2 表示立体声
        # - buffer: 缓冲区大小，越大越稳定但延迟越高
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception:
            # 如果高级参数失败，使用默认参数
            pygame.mixer.init()

        # 创建播放器实例
        _player = MusicPlayer()

    return _player


class MusicPlayer:
    """
    音乐播放器类

    封装 pygame mixer 功能，提供播放控制接口
    支持播放列表、音量控制、暂停/恢复等基本功能
    """

    def __init__(self):
        """
        初始化播放器

        设置默认状态，创建后台监控线程
        """
        import pygame

        # 保存 pygame 模块引用（懒加载）
        self._pygame = pygame

        # 当前播放的音乐文件路径
        self.current_track = None

        # 播放列表（Music 对象列表）
        self.playlist: List[Music] = []

        # 当前播放的索引位置
        self.current_index = 0

        # 播放状态标志
        self.is_playing = False      # 是否正在播放
        self.is_paused = False       # 是否已暂停

        # 音量设置 (0.0 ~ 1.0)
        self.volume = config.DEFAULT_VOLUME
        pygame.mixer.music.set_volume(self.volume)

        # 启动后台线程：监控播放状态，歌曲结束后自动播放下一首
        import threading
        self._monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
        self._monitor_thread.start()

        # 记录上一次的播放状态（用于检测播放结束）
        self._last_busy_state = False

    def _monitor_playback(self):
        """
        后台线程：监控播放状态

        每秒检查一次播放状态
        当检测到歌曲播放结束时（从 playing 变为 stopped）
        自动切换到播放列表中的下一首

        注意：这是一个死循环线程，在程序结束前一直运行
        daemon=True 确保主程序结束时自动终止此线程
        """
        import time
        while True:
            try:
                pygame = self._py()
                is_busy = pygame.mixer.music.get_busy()

                # 检测播放结束：从"正在播放"变为"停止"
                if self._last_busy_state and not is_busy and not self.is_paused:
                    # 歌曲已结束，检查是否需要自动播放下一首
                    if self.playlist and len(self.playlist) > 1:
                        # 只有当播放列表有多于一首歌时才自动播放下一首
                        self.current_index = (self.current_index + 1) % len(self.playlist)
                        self.play_current()
                    else:
                        # 只有一首歌或最后一首，播放完毕后停止
                        self.is_playing = False

                # 更新状态
                self._last_busy_state = is_busy
            except Exception:
                # 忽略所有异常，避免线程崩溃
                pass

            # 每秒检查一次
            time.sleep(1)

    def _py(self):
        """
        获取 pygame 模块（懒加载）

        延迟导入 pygame 模块，避免不必要的开销
        在某些情况下 pygame 可能未安装，懒加载可以提供更好的错误处理

        Returns:
            pygame: pygame 模块
        """
        if not hasattr(self, '_pygame') or self._pygame is None:
            import pygame
            self._pygame = pygame
        return self._pygame

    def load(self, file_path: str) -> bool:
        """
        加载音乐文件

        Args:
            file_path: 音乐文件的绝对路径

        Returns:
            bool: 加载是否成功
        """
        pygame = self._py()
        try:
            pygame.mixer.music.load(file_path)
            self.current_track = file_path
            return True
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return False

    def play(self) -> bool:
        """
        开始播放

        开始播放当前已加载的音乐文件

        Returns:
            bool: 播放是否成功
        """
        pygame = self._py()
        try:
            # 设置播放结束事件（用于检测歌曲播放完毕）
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            # 短暂等待，让 pygame 有时间启动
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"Error playing: {e}")
            return False

    def pause(self) -> bool:
        """
        暂停播放

        暂停当前播放的音乐

        Returns:
            bool: 操作是否成功
        """
        pygame = self._py()
        try:
            is_busy = pygame.mixer.music.get_busy()
            if is_busy:
                pygame.mixer.music.pause()
                self.is_paused = True
                return True
            elif self.is_paused:
                # 已经是暂停状态
                return True
            return False
        except Exception as e:
            print(f"Error pausing: {e}")
            return False

    def resume(self) -> bool:
        """
        恢复播放

        恢复已暂停的音乐播放

        Returns:
            bool: 操作是否成功
        """
        pygame = self._py()
        try:
            if self.is_paused:
                # 从暂停状态恢复
                pygame.mixer.music.unpause()
                self.is_paused = False
                return True
            elif not pygame.mixer.music.get_busy():
                # 没有在播放，尝试重新播放当前歌曲
                return self.play_current()
            return False
        except Exception as e:
            print(f"Error resuming: {e}")
            return False

    def stop(self) -> bool:
        """
        停止播放

        完全停止播放，重置播放位置到开头

        Returns:
            bool: 操作是否成功
        """
        pygame = self._py()
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.current_index = 0  # 重置播放索引
            # 重置播放状态，避免后台线程误判为播放结束而重新播放
            self._last_busy_state = False
            return True
        except Exception as e:
            print(f"Error stopping: {e}")
            return False

    def next(self) -> bool:
        """
        播放下一首

        循环播放：播放完最后一首后回到第一首

        Returns:
            bool: 操作是否成功
        """
        if not self.playlist:
            return False
        # 使用模运算实现循环
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self._setup_endevent()
        return self.play_current()

    def previous(self) -> bool:
        """
        播放上一首

        循环播放：播放完第一首后回到最后一首

        Returns:
            bool: 操作是否成功
        """
        if not self.playlist:
            return False
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self._setup_endevent()
        return self.play_current()

    def play_current(self) -> bool:
        """
        播放播放列表中当前索引的歌曲

        Returns:
            bool: 操作是否成功
        """
        if not self.playlist:
            return False
        track = self.playlist[self.current_index]
        if self.load(track.file_path):
            return self.play()
        return False

    def set_playlist(self, tracks: List[Music]):
        """
        设置播放列表

        Args:
            tracks: Music 对象列表
        """
        self.playlist = list(tracks)
        self.current_index = 0

    def play_track(self, track: Music) -> bool:
        """
        播放指定的歌曲

        Args:
            track: Music 对象

        Returns:
            bool: 操作是否成功
        """
        self.current_track = track.file_path
        if self.load(track.file_path):
            return self.play()
        return False

    def play_all(self) -> bool:
        """
        按顺序播放整个播放列表

        Returns:
            bool: 操作是否成功
        """
        if not self.playlist:
            return False
        self.current_index = 0
        self._setup_endevent()
        return self.play_current()

    def shuffle_play(self) -> bool:
        """
        随机播放

        随机打乱播放列表后播放

        Returns:
            bool: 操作是否成功
        """
        if not self.playlist:
            return False
        random.shuffle(self.playlist)
        self.current_index = 0
        self._setup_endevent()
        return self.play_current()

    def _setup_endevent(self):
        """
        设置播放结束事件

        用于检测歌曲播放完毕，触发自动播放下一首
        """
        pygame = self._py()
        try:
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
        except Exception as e:
            print(f"Error setting up endevent: {e}")

    def _check_and_play_next(self) -> bool:
        """
        检查并播放下一首

        由播放结束事件触发

        Returns:
            bool: 是否成功播放下一首
        """
        if not self.playlist:
            return False

        pygame = self._py()
        try:
            # 检查是否有歌曲结束事件
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    return self.next()
        except Exception:
            pass
        return False

    def set_volume(self, volume: float) -> float:
        """
        设置音量

        Args:
            volume: 音量值 (0.0 ~ 1.0)

        Returns:
            float: 实际设置的音量值
        """
        pygame = self._py()
        # 限制在有效范围内
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        return self.volume

    def volume_up(self) -> float:
        """
        增加音量

        每次增加 10% 的音量

        Returns:
            float: 调整后的音量值
        """
        return self.set_volume(self.volume + 0.1)

    def volume_down(self) -> float:
        """
        减少音量

        每次减少 10% 的音量

        Returns:
            float: 调整后的音量值
        """
        return self.set_volume(self.volume - 0.1)

    def get_status(self) -> dict:
        """
        获取当前播放状态

        Returns:
            dict: 包含播放状态的字典:
                - is_playing: 是否正在播放
                - is_paused: 是否已暂停
                - current_track: 当前音乐文件路径
                - current_track_name: 当前音乐文件名（不含路径和扩展名）
                - volume: 当前音量 (0.0 ~ 1.0)
                - playlist_size: 播放列表中的歌曲数量
                - current_index: 当前播放的索引位置
        """
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_track': self.current_track,
            'current_track_name': Path(self.current_track).stem if self.current_track else None,
            'volume': self.volume,
            'playlist_size': len(self.playlist),
            'current_index': self.current_index
        }

    def is_busy(self) -> bool:
        """
        检查是否正在播放

        Returns:
            bool: 是否正在播放（有声音输出）
        """
        pygame = self._py()
        try:
            return pygame.mixer.music.get_busy() > 0
        except Exception:
            return False

    def seek_to(self, position: float) -> bool:
        """
        跳转到指定位置播放

        Args:
            position: 跳转到的位置（单位：秒）

        Returns:
            bool: 操作是否成功
        """
        pygame = self._py()
        try:
            pygame.mixer.music.set_pos(position)
            return True
        except Exception as e:
            print(f"Error seeking: {e}")
            return False


# ==================== MCP Tools ====================
#
# MCP 工具函数列表
# 每个函数都使用 @mcp.tool() 装饰器注册为 MCP 工具
# 客户端（如 Cherry Studio）可以通过调用这些工具来控制音乐播放器
#
# 工具列表:
# - 播放控制: play_artist, play_song, play_genre, play_decade, play_album, play_random, smart_recommend
# - 播放操作: pause, resume, stop, next_track, previous_track, seek_to
# - 音量控制: volume_up, volume_down, set_volume
# - 查询功能: get_player_status, list_artists, list_genres, search_songs, get_user_preferences
# - 库管理: scan_music_library

@mcp.tool()
def play_artist(artist: str) -> str:
    """
    播放指定歌手的歌曲。当用户说"播放XX的歌"、"播放XX的歌曲"、"我想听XX的歌"时调用此工具。

    参数:
        artist: 歌手姓名，如"蔡琴"、"周杰伦"等
    """
    try:
        player = get_player()
        tracks = database_db.get_music_by_artist(artist)
        if tracks:
            player.set_playlist(tracks)
            success = player.shuffle_play()
            for track in tracks[:5]:
                database_db.record_play(track.id)

            status = player.get_status()
            current = status.get('current_track_name', 'Unknown')

            if success:
                return f"正在播放 {artist} 的歌曲，共 {len(tracks)} 首 - 当前: {current}"
            else:
                return f"找到 {len(tracks)} 首 {artist} 的歌曲，但播放失败"
        return f"未找到歌手 {artist} 的歌曲"
    except Exception as e:
        return f"播放出错: {str(e)}"


@mcp.tool()
def play_song(title: str) -> str:
    """
    播放指定的歌曲。当用户说"播放XX"、"播放歌曲XX"、"我想听XX"时调用此工具。

    参数:
        title: 歌曲名称
    """
    player = get_player()
    tracks = database_db.get_music_by_title(title)
    if tracks:
        player.set_playlist(tracks)
        player.play_all()
        for track in tracks[:3]:
            database_db.record_play(track.id)
        return f"正在播放: {tracks[0].title} - {tracks[0].artist or '未知艺术家'}"
    return f"未找到歌曲: {title}"


@mcp.tool()
def play_genre(genre: str) -> str:
    """
    播放指定风格的音乐。当用户说"播放摇滚"、"来首流行歌"、"播放古典音乐"时调用此工具。

    参数:
        genre: 音乐风格，如摇滚、流行、古典、爵士、电子、民谣等
    """
    player = get_player()
    tracks = database_db.get_music_by_genre(genre)
    if tracks:
        player.set_playlist(tracks)
        player.shuffle_play()
        for track in tracks[:5]:
            database_db.record_play(track.id)
        return f"正在播放{genre}音乐，共 {len(tracks)} 首"
    return f"未找到{genre}类型的歌曲"


@mcp.tool()
def play_decade(decade: int) -> str:
    """
    播放指定年代的歌曲。当用户说"播放80年代的歌"、"播放90年代的音乐"时调用此工具。

    参数:
        decade: 年代，如1980代表80年代，1990代表90年代
    """
    player = get_player()
    decade_start = int(decade)
    decade_end = decade_start + 9
    tracks = database_db.get_all_music()
    filtered = [t for t in tracks if t.year and decade_start <= t.year <= decade_end]
    if filtered:
        player.set_playlist(filtered)
        player.shuffle_play()
        for track in filtered[:5]:
            database_db.record_play(track.id)
        return f"正在播放{decade}年代的音乐，共 {len(filtered)} 首"
    return f"未找到{decade}年代的歌曲"


@mcp.tool()
def play_album(album: str) -> str:
    """
    播放指定专辑的歌曲。当用户说"播放专辑XX"时调用此工具。

    参数:
        album: 专辑名称
    """
    player = get_player()
    tracks = database_db.get_music_by_album(album)
    if tracks:
        player.set_playlist(tracks)
        player.play_all()
        for track in tracks[:5]:
            database_db.record_play(track.id)
        return f"正在播放专辑《{album}》，共 {len(tracks)} 首"
    return f"未找到专辑: {album}"


@mcp.tool()
def play_random() -> str:
    """
    随机播放一首歌曲。当用户说"随机播放"、"随便放一首"、"放首随机歌"时调用此工具。
    """
    player = get_player()
    track = database_db.get_random_music()
    if track:
        player.play_track(track)
        database_db.record_play(track.id)
        return f"随机播放: {track.title} - {track.artist or '未知艺术家'}"
    return "没有可播放的歌曲"


@mcp.tool()
def smart_recommend(context: Optional[str] = "") -> str:
    """
    智能推荐歌曲。当用户说"推荐歌曲"、"来首歌"、"放首歌"、"随便放首歌"但不是明确说"随机"时调用此工具。

    参数:
        context: 可选的情境描述，如放松、工作、运动等
    """
    player = get_player()
    prefs = database_db.get_user_preferences()
    tracks = database_db.get_recommended_tracks(limit=10)

    if tracks:
        player.set_playlist(tracks)
        player.shuffle_play()
        for track in tracks[:5]:
            database_db.record_play(track.id)

        reasons = []
        if prefs['top_artists']:
            reasons.append(f"喜欢{prefs['top_artists'][0]}")
        if prefs['top_decades']:
            reasons.append(f"{prefs['top_decades'][0]}年代")
        if prefs['top_genres']:
            reasons.append(f"{prefs['top_genres'][0]}风格")

        if reasons:
            return f"根据您的偏好，为您推荐: {', '.join(reasons)}，共{len(tracks)}首"
        return f"为您推荐10首歌曲"
    return "没有可播放的歌曲"


@mcp.tool()
def pause() -> str:
    """
    暂停当前播放的音乐。必须调用此工具来真正暂停播放！

    触发条件：当用户说"暂停"、"暂停播放"、"不要播放了"、"先暂停"时，必须调用此工具。
    重要：绝对不要只是回复用户"已暂停"，必须调用此工具才能真正暂停音乐！
    """
    player = get_player()
    player.pause()
    return "已暂停"


@mcp.tool()
def resume() -> str:
    """
    继续播放音乐。必须调用此工具来真正恢复播放！

    触发条件：当用户说"继续"、"继续播放"、"恢复播放"、"开始播放"、"播放"时，必须调用此工具。
    重要：绝对不要只是回复用户"继续播放"，必须调用此工具才能真正恢复音乐播放！
    """
    player = get_player()
    player.resume()
    return "继续播放"


@mcp.tool()
def stop() -> str:
    """
    停止播放音乐。必须调用此工具来真正停止播放！

    触发条件：当用户说"停止"、"停止播放"、"不听了"、"关掉"、"别放了"时，必须调用此工具。
    重要：绝对不要只是回复用户"停止了"，必须调用此工具才能真正停止音乐！
    """
    player = get_player()
    player.stop()
    return "已停止"


@mcp.tool()
def next_track() -> str:
    """
    播放下一首。当用户说"下一首"、"下一曲"、"切歌"、"换一首"、"换首歌"、"播放下一首"、"再来一首"时调用此工具。
    """
    player = get_player()
    player.next()
    status = player.get_status()
    if status['current_track_name']:
        return f"正在播放: {status['current_track_name']}"
    return "播放下一首"


@mcp.tool()
def previous_track() -> str:
    """
    播放上一首。当用户说"上一首"、"上一曲"、"上一首歌曲"、"播放上一首"时调用此工具。
    """
    player = get_player()
    player.previous()
    status = player.get_status()
    if status['current_track_name']:
        return f"正在播放: {status['current_track_name']}"
    return "播放上一首"


@mcp.tool()
def volume_up() -> str:
    """
    调高音量。当用户说"声音调大"、"音量调大"、"大声点"、"声音大一点"、"调高音量"、"音量加"、"声音放大"时调用此工具。
    """
    player = get_player()
    vol = player.volume_up()
    return f"音量: {int(vol * 100)}%"


@mcp.tool()
def volume_down() -> str:
    """
    调低音量。当用户说"声音调小"、"音量调小"、"小声点"、"声音小一点"、"调低音量"、"音量减"、"声音放小"时调用此工具。
    """
    player = get_player()
    vol = player.volume_down()
    return f"音量: {int(vol * 100)}%"


@mcp.tool()
def set_volume(volume: float) -> str:
    """
    设置指定音量。当用户说"音量设为50%"、"把音量调到0.5"时调用此工具。

    参数:
        volume: 音量值，0.0到1.0之间，如0.5表示50%
    """
    player = get_player()
    vol = player.set_volume(float(volume))
    return f"音量: {int(vol * 100)}%"


@mcp.tool()
def get_player_status() -> dict:
    """
    获取当前播放状态。当用户说"现在播放的是什么"、"查看播放状态"、"当前播放什么"时调用此工具。
    返回包含播放状态、当前歌曲、音量等信息的字典。
    """
    player = get_player()
    status = player.get_status()
    is_busy = player.is_busy()

    current_track_info = None
    if status['playlist_size'] > 0 and status['current_index'] < len(player.playlist):
        track = player.playlist[status['current_index']]
        current_track_info = {
            'title': track.title,
            'artist': track.artist,
            'album': track.album,
            'year': track.year
        }

    return {
        'is_playing': status['is_playing'],
        'is_paused': status['is_paused'],
        'is_busy': is_busy,
        'current_track': current_track_info,
        'volume': int(status['volume'] * 100),
        'playlist_size': status['playlist_size'],
        'current_index': status['current_index'] + 1
    }


@mcp.tool()
def list_artists(limit: int = 20) -> List[str]:
    """
    列出所有歌手。当用户说"有哪些歌手"、"列出歌手"时调用此工具。

    参数:
        limit: 返回的歌手数量限制，默认20
    """
    artists = database_db.get_all_artists()
    return artists[:int(limit)]


@mcp.tool()
def list_genres(limit: int = 20) -> List[str]:
    """
    列出所有音乐风格。当用户说"有哪些风格"、"列出风格"时调用此工具。

    参数:
        limit: 返回的风格数量限制，默认20
    """
    genres = database_db.get_all_genres()
    return genres[:int(limit)]


@mcp.tool()
def search_songs(keyword: str) -> List[dict]:
    """
    搜索歌曲。当用户说"搜索XX"、"找一首XX"时调用此工具。

    参数:
        keyword: 搜索关键词，会在歌曲名和歌手中搜索
    """
    tracks = database_db.get_music_by_title(keyword)
    artist_tracks = database_db.get_music_by_artist(keyword)

    seen_ids = set()
    results = []
    for track in tracks + artist_tracks:
        if track.id not in seen_ids:
            seen_ids.add(track.id)
            results.append({
                'title': track.title,
                'artist': track.artist,
                'album': track.album,
                'year': track.year,
                'duration': track.duration
            })

    return results[:20]


@mcp.tool()
def get_user_preferences() -> dict:
    """
    获取用户的音乐偏好。当用户说"我平时喜欢听什么"、"我的偏好"时调用此工具。
    返回用户最常听的歌手、年代、风格等信息。
    """
    return database_db.get_user_preferences()


@mcp.tool()
def scan_music_library() -> str:
    """
    重新扫描音乐库。当用户说"扫描音乐"、"更新音乐库"时调用此工具。
    同时会扫描同目录下的.lrc歌词文件。
    """
    from scanner.music_scanner import scan_music
    count = scan_music()
    return f"扫描完成，共添加 {count} 首歌曲"


@mcp.tool()
def seek_to(position: float) -> str:
    """
    跳转到指定位置播放。当用户说"跳到X分X秒"、"快进到"、"播放X分半"时调用此工具。

    参数:
        position: 跳转到的位置，单位为秒。如 60 表示跳转到 1分钟处，90.5 表示 1分30秒处
    """
    player = get_player()

    # 检查是否正在播放
    is_busy = player.is_busy()
    if not is_busy and not player.is_paused:
        return "没有正在播放的歌曲"

    # 获取当前播放列表和位置
    if not player.playlist:
        return "播放列表为空"

    # 获取当前歌曲时长
    current_index = player.current_index
    if current_index >= len(player.playlist):
        return "播放索引无效"

    track = player.playlist[current_index]
    if not track.duration:
        return f"无法获取歌曲时长"

    # 限制跳转范围
    position = max(0.0, min(float(position), float(track.duration)))

    try:
        player.seek_to(position)
        minutes = int(position) // 60
        seconds = int(position) % 60
        return f"已跳转到 {minutes:02d}:{seconds:02d} / {track.duration // 60:02d}:{track.duration % 60:02d}"
    except Exception as e:
        return f"跳转失败: {str(e)}"


def main():
    """Main entry point."""
    init_db()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
