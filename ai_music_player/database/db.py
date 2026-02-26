# -*- coding: utf-8 -*-
"""
数据库操作模块

提供音乐数据库的增删改查操作，以及播放历史记录和智能推荐功能

主要功能:
- 音乐元数据管理（添加、查询、删除）
- 播放历史记录
- 用户偏好分析
- 智能推荐算法

作者: AI Assistant
"""

from datetime import datetime, timezone

# SQLAlchemy 聚合函数（用于 count, sum 等）
from sqlalchemy import func

from database.models import Music, PlayHistory, UserPreference, get_session


# ==================== 音乐管理函数 ====================

def add_music(file_path, title, artist=None, album=None, year=None, genre=None, duration=None, format=None):
    """
    添加音乐到数据库

    如果音乐已存在（通过 file_path 判断），则返回现有记录，不会重复添加

    Args:
        file_path: 音乐文件的绝对路径（必填）
        title: 歌曲标题
        artist: 艺术家/歌手
        album: 专辑名称
        year: 发行年份
        genre: 音乐风格
        duration: 播放时长（秒）
        format: 音频格式（mp3, flac 等）

    Returns:
        Music: 添加的音乐记录对象
    """
    session = get_session()
    try:
        # 检查音乐是否已存在
        existing = session.query(Music).filter_by(file_path=file_path).first()
        if existing:
            return existing

        # 创建新音乐记录
        music = Music(
            file_path=file_path,
            title=title,
            artist=artist,
            album=album,
            year=year,
            genre=genre,
            duration=duration,
            format=format
        )
        session.add(music)
        session.commit()
        return music
    finally:
        session.close()


def get_all_music():
    """
    获取所有音乐记录

    Returns:
        List[Music]: 所有音乐记录的列表
    """
    session = get_session()
    try:
        return session.query(Music).all()
    finally:
        session.close()


def get_music_by_artist(artist):
    """
    按艺术家搜索音乐（模糊匹配，大小写不敏感）

    Args:
        artist: 艺术家名称关键词

    Returns:
        List[Music]: 匹配的音乐列表
    """
    session = get_session()
    try:
        # ilike 是大小写不敏感的 LIKE 查询
        return session.query(Music).filter(Music.artist.ilike(f"%{artist}%")).all()
    finally:
        session.close()


def get_music_by_album(album):
    """
    按专辑搜索音乐（模糊匹配）

    Args:
        album: 专辑名称关键词

    Returns:
        List[Music]: 匹配的音乐列表
    """
    session = get_session()
    try:
        return session.query(Music).filter(Music.album.ilike(f"%{album}%")).all()
    finally:
        session.close()


def get_music_by_genre(genre):
    """
    按音乐风格搜索（模糊匹配）

    Args:
        genre: 风格关键词（如 "摇滚", "流行"）

    Returns:
        List[Music]: 匹配的音乐列表
    """
    session = get_session()
    try:
        return session.query(Music).filter(Music.genre.ilike(f"%{genre}%")).all()
    finally:
        session.close()


def get_music_by_year(year):
    """
    按发行年份精确查询

    Args:
        year: 年份（如 1980, 1990）

    Returns:
        List[Music]: 该年份的音乐列表
    """
    session = get_session()
    try:
        return session.query(Music).filter(Music.year == year).all()
    finally:
        session.close()


def get_music_by_title(title):
    """
    按歌曲标题搜索（模糊匹配）

    Args:
        title: 歌曲标题关键词

    Returns:
        List[Music]: 匹配的音乐列表
    """
    session = get_session()
    try:
        return session.query(Music).filter(Music.title.ilike(f"%{title}%")).all()
    finally:
        session.close()


def get_random_music():
    """
    随机获取一首音乐

    用于"随机播放"功能

    Returns:
        Music: 随机的音乐记录，如果没有音乐则返回 None
    """
    session = get_session()
    try:
        # SQLite 使用 RANDOM() 函数随机排序
        return session.query(Music).order_by(func.random()).first()
    finally:
        session.close()


def delete_music(file_path):
    """
    从数据库删除音乐记录

    Args:
        file_path: 音乐文件的绝对路径

    Returns:
        bool: 是否删除成功
    """
    session = get_session()
    try:
        music = session.query(Music).filter_by(file_path=file_path).first()
        if music:
            session.delete(music)
            session.commit()
            return True
        return False
    finally:
        session.close()


# ==================== 列表查询函数 ====================

def get_all_artists():
    """
    获取所有艺术家列表（去重）

    Returns:
        List[str]: 艺术家名称列表
    """
    session = get_session()
    try:
        # distinct() 去重，然后过滤掉 None 值
        return [m.artist for m in session.query(Music.artist).distinct().all() if m.artist]
    finally:
        session.close()


def get_all_genres():
    """
    获取所有音乐风格列表（去重）

    Returns:
        List[str]: 风格名称列表
    """
    session = get_session()
    try:
        return [m.genre for m in session.query(Music.genre).distinct().all() if m.genre]
    finally:
        session.close()


# ==================== 播放历史与推荐 ====================

