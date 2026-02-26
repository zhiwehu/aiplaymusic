# -*- coding: utf-8 -*-
"""
数据库模型单元测试

测试 ai_music_player/database/models.py 中的模型定义
"""

import os
import sys
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录和 ai_music_player 目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'ai_music_player'))

from ai_music_player.database.models import Base, Music, PlayHistory, UserPreference


class TestMusicModel:
    """Music 模型测试类"""

    @pytest.fixture
    def engine(self):
        """创建内存数据库引擎"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine):
        """创建数据库会话"""
        Session = sessionmaker(bind=engine)
        return Session()

    def test_music_table_name(self):
        """测试 Music 表名"""
        assert Music.__tablename__ == "music"

    def test_music_columns(self):
        """测试 Music 模型列定义"""
        columns = [c.name for c in Music.__table__.columns]
        expected_columns = ['id', 'file_path', 'title', 'artist', 'album',
                           'year', 'genre', 'duration', 'format', 'created_at']
        for col in expected_columns:
            assert col in columns

    def test_music_file_path_unique(self):
        """测试 file_path 是否有唯一约束"""
        file_path_column = Music.__table__.columns['file_path']
        assert file_path_column.unique is True

    def test_music_file_path_not_nullable(self):
        """测试 file_path 是否为必填"""
        file_path_column = Music.__table__.columns['file_path']
        assert not file_path_column.nullable

    def test_music_repr(self):
        """测试 Music 字符串表示"""
        music = Music(id=1, title="Test Song", artist="Test Artist")
        repr_str = repr(music)
        assert "Music" in repr_str
        assert "Test Song" in repr_str
        assert "Test Artist" in repr_str

    def test_music_create_and_query(self, session):
        """测试 Music 创建和查询"""
        music = Music(
            file_path="/path/to/song.mp3",
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            year=2023,
            genre="Pop",
            duration=180,
            format="mp3"
        )
        session.add(music)
        session.commit()

        # 查询
        result = session.query(Music).filter_by(title="Test Song").first()
        assert result is not None
        assert result.artist == "Test Artist"
        assert result.album == "Test Album"
        assert result.year == 2023


class TestPlayHistoryModel:
    """PlayHistory 模型测试类"""

    @pytest.fixture
    def engine(self):
        """创建内存数据库引擎"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine):
        """创建数据库会话"""
        Session = sessionmaker(bind=engine)
        return Session()

    def test_play_history_table_name(self):
        """测试 PlayHistory 表名"""
        assert PlayHistory.__tablename__ == "play_history"

    def test_play_history_columns(self):
        """测试 PlayHistory 模型列定义"""
        columns = [c.name for c in PlayHistory.__table__.columns]
        expected_columns = ['id', 'music_id', 'played_at', 'completion_rate']
        for col in expected_columns:
            assert col in columns

    def test_play_history_repr(self):
        """测试 PlayHistory 字符串表示"""
        history = PlayHistory(id=1, music_id=10)
        repr_str = repr(history)
        assert "PlayHistory" in repr_str
        assert "music_id=10" in repr_str

    def test_play_history_create(self, session):
        """测试 PlayHistory 创建"""
        history = PlayHistory(music_id=1, completion_rate=0.8)
        session.add(history)
        session.commit()

        result = session.query(PlayHistory).first()
        assert result.music_id == 1
        assert result.completion_rate == 0.8

    def test_play_history_default_completion_rate(self, session):
        """测试 completion_rate 默认值"""
        history = PlayHistory(music_id=1)
        session.add(history)
        session.commit()

        result = session.query(PlayHistory).first()
        assert result.completion_rate == 0.0


class TestUserPreferenceModel:
    """UserPreference 模型测试类"""

    @pytest.fixture
    def engine(self):
        """创建内存数据库引擎"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine):
        """创建数据库会话"""
        Session = sessionmaker(bind=engine)
        return Session()

    def test_user_preference_table_name(self):
        """测试 UserPreference 表名"""
        assert UserPreference.__tablename__ == "user_preference"

    def test_user_preference_columns(self):
        """测试 UserPreference 模型列定义"""
        columns = [c.name for c in UserPreference.__table__.columns]
        expected_columns = ['id', 'artist', 'album', 'genre', 'decade',
                           'play_count', 'last_played']
        for col in expected_columns:
            assert col in columns

    def test_user_preference_repr(self):
        """测试 UserPreference 字符串表示"""
        pref = UserPreference(artist="Test Artist", genre="Rock", play_count=5)
        repr_str = repr(pref)
        assert "UserPreference" in repr_str
        assert "Test Artist" in repr_str

    def test_user_preference_create(self, session):
        """测试 UserPreference 创建"""
        pref = UserPreference(
            artist="周杰伦",
            genre="流行",
            play_count=10
        )
        session.add(pref)
        session.commit()

        result = session.query(UserPreference).first()
        assert result.artist == "周杰伦"
        assert result.genre == "流行"
        assert result.play_count == 10

    def test_user_preference_default_play_count(self, session):
        """测试 play_count 默认值"""
        pref = UserPreference(artist="Test")
        session.add(pref)
        session.commit()

        result = session.query(UserPreference).first()
        assert result.play_count == 0


class TestDatabaseInit:
    """数据库初始化测试类"""

    def test_init_db_creates_tables(self):
        """测试 init_db 是否创建表"""
        import tempfile
        from database import models

        # 使用临时数据库
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            # 修改数据库路径
            engine = create_engine(f"sqlite:///{db_path}")

            # 调用 init_db
            models.Base.metadata.create_all(engine)

            # 验证表已创建
            assert 'music' in models.Base.metadata.tables
            assert 'play_history' in models.Base.metadata.tables
            assert 'user_preference' in models.Base.metadata.tables
        finally:
            os.unlink(db_path)

    def test_get_session_returns_session(self):
        """测试 get_session 是否返回会话对象"""
        from database.models import get_session
        session = get_session()
        try:
            assert session is not None
        finally:
            session.close()
