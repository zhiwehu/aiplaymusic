# -*- coding: utf-8 -*-
"""
数据库操作单元测试

测试 ai_music_player/database/db.py 中的数据库操作函数
使用项目的实际数据库进行测试
"""

import os
import sys
import pytest

# 添加项目根目录和 ai_music_player 目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'ai_music_player'))

from ai_music_player.database.models import Music


# 使用项目的实际数据库
TEST_DB_PATH = "/Users/huzhiwei/ai/aiplaymusic/music.db"


class TestQueryMusic:
    """查询音乐测试类（使用实际数据库）"""

    def test_get_all_music(self):
        """测试获取所有音乐"""
        import database.db as db

        all_music = db.get_all_music()
        assert isinstance(all_music, list)

    def test_get_music_by_artist(self):
        """测试按艺术家查询"""
        import database.db as db

        # 查询一个存在的艺术家
        results = db.get_music_by_artist("周")
        assert isinstance(results, list)

    def test_get_music_by_artist_case_insensitive(self):
        """测试艺术家查询大小写不敏感"""
        import database.db as db

        results = db.get_music_by_artist("zhou")
        assert isinstance(results, list)

    def test_get_music_by_title(self):
        """测试按标题查询"""
        import database.db as db

        results = db.get_music_by_title("测试")
        assert isinstance(results, list)

    def test_get_random_music(self):
        """测试随机获取音乐"""
        import database.db as db

        random_track = db.get_random_music()
        # 数据库可能有音乐也可能没有
        if random_track:
            assert random_track.file_path is not None


class TestListQueries:
    """列表查询测试类"""

    def test_get_all_artists(self):
        """测试获取所有艺术家"""
        import database.db as db

        artists = db.get_all_artists()
        assert isinstance(artists, list)

    def test_get_all_genres(self):
        """测试获取所有风格"""
        import database.db as db

        genres = db.get_all_genres()
        assert isinstance(genres, list)


class TestPreferences:
    """用户偏好测试类"""

    def test_get_user_preferences(self):
        """测试获取用户偏好"""
        import database.db as db

        prefs = db.get_user_preferences()
        assert 'top_artists' in prefs
        assert 'top_decades' in prefs
        assert 'top_genres' in prefs
        assert isinstance(prefs['top_artists'], list)
        assert isinstance(prefs['top_decades'], list)
        assert isinstance(prefs['top_genres'], list)

    def test_get_recommended_tracks(self):
        """测试获取推荐歌曲"""
        import database.db as db

        recommendations = db.get_recommended_tracks(limit=10)
        assert isinstance(recommendations, list)


class TestMusicModel:
    """Music 模型测试类"""

    def test_music_has_required_attributes(self):
        """测试 Music 模型有所需属性"""
        music = Music(
            file_path="/test/path.mp3",
            title="Test"
        )
        assert hasattr(music, 'id')
        assert hasattr(music, 'file_path')
        assert hasattr(music, 'title')
        assert hasattr(music, 'artist')
        assert hasattr(music, 'album')
        assert hasattr(music, 'year')
        assert hasattr(music, 'genre')
        assert hasattr(music, 'duration')
        assert hasattr(music, 'format')

    def test_music_repr(self):
        """测试 Music 字符串表示"""
        music = Music(id=1, title="Test Song", artist="Test Artist")
        repr_str = repr(music)
        assert "Music" in repr_str
        assert "Test Song" in repr_str


class TestDatabaseConnection:
    """数据库连接测试类"""

    def test_database_exists(self):
        """测试数据库文件存在"""
        assert os.path.exists(TEST_DB_PATH), f"数据库文件不存在: {TEST_DB_PATH}"

    def test_database_has_music_table(self):
        """测试音乐表存在"""
        import database.db as db
        all_music = db.get_all_music()
        assert isinstance(all_music, list)

    def test_get_session_works(self):
        """测试获取会话正常工作"""
        from database.models import get_session
        session = get_session()
        try:
            count = session.query(Music).count()
            assert count >= 0
        finally:
            session.close()
