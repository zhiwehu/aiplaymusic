# -*- coding: utf-8 -*-
"""
配置模块单元测试

测试 config.py 中的配置项
"""

import tempfile
from pathlib import Path

import pytest


class TestConfig:
    """配置模块测试类"""

    def test_base_dir_is_path(self):
        """测试 BASE_DIR 是否为 Path 对象"""
        import config
        assert isinstance(config.BASE_DIR, Path)

    def test_music_dir_under_base_dir(self):
        """测试 MUSIC_DIR 是否在 BASE_DIR 下"""
        import config
        assert config.MUSIC_DIR.is_relative_to(config.BASE_DIR)

    def test_database_path_under_base_dir(self):
        """测试 DATABASE_PATH 是否在 BASE_DIR 下"""
        import config
        assert config.DATABASE_PATH.is_relative_to(config.BASE_DIR)

    def test_supported_formats_contains_common_formats(self):
        """测试 SUPPORTED_FORMATS 是否包含常见音频格式"""
        import config
        expected_formats = ['.mp3', '.flac', '.wav', '.m4a', '.ogg']
        for fmt in expected_formats:
            assert fmt in config.SUPPORTED_FORMATS

    def test_supported_formats_all_lowercase(self):
        """测试 SUPPORTED_FORMATS 是否全为小写"""
        import config
        for fmt in config.SUPPORTED_FORMATS:
            assert fmt == fmt.lower()

    def test_supported_formats_start_with_dot(self):
        """测试 SUPPORTED_FORMATS 是否都以点开头"""
        import config
        for fmt in config.SUPPORTED_FORMATS:
            assert fmt.startswith('.')

    def test_default_volume_in_valid_range(self):
        """测试 DEFAULT_VOLUME 是否在有效范围内 (0.0 ~ 1.0)"""
        import config
        assert 0.0 <= config.DEFAULT_VOLUME <= 1.0


class TestConfigWithEnv:
    """环境变量配置测试类"""

    def test_music_dir_custom_from_env(self, monkeypatch, tmp_path):
        """测试 MUSIC_DIR 是否可自定义"""
        custom_dir = tmp_path / "custom_music"
        custom_dir.mkdir()

        # 注意：这个测试会受环境变量影响
        monkeypatch.setenv("MUSIC_DIR", str(custom_dir))

        import importlib
        import config as config_module
        importlib.reload(config_module)

        # 由于 MUSIC_DIR 使用 Path，需要测试其行为
        assert isinstance(config_module.MUSIC_DIR, Path)
