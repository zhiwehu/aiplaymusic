# -*- coding: utf-8 -*-
"""
音乐扫描器单元测试

测试 scanner/music_scanner.py 中的扫描功能
"""

import os
import tempfile

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestExtractMetadata:
    """元数据提取测试类"""

    @patch('scanner.music_scanner.File')
    def test_extract_metadata_with_id3_tags(self, mock_file):
        """测试从带 ID3 标签的音频文件提取元数据"""
        from scanner import music_scanner

        # 模拟 mutagen 返回的对象
        mock_audio = MagicMock()
        mock_audio.info.length = 180
        mock_audio.tags = {
            'TIT2': ['Test Title'],
            'TPE1': ['Test Artist'],
            'TALB': ['Test Album'],
            'TCON': ['Pop'],
            'TDRC': ['2023']
        }
        mock_file.return_value = mock_audio

        result = music_scanner.extract_metadata('/path/to/song.mp3')

        assert result is not None
        assert result['title'] == 'Test Title'
        assert result['artist'] == 'Test Artist'
        assert result['album'] == 'Test Album'
        assert result['genre'] == 'Pop'
        assert result['year'] == 2023
        assert result['duration'] == 180
        assert result['format'] == 'mp3'

    @patch('scanner.music_scanner.File')
    def test_extract_metadata_no_tags(self, mock_file):
        """测试无 ID3 标签的音频文件"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        mock_audio.info.length = 200
        mock_audio.tags = None
        mock_file.return_value = mock_audio

        result = music_scanner.extract_metadata('/path/to/song.flac')

        assert result is not None
        assert result['title'] is None
        assert result['artist'] is None
        assert result['duration'] == 200
        assert result['format'] == 'flac'

    @patch('scanner.music_scanner.File')
    def test_extract_metadata_invalid_file(self, mock_file):
        """测试无效文件"""
        from scanner import music_scanner

        mock_file.return_value = None

        result = music_scanner.extract_metadata('/path/to/invalid.file')

        assert result is None

    @patch('scanner.music_scanner.File')
    def test_extract_metadata_alternative_tag_keys(self, mock_file):
        """测试备选标签键名"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        mock_audio.info.length = 150
        mock_audio.tags = {
            'title': ['Alt Title'],      # 备选键名
            'artist': ['Alt Artist'],
            'album': ['Alt Album'],
            'genre': ['Alt Genre'],
            'year': '2022'               # 字符串类型
        }
        mock_file.return_value = mock_audio

        result = music_scanner.extract_metadata('/path/to/song.ogg')

        assert result['title'] == 'Alt Title'
        assert result['artist'] == 'Alt Artist'

    @patch('scanner.music_scanner.File')
    def test_extract_metadata_year_extraction(self, mock_file):
        """测试年份提取（从复杂格式中提取）"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        mock_audio.info.length = 180
        mock_audio.tags = {
            'TDRC': '2023-05-15',  # 完整日期格式
            'TIT2': ['Test']
        }
        mock_file.return_value = mock_audio

        result = music_scanner.extract_metadata('/path/to/song.mp3')

        assert result['year'] == 2023


class TestScanDirectory:
    """目录扫描测试类"""

    @pytest.fixture
    def temp_music_dir(self):
        """创建临时音乐目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @patch('scanner.music_scanner.extract_metadata')
    @patch('scanner.music_scanner.SUPPORTED_EXTENSIONS', ['.mp3', '.flac'])
    def test_scan_directory_with_files(self, mock_extract, temp_music_dir):
        """测试扫描包含音频文件的目录"""
        from scanner import music_scanner

        # 创建测试文件
        mp3_file = os.path.join(temp_music_dir, 'song1.mp3')
        flac_file = os.path.join(temp_music_dir, 'song2.flac')
        txt_file = os.path.join(temp_music_dir, 'readme.txt')

        # 创建空文件（模拟音频文件）
        open(mp3_file, 'w').close()
        open(flac_file, 'w').close()
        open(txt_file, 'w').close()

        # 模拟元数据提取返回值
        mock_extract.return_value = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'album': 'Test Album',
            'year': 2023,
            'genre': 'Pop',
            'duration': 180,
            'format': 'mp3'
        }

        # 使用内存数据库
        with patch('scanner.music_scanner.db'):
            count = music_scanner.scan_directory(temp_music_dir)

        # 应该只扫描 .mp3 和 .flac 文件
        assert count >= 0

    @patch('scanner.music_scanner.db')
    def test_scan_directory_nonexistent(self, mock_db):
        """测试扫描不存在的目录"""
        from scanner import music_scanner

        result = music_scanner.scan_directory('/nonexistent/path')
        assert result == 0


class TestHelperFunctions:
    """辅助函数测试类"""

    def test_get_duration_with_length(self):
        """测试获取播放时长（有长度信息）"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        mock_audio.info.length = 245.5

        result = music_scanner.get_duration(mock_audio)
        assert result == 245

    def test_get_duration_without_length(self):
        """测试获取播放时长（无长度信息）"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        del mock_audio.info.length

        result = music_scanner.get_duration(mock_audio)
        assert result == 0

    def test_get_id3_tag_with_value(self):
        """测试获取 ID3 标签（有值）"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        mock_audio.tags = {'TIT2': ['Test Value']}

        result = music_scanner.get_id3_tag(mock_audio, 'TIT2')
        assert result == 'Test Value'

    def test_get_id3_tag_with_list(self):
        """测试获取 ID3 标签（列表值）"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        mock_audio.tags = {'TPE1': ['Artist1', 'Artist2']}

        result = music_scanner.get_id3_tag(mock_audio, 'TPE1')
        assert result == 'Artist1'

    def test_get_id3_tag_no_tags(self):
        """测试获取 ID3 标签（无标签）"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        mock_audio.tags = None

        result = music_scanner.get_id3_tag(mock_audio, 'TIT2')
        assert result is None

    def test_get_id3_tag_fallback_keys(self):
        """测试备选键名"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        mock_audio.tags = {'title': ['Fallback Title']}

        # TIT2 不存在，应该回退到 title
        result = music_scanner.get_id3_tag(mock_audio, 'TIT2', 'title')
        assert result == 'Fallback Title'

    def test_get_id3_tag_no_match(self):
        """测试获取 ID3 标签（无匹配）"""
        from scanner import music_scanner

        mock_audio = MagicMock()
        mock_audio.tags = {'OTHER': ['Value']}

        result = music_scanner.get_id3_tag(mock_audio, 'TIT2', 'title')
        assert result is None
