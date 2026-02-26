# -*- coding: utf-8 -*-
"""
播放器模块单元测试

测试 player/player.py 中的播放器功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestMusicPlayerInit:
    """播放器初始化测试类"""

    @patch('player.player.pygame.mixer')
    def test_init_default_values(self, mock_mixer):
        """测试初始化默认属性"""
        from player.player import MusicPlayer

        player = MusicPlayer()

        assert player.current_track is None
        assert player.playlist == []
        assert player.current_index == 0
        assert player.is_playing is False
        assert player.is_paused is False
        # 音量应该是默认配置值
        assert 0.0 <= player.volume <= 1.0

    @patch('player.player.pygame.mixer')
    def test_init_calls_mixer_init(self, mock_mixer):
        """测试初始化调用 mixer.init()"""
        from player.player import MusicPlayer

        player = MusicPlayer()

        mock_mixer.init.assert_called_once()

    @patch('player.player.pygame.mixer')
    def test_init_sets_volume(self, mock_mixer):
        """测试初始化设置音量"""
        from player.player import MusicPlayer

        player = MusicPlayer()

        mock_mixer.music.set_volume.assert_called_once()


class TestMusicPlayerLoad:
    """音乐加载测试类"""

    @patch('player.player.pygame.mixer')
    def test_load_success(self, mock_mixer):
        """测试加载成功"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        result = player.load('/path/to/song.mp3')

        assert result is True
        assert player.current_track == '/path/to/song.mp3'
        mock_mixer.music.load.assert_called_once_with('/path/to/song.mp3')

    @patch('player.player.pygame.mixer')
    def test_load_failure(self, mock_mixer):
        """测试加载失败"""
        from player.player import MusicPlayer

        mock_mixer.music.load.side_effect = Exception("File not found")

        player = MusicPlayer()
        result = player.load('/path/to/invalid.mp3')

        assert result is False


class TestMusicPlayerPlay:
    """播放功能测试类"""

    @patch('player.player.pygame.mixer')
    def test_play_success(self, mock_mixer):
        """测试播放成功"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        result = player.play()

        assert result is True
        assert player.is_playing is True
        assert player.is_paused is False
        mock_mixer.music.play.assert_called_once()

    @patch('player.player.pygame.mixer')
    def test_play_failure(self, mock_mixer):
        """测试播放失败"""
        from player.player import MusicPlayer

        mock_mixer.music.play.side_effect = Exception("No file loaded")

        player = MusicPlayer()
        result = player.play()

        assert result is False


class TestMusicPlayerPause:
    """暂停功能测试类"""

    @patch('player.player.pygame.mixer')
    def test_pause_success(self, mock_mixer):
        """测试暂停成功"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        result = player.pause()

        assert result is True
        assert player.is_paused is True
        mock_mixer.music.pause.assert_called_once()

    @patch('player.player.pygame.mixer')
    def test_pause_failure(self, mock_mixer):
        """测试暂停失败"""
        from player.player import MusicPlayer

        mock_mixer.music.pause.side_effect = Exception("Error")

        player = MusicPlayer()
        result = player.pause()

        assert result is False


class TestMusicPlayerResume:
    """恢复播放测试类"""

    @patch('player.player.pygame.mixer')
    def test_resume_success(self, mock_mixer):
        """测试恢复播放成功"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        player.is_paused = True

        result = player.resume()

        assert result is True
        assert player.is_paused is False
        mock_mixer.music.unpause.assert_called_once()

    @patch('player.player.pygame.mixer')
    def test_resume_failure(self, mock_mixer):
        """测试恢复播放失败"""
        from player.player import MusicPlayer

        mock_mixer.music.unpause.side_effect = Exception("Error")

        player = MusicPlayer()
        result = player.resume()

        assert result is False


class TestMusicPlayerStop:
    """停止播放测试类"""

    @patch('player.player.pygame.mixer')
    def test_stop_success(self, mock_mixer):
        """测试停止成功"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        player.is_playing = True
        player.is_paused = False

        result = player.stop()

        assert result is True
        assert player.is_playing is False
        assert player.is_paused is False
        mock_mixer.music.stop.assert_called_once()

    @patch('player.player.pygame.mixer')
    def test_stop_failure(self, mock_mixer):
        """测试停止失败"""
        from player.player import MusicPlayer

        mock_mixer.music.stop.side_effect = Exception("Error")

        player = MusicPlayer()
        result = player.stop()

        assert result is False