def record_play(music_id, completion_rate=1.0):
    """
    记录播放历史并更新用户偏好

    当用户播放一首歌曲时调用此函数：
    1. 在 PlayHistory 中记录播放事件
    2. 在 UserPreference 中更新用户对歌手、专辑、风格、年代的偏好

    Args:
        music_id: 音乐的数据库 ID
        completion_rate: 播放完成率 (0.0 ~ 1.0)，默认为 1.0（完整播放）
    """
    session = get_session()
    try:
        # 1. 添加播放历史记录
        history = PlayHistory(music_id=music_id, completion_rate=completion_rate)
        session.add(history)

        # 2. 获取音乐元数据
        music = session.query(Music).filter_by(id=music_id).first()
        if not music:
            session.commit()
            return

        # 3. 更新用户偏好
        # 定义更新偏好的辅助函数
        def update_preference(category, value):
            """更新单个类别的用户偏好"""
            if not value:
                return

            # 查找现有偏好记录
            pref = session.query(UserPreference).filter_by(**{category: value}).first()

            if pref:
                # 已有记录，累加播放次数
                pref.play_count += 1
                pref.last_played = datetime.now(timezone.utc)
            else:
                # 新建偏好记录
                pref = UserPreference(**{category: value}, play_count=1)
                session.add(pref)

        # 更新四个维度的偏好
        update_preference('artist', music.artist)
        update_preference('album', music.album)
        update_preference('genre', music.genre)

        # 年代处理（将具体年份转换为年代，如 1985 -> 1980）
        if music.year:
            decade = (music.year // 10) * 10
            update_preference('decade', decade)

        session.commit()
    finally:
        session.close()


def get_user_preferences():
    """
    获取用户音乐偏好

    通过聚合查询统计用户最常播放的：
    - 歌手（Top 5）
    - 年代（Top 3）
    - 风格（Top 3）

    Returns:
        dict: 包含 top_artists, top_decades, top_genres 的字典
    """
    session = get_session()
    try:
        # 查询播放次数最多的艺术家
        top_artists = session.query(
            UserPreference.artist,
            func.sum(UserPreference.play_count).label('total')
        ).filter(
            UserPreference.artist.isnot(None)
        ).group_by(
            UserPreference.artist
        ).order_by(
            func.sum(UserPreference.play_count).desc()
        ).limit(5).all()

        # 查询播放次数最多的年代
        top_decades = session.query(
            UserPreference.decade,
            func.sum(UserPreference.play_count).label('total')
        ).filter(
            UserPreference.decade.isnot(None)
        ).group_by(
            UserPreference.decade
        ).order_by(
            func.sum(UserPreference.play_count).desc()
        ).limit(3).all()

        # 查询播放次数最多的风格
        top_genres = session.query(
            UserPreference.genre,
            func.sum(UserPreference.play_count).label('total')
        ).filter(
            UserPreference.genre.isnot(None)
        ).group_by(
            UserPreference.genre
        ).order_by(
            func.sum(UserPreference.play_count).desc()
        ).limit(3).all()

        # 构建返回结果
        return {
            'top_artists': [a[0] for a in top_artists if a[0]],
            'top_decades': [d[0] for d in top_decades if d[0]],
            'top_genres': [g[0] for g in top_genres if g[0]]
        }
    finally:
        session.close()


def get_recommended_tracks(limit=10):
    """
    根据用户偏好推荐音乐

    推荐算法优先级：
    1. 用户最常听的歌手
    2. 用户最常听的年代
    3. 用户最常听的风格
    4. 如果推荐不足，随机填充

    Args:
        limit: 返回的推荐数量，默认 10 首

    Returns:
        List[Music]: 推荐的音乐列表
    """
    session = get_session()
    try:
        # 获取用户偏好
        prefs = get_user_preferences()

        # 如果没有偏好记录，返回随机音乐
        if not prefs['top_artists'] and not prefs['top_decades']:
            return session.query(Music).order_by(func.random()).limit(limit).all()

        # 构建推荐列表
        results = []
        seen_ids = set()  # 用于去重

        # 优先级 1: 用户喜欢的歌手
        for artist in prefs['top_artists'][:3]:
            tracks = session.query(Music).filter(
                Music.artist.ilike(f"%{artist}%")
            ).limit(5).all()
            for t in tracks:
                if t.id not in seen_ids:
                    results.append(t)
                    seen_ids.add(t.id)

        # 优先级 2: 用户喜欢的年代
        for decade in prefs['top_decades'][:2]:
            if decade:
                tracks = session.query(Music).filter(
                    Music.year >= decade,
                    Music.year < decade + 10
                ).limit(5).all()
                for t in tracks:
                    if t.id not in seen_ids:
                        results.append(t)
                        seen_ids.add(t.id)

        # 优先级 3: 用户喜欢的风格
        for genre in prefs['top_genres'][:2]:
            if genre:
                tracks = session.query(Music).filter(
                    Music.genre.ilike(f"%{genre}%")
                ).limit(5).all()
                for t in tracks:
                    if t.id not in seen_ids:
                        results.append(t)
                        seen_ids.add(t.id)

        # 如果推荐数量不足，随机填充
        if len(results) < limit:
            remaining = limit - len(results)
            random_tracks = session.query(Music).order_by(
                func.random()
            ).limit(remaining).all()
            for t in random_tracks:
                if t.id not in seen_ids:
                    results.append(t)

        return results[:limit]
    finally:
        session.close()
