# -*- coding: utf-8 -*-
"""
数据库模型定义

使用 SQLAlchemy ORM 定义数据库表结构
包括音乐信息表、播放历史表、用户偏好表

作者: AI Assistant
"""

from datetime import datetime, timezone

# SQLAlchemy 核心组件
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker

import config

# 创建 ORM 基类
# 所有数据库模型类都需要继承此基类
Base = declarative_base()


class Music(Base):
    """
    音乐文件表

    存储扫描到的音乐文件元数据信息
    """
    __tablename__ = "music"

    # 主键自增ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 文件绝对路径（唯一约束，防止重复添加）
    file_path = Column(String(500), unique=True, nullable=False)

    # 音乐元数据
    title = Column(String(255), nullable=True)      # 歌曲标题
    artist = Column(String(255), nullable=True)      # 艺术家/歌手
    album = Column(String(255), nullable=True)       # 专辑名称
    year = Column(Integer, nullable=True)            # 发行年份
    genre = Column(String(100), nullable=True)       # 音乐风格/类型

    # 播放时长（单位：秒）
    duration = Column(Integer, nullable=True)

    # 音频格式（mp3, flac, wav, m4a, ogg）
    # 注意：保留 format 字段名以兼容现有数据库
    format = Column(String(10), nullable=True)

    # 记录创建时间
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """调试用的字符串表示"""
        return f"<Music(id={self.id}, title='{self.title}', artist='{self.artist}')>"


class PlayHistory(Base):
    """
    播放历史记录表

    记录用户每次播放音乐的信息
    用于分析用户偏好和推荐算法
    """
    __tablename__ = "play_history"

    # 主键自增ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 关联的音乐ID（外键）
    music_id = Column(Integer, nullable=False)

    # 播放时间
    played_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 播放完成率 (0.0 ~ 1.0)
    # 用于分析用户是否完整听完歌曲
    completion_rate = Column(Float, default=0.0)

    def __repr__(self):
        return f"<PlayHistory(id={self.id}, music_id={self.music_id}, played_at={self.played_at})>"


class UserPreference(Base):
    """
    用户音乐偏好表

    记录用户对不同歌手、专辑、风格、年代的偏好程度
    用于智能推荐算法
    """
    __tablename__ = "user_preference"

    # 主键自增ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 偏好维度（不同类型记录的偏好）
    artist = Column(String(255), nullable=True)      # 偏好的歌手
    album = Column(String(255), nullable=True)       # 偏好的专辑
    genre = Column(String(100), nullable=True)       # 偏好的风格
    decade = Column(Integer, nullable=True)          # 偏好的年代（如 1980, 1990）

    # 播放次数（累加）
    play_count = Column(Integer, default=0)

    # 最后播放时间
    last_played = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<UserPreference(artist='{self.artist}', genre='{self.genre}', play_count={self.play_count})>"


# ==================== 数据库连接初始化 ====================

# 创建数据库引擎
# 使用 SQLite 数据库，路径从配置中读取
engine = create_engine(
    f"sqlite:///{config.DATABASE_PATH}",
    echo=False  # 调试时可设为 True 查看 SQL 语句
)

# 创建会话工厂
# 每次数据库操作都需要创建新会话
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """
    初始化数据库

    创建所有表结构（如果不存在）
    必须在应用启动时调用一次
    """
    Base.metadata.create_all(engine)


def get_session():
    """
    获取数据库会话

    使用示例:
        session = get_session()
        try:
            # 数据库操作
            session.commit()
        finally:
            session.close()

    Returns:
        Session: SQLAlchemy 会话对象
    """
    return SessionLocal()