class TestMusicPlayerNextPrevious:
    """下一首/上一首测试类"""

    @patch('player.player.pygame.mixer')
    def test_next_with_playlist(self, mock_mixer):
        """测试下一首（有播放列表）"""
        from player.player import MusicPlayer

        # 创建模拟播放列表
        track1 = MagicMock()
        track1.file_path = '/path/song1.mp3'
        track2 = MagicMock()
        track2.file_path = '/path/song2.mp3'

        player = MusicPlayer()
        player.playlist = [track1, track2]
        player.current_index = 0

        with patch.object(player, 'play_current', return_value=True):
            result = player.next()

        assert result is True
        assert player.current_index == 1

    @patch('player.player.pygame.mixer')
    def test_next_loop_back(self, mock_mixer):
        """测试下一首循环回到开头"""
        from player.player import MusicPlayer

        track1 = MagicMock()
        track1.file_path = '/path/song1.mp3'

        player = MusicPlayer()
        player.playlist = [track1]
        player.current_index = 0

        with patch.object(player, 'play_current', return_value=True):
            result = player.next()

        assert result is True
        assert player.current_index == 0  # 循环回到开头

    @patch('player.player.pygame.mixer')
    def test_next_empty_playlist(self, mock_mixer):
        """测试下一首（空播放列表）"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        player.playlist = []

        result = player.next()

        assert result is False

    @patch('player.player.pygame.mixer')
    def test_previous_with_playlist(self, mock_mixer):
        """测试上一首（有播放列表）"""
        from player.player import MusicPlayer

        track1 = MagicMock()
        track1.file_path = '/path/song1.mp3'
        track2 = MagicMock()
        track2.file_path = '/path/song2.mp3'

        player = MusicPlayer()
        player.playlist = [track1, track2]
        player.current_index = 1

        with patch.object(player, 'play_current', return_value=True):
            result = player.previous()

        assert result is True
        assert player.current_index == 0

    @patch('player.player.pygame.mixer')
    def test_previous_loop_to_end(self, mock_mixer):
        """测试上一首循环到末尾"""
        from player.player import MusicPlayer

        track1 = MagicMock()
        track1.file_path = '/path/song1.mp3'
        track2 = MagicMock()
        track2.file_path = '/path/song2.mp3'

        player = MusicPlayer()
        player.playlist = [track1, track2]
        player.current_index = 0

        with patch.object(player, 'play_current', return_value=True):
            result = player.previous()

        assert result is True
        assert player.current_index == 1  # 循环到末尾


class TestMusicPlayerPlaylist:
    """播放列表测试类"""

    @patch('player.player.pygame.mixer')
    def test_set_playlist(self, mock_mixer):
        """测试设置播放列表"""
        from player.player import MusicPlayer

        track1 = MagicMock()
        track2 = MagicMock()

        player = MusicPlayer()
        player.set_playlist([track1, track2])

        assert len(player.playlist) == 2
        assert player.current_index == 0

    @patch('player.player.pygame.mixer')
    def test_play_all(self, mock_mixer):
        """测试播放全部"""
        from player.player import MusicPlayer

        track1 = MagicMock()
        track1.file_path = '/path/song1.mp3'

        player = MusicPlayer()
        player.playlist = [track1]

        with patch.object(player, 'play_current', return_value=True):
            result = player.play_all()

        assert result is True
        assert player.current_index == 0

    @patch('player.player.pygame.mixer')
    def test_play_all_empty_playlist(self, mock_mixer):
        """测试播放全部（空列表）"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        player.playlist = []

        result = player.play_all()

        assert result is False


