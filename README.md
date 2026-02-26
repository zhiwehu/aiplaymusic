# AI Music Player MCP Server

把 AI 音乐播放器变成 MCP 服务器，可以在任何 MCP 客户端（如 Cherry Studio、Claude Desktop）中使用。

## 快速开始

### 方式一：测试运行

```bash
# 安装 uv（如果没有）
pip install uv

# 直接运行测试（仅用于测试 MCP 是否正常工作）
uvx --from "git+https://github.com/zhiwehu/aiplaymusic" ai-music-player
```

### 方式二：配置到 Cherry Studio（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/zhiwehu/aiplaymusic.git
cd aiplaymusic

# 2. 运行安装脚本
python install.py
```

安装脚本会生成 MCP 配置，复制到 Cherry Studio 即可使用。

安装脚本会询问选择 uvx 或本地 Python 方式运行，并生成 MCP 配置供复制。

### 方式三：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/zhiwehu/aiplaymusic.git
cd aiplaymusic

# 2. 创建虚拟环境并安装
python -m venv venv
source venv/bin/activate
pip install -e .
```

## MCP 客户端配置

### Cherry Studio

运行 `python install.py` 后会生成配置，复制即可。手动配置如下：

#### 使用 uvx（推荐）

```json
{
  "mcpServers": {
    "ai-music-player": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/zhiwehu/aiplaymusic",
        "--python",
        "python3",
        "ai-music-player"
      ],
      "env": {
        "MUSIC_DIR": "/path/to/your/music"
      }
    }
  }
}
```

#### 使用本地 Python

```json
{
  "mcpServers": {
    "ai-music-player": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/ai_music_player/__main__.py"],
      "env": {
        "MUSIC_DIR": "/path/to/your/music",
        "DATABASE_PATH": "music.db",
        "DEFAULT_VOLUME": "0.7"
      },
      "enabled": true
    }
  }
}
```

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MUSIC_DIR` | 音乐文件目录 | `./music` |
| `DATABASE_PATH` | 数据库路径 | `music.db` |
| `DEFAULT_VOLUME` | 默认音量 (0.0-1.0) | `0.7` |

## 使用方法

### 播放控制

| 命令 | 说明 |
|------|------|
| 播放 XX 的歌 | 播放特定歌手的歌曲 |
| 播放 XX | 播放特定歌曲 |
| 来首 XX 风格的歌 | 播放特定风格 |
| 播放 80 年代音乐 | 播放特定年代 |
| 随机播放 | 随机播放一首 |
| 推荐歌曲 | 智能推荐 |

### 播放操作

| 命令 | 说明 |
|------|------|
| 暂停 | 暂停播放 |
| 继续 | 继续播放 |
| 停止 | 停止播放 |
| 下一首 | 下一首 |
| 上一首 | 上一首 |
| 音量调大/调小 | 调节音量 |

### 查询功能

| 命令 | 说明 |
|------|------|
| 现在播放什么 | 查看当前播放状态 |
| 列出歌手 | 显示所有歌手 |
| 列出风格 | 显示所有音乐风格 |
| 搜索 XX | 搜索歌曲 |

## 故障排除

### 1. MCP 服务器未连接

- 确保 uvx 或 Python 路径正确
- 重启 MCP 客户端

### 2. 音乐无法播放

- 检查音乐文件是否在指定目录
- 确认音频格式被支持（mp3, flac, wav, m4a, ogg）
- 运行 "扫描音乐库" 重新扫描

### 3. LLM 不调用工具

- 使用更明确的命令："请暂停播放"
- 在系统提示词中添加规则

## 技术栈

- **FastMCP** - MCP 框架
- **pygame** - 音频播放
- **mutagen** - 音乐元数据
- **SQLAlchemy** - 数据存储

## 许可证

MIT License
