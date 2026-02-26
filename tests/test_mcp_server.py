# -*- coding: utf-8 -*-
"""
MCP 服务器单元测试

测试 mcp_server.py 中的 MCP 工具函数
使用实际项目数据库进行测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestMCPConfig:
    """MCP 配置测试类"""

    def test_mcp_server_exists(self):
        """测试 MCP 服务器模块是否存在"""
        import mcp_server
        assert mcp_server is not None


class TestControlFunctions:
    """控制功能测试类"""

    def test_pause_function(self):
        """测试暂停函数"""
        with patch('mcp_server.get_player') as mock_get:
            player = MagicMock()
            player.pause.return_value = True
            mock_get.return_value = player

            from mcp_server import pause
            result = pause()

            assert result == "已暂停"
            player.pause.assert_called_once()

    def test_resume_function(self):
        """测试继续播放函数"""
        with patch('mcp_server.get_player') as mock_get:
            player = MagicMock()
            player.resume.return_value = True
            mock_get.return_value = player

            from mcp_server import resume
            result = resume()

            assert result == "继续播放"
            player.resume.assert_called_once()

    def test_stop_function(self):
        """测试停止函数"""
        with patch('mcp_server.get_player') as mock_get:
            player = MagicMock()
            player.stop.return_value = True
            mock_get.return_value = player

            from mcp_server import stop
            result = stop()

            assert result == "已停止"
            player.stop.assert_called_once()

    def test_next_track_function(self):
        """测试下一首函数"""
        with patch('mcp_server.get_player') as mock_get:
            player = MagicMock()
            player.next.return_value = True
            player.get_status.return_value = {
                'current_track_name': 'Next Song'
            }
            mock_get.return_value = player

            from mcp_server import next_track
            result = next_track()

            assert "下一首" in result or "正在播放" in result


class TestVolumeFunctions:
    """音量控制测试类"""

    def test_volume_up_function(self):
        """测试音量增加函数"""
        with patch('mcp_server.get_player') as mock_get:
            player = MagicMock()
            player.volume_up.return_value = 0.8
            mock_get.return_value = player

            from mcp_server import volume_up
            result = volume_up()

            assert "80%" in result
            player.volume_up.assert_called_once()

    def test_volume_down_function(self):
        """测试音量降低函数"""
        with patch('mcp_server.get_player') as mock_get:
            player = MagicMock()
            player.volume_down.return_value = 0.6
            mock_get.return_value = player

            from mcp_server import volume_down
            result = volume_down()

            assert "60%" in result
            player.volume_down.assert_called_once()

    def test_set_volume_function(self):
        """测试设置音量函数"""
        with patch('mcp_server.get_player') as mock_get:
            player = MagicMock()
            player.set_volume.return_value = 0.5
            mock_get.return_value = player

            from mcp_server import set_volume
            result = set_volume(0.5)

            assert "50%" in result
            player.set_volume.assert_called_once_with(0.5)


class TestDatabaseFunctions:
    """数据库功能测试类（使用 db 模块）"""

    def test_get_all_artists_via_db(self):
        """测试获取所有艺术家"""
        import database.db as db
        artists = db.get_all_artists()
        assert isinstance(artists, list)

    def test_get_all_genres_via_db(self):
        """测试获取所有风格"""
        import database.db as db
        genres = db.get_all_genres()
        assert isinstance(genres, list)


class TestMCPFunctions:
    """MCP 工具函数存在性测试"""

    def test_tools_exist(self):
        """测试主要 MCP 工具函数都存在"""
        from mcp_server import (
            play_artist, play_song, play_genre,
            play_album, play_random, smart_recommend, pause, resume, stop,
            next_track, previous_track, volume_up, volume_down,
            set_volume, get_player_status,
            list_artists, list_genres, search_songs,
            scan_music_library, seek_to
        )
        assert callable(play_artist)
        assert callable(pause)
        assert callable(stop)

    def test_mcp_decorator_works(self):
        """测试 MCP 装饰器正常工作"""
        import mcp_server
        assert hasattr(mcp_server, 'mcp')