class TestMusicPlayerVolume:
    """音量控制测试类"""

    @patch('player.player.pygame.mixer')
    def test_set_volume_in_range(self, mock_mixer):
        """测试设置音量（在有效范围内）"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        result = player.set_volume(0.5)

        assert result == 0.5
        mock_mixer.music.set_volume.assert_called_with(0.5)

    @patch('player.player.pygame.mixer')
    def test_set_volume_above_max(self, mock_mixer):
        """测试设置音量（超过最大值）"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        result = player.set_volume(1.5)

        assert result == 1.0  # 应该被限制到 1.0
        mock_mixer.music.set_volume.assert_called_with(1.0)

    @patch('player.player.pygame.mixer')
    def test_set_volume_below_min(self, mock_mixer):
        """测试设置音量（低于最小值）"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        result = player.set_volume(-0.5)

        assert result == 0.0  # 应该被限制到 0.0
        mock_mixer.music.set_volume.assert_called_with(0.0)

    @patch('player.player.pygame.mixer')
    def test_volume_up(self, mock_mixer):
        """测试增加音量"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        player.volume = 0.5

        result = player.volume_up()

        assert result == 0.6

    @patch('player.player.pygame.mixer')
    def test_volume_up_at_max(self, mock_mixer):
        """测试增加音量（已达最大值）"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        player.volume = 1.0

        result = player.volume_up()

        assert result == 1.0  # 保持在最大值

    @patch('player.player.pygame.mixer')
    def test_volume_down(self, mock_mixer):
        """测试降低音量"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        player.volume = 0.5

        result = player.volume_down()

        assert result == 0.4

    @patch('player.player.pygame.mixer')
    def test_volume_down_at_min(self, mock_mixer):
        """测试降低音量（已达最小值）"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        player.volume = 0.0

        result = player.volume_down()

        assert result == 0.0  # 保持在最小值


class TestMusicPlayerStatus:
    """状态查询测试类"""

    @patch('player.player.pygame.mixer')
    def test_get_status(self, mock_mixer):
        """测试获取状态"""
        from player.player import MusicPlayer

        player = MusicPlayer()
        player.is_playing = True
        player.is_paused = False
        player.current_track = '/path/song.mp3'
        player.volume = 0.7
        player.playlist = [MagicMock(), MagicMock()]
        player.current_index = 1

        status = player.get_status()

        assert status['is_playing'] is True
        assert status['is_paused'] is False
        assert status['current_track'] == '/path/song.mp3'
        assert status['volume'] == 0.7
        assert status['playlist_size'] == 2
        assert status['current_index'] == 1

    @patch('player.player.pygame.mixer')
    def test_get_current_track_info_no_track(self, mock_mixer):
        """测试获取当前曲目信息（无曲目）"""
        from player.player import MusicPlayer

        player = MusicPlayer()

        with patch('player.player.db') as mock_db:
            mock_db.get_music_by_title.return_value = []
            result = player.get_current_track_info()

        assert result is None

    @patch('player.player.pygame.mixer')
    def test_is_busy(self, mock_mixer):
        """测试检查忙碌状态"""
        from player.player import MusicPlayer

        mock_mixer.music.get_busy.return_value = 1

        player = MusicPlayer()
        result = player.is_busy()

        assert result is True

    @patch('player.player.pygame.mixer')
    def test_is_busy_not_playing(self, mock_mixer):
        """测试检查忙碌状态（未播放）"""
        from player.player import MusicPlayer

        mock_mixer.music.get_busy.return_value = 0

        player = MusicPlayer()
        result = player.is_busy()

        assert result is False
