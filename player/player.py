# -*- coding: utf-8 -*-
"""
音乐播放器模块

使用 pygame 实现音频播放功能

功能特性：
- 加载和播放音频文件
- 播放列表管理
- 随机播放、顺序播放
- 音量控制
- 播放状态查询

依赖：
- pygame: Python 多媒体库，用于音频播放
- database.db: 数据库操作模块

作者: AI Assistant
"""

import random
from pathlib import Path

# pygame: Python 游戏开发库
# 此处使用其 mixer 模块进行音频播放
import pygame

import config
import database.db as db


class MusicPlayer:
    """
    音乐播放器类

    封装 pygame.mixer 的播放功能，提供更高级的播放控制接口

    属性:
        current_track: 当前播放的音乐文件路径
        playlist: 播放列表（音乐对象列表）
        current_index: 当前播放的曲目索引
        is_playing: 是否正在播放
        is_paused: 是否已暂停
        volume: 当前音量 (0.0 ~ 1.0)
    """

    def __init__(self):
        """
        初始化音乐播放器

        初始化 pygame mixer，设置默认音量
        """
        # 初始化 pygame 音频混合器
        # 必须在使用任何 mixer 功能前调用
        pygame.mixer.init()

        # 当前播放的曲目（文件路径）
        self.current_track = None

        # 播放列表（Music 对象列表）
        self.playlist = []

        # 当前播放的曲目在播放列表中的索引
        self.current_index = 0

        # 播放状态标志
        self.is_playing = False   # 是否正在播放
        self.is_paused = False   # 是否已暂停

        # 当前音量 (0.0 ~ 1.0)
        # 从配置文件读取默认值
        self.volume = config.DEFAULT_VOLUME

        # 设置初始音量
        pygame.mixer.music.set_volume(self.volume)

    def load(self, file_path):
        """
        加载音乐文件

        Args:
            file_path: 音乐文件的绝对路径

        Returns:
            bool: 加载是否成功
        """
        try:
            pygame.mixer.music.load(file_path)
            self.current_track = file_path
            return True
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return False

    def play(self):
        """
        开始播放已加载的音乐

        Returns:
            bool: 播放是否成功启动
        """
        try:
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            return True
        except Exception as e:
            print(f"Error playing: {e}")
            return False

    def pause(self):
        """
        暂停当前播放

        注意：暂停后可以使用 resume() 恢复播放

        Returns:
            bool: 暂停是否成功
        """
        try:
            pygame.mixer.music.pause()
            self.is_paused = True
            return True
        except Exception as e:
            print(f"Error pausing: {e}")
            return False

    def resume(self):
        """
        恢复暂停的播放

        Returns:
            bool: 恢复播放是否成功
        """
        try:
            pygame.mixer.music.unpause()
            self.is_paused = False
            return True
        except Exception as e:
            print(f"Error resuming: {e}")
            return False

    def stop(self):
        """
        停止播放

        停止后需要重新加载和播放音乐

        Returns:
            bool: 停止是否成功
        """
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            return True
        except Exception as e:
            print(f"Error stopping: {e}")
            return False

    def next(self):
        """
        播放下一首

        如果当前是最后一首，则循环到第一首

        Returns:
            bool: 切换是否成功（播放列表为空时返回 False）
        """
        if not self.playlist:
            return False

        # 循环播放：到达末尾后回到开头
        self.current_index = (self.current_index + 1) % len(self.playlist)
        return self.play_current()

    def previous(self):
        """
        播放上一首

        如果当前是第一首，则循环到最后一首

        Returns:
            bool: 切换是否成功
        """
        if not self.playlist:
            return False

        # 循环播放：到达开头后跳到末尾
        self.current_index = (self.current_index - 1) % len(self.playlist)
        return self.play_current()

    def play_current(self):
        """
        播放播放列表中当前索引对应的曲目

        Returns:
            bool: 播放是否成功
        """
        if not self.playlist:
            return False

        # 获取当前曲目
        track = self.playlist[self.current_index]

        # 加载并播放
        if self.load(track.file_path):
            return self.play()
        return False

    def set_playlist(self, tracks):
        """
        设置播放列表

        Args:
            tracks: 音乐对象列表（Music 模型实例）
        """
        # 转换为列表以支持多种输入类型
        self.playlist = list(tracks)
        # 重置播放索引到开头
        self.current_index = 0

    def play_track(self, track):
        """
        播放指定的单曲

        不影响当前播放列表，仅播放指定曲目

        Args:
            track: Music 对象

        Returns:
            bool: 播放是否成功
        """
        self.current_track = track.file_path
        if self.load(track.file_path):
            return self.play()
        return False

    def play_all(self):
        """
        按顺序播放播放列表中的所有曲目

        从第一首开始，依次播放

        Returns:
            bool: 播放是否成功
        """
        if not self.playlist:
            return False

        # 从第一首开始
        self.current_index = 0
        return self.play_current()

    def shuffle_play(self):
        """
        随机播放播放列表

        随机打乱播放列表后从第一首开始播放

        Returns:
            bool: 播放是否成功
        """
        if not self.playlist:
            return False

        # 随机打乱列表顺序
        random.shuffle(self.playlist)
        self.current_index = 0
        return self.play_current()

    def set_volume(self, volume):
        """
        设置音量

        Args:
            volume: 音量值 (0.0 ~ 1.0)

        Returns:
            float: 实际设置的音量值（会被限制在有效范围内）
        """
        # 确保音量在有效范围内 (0.0 ~ 1.0)
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        return self.volume

    def volume_up(self):
        """
        增加音量 10%

        Returns:
            float: 增大后的音量值
        """
        return self.set_volume(self.volume + 0.1)

    def volume_down(self):
        """
        降低音量 10%

        Returns:
            float: 降低后的音量值
        """
        return self.set_volume(self.volume - 0.1)

    def get_status(self):
        """
        获取播放器当前状态

        Returns:
            dict: 包含播放状态的字典
        """
        return {
            'is_playing': self.is_playing,      # 是否正在播放
            'is_paused': self.is_paused,        # 是否已暂停
            'current_track': self.current_track,  # 当前曲目路径
            'volume': self.volume,              # 当前音量
            'playlist_size': len(self.playlist),  # 播放列表大小
            'current_index': self.current_index   # 当前曲目索引
        }

    def get_current_track_info(self):
        """
        获取当前曲目的详细信息

        从数据库查询当前曲目的元数据

        Returns:
            Music 或 None: 当前曲目的数据库记录
        """
        if not self.current_track:
            return None

        # 从文件路径中提取文件名（不含扩展名）作为查询依据
        # 注意：这种查询方式可能不够精确，建议使用播放列表中的曲目信息
        return db.get_music_by_title(Path(self.current_track).stem)

    def is_busy(self):
        """
        检查是否正在播放

        用于判断音频是否正在播放或处于可播放状态

        Returns:
            bool: 是否有音频正在播放
        """
        return pygame.mixer.music.get_busy() > 0
