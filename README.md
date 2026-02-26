# AI Music Player MCP Server

把 AI 音乐播放器变成 MCP 服务器，可以在任何 MCP 客户端（如 Cherry Studio、Claude Desktop）中使用。

## 快速开始

### 方式一：使用安装脚本（推荐）

```bash
# 1. 克隆或下载项目
git clone https://github.com/yourname/ai-music-player.git
cd ai-music-player

# 2. 运行安装脚本
python install.py
```

安装脚本会自动：
- 检查并安装依赖
- 配置 MCP 客户端（Claude Desktop / Cherry Studio）
- 生成配置文件

### 方式二：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/yourname/ai-music-player.git
cd ai-music-player

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 3. 安装
pip install -e .

# 4. 配置 MCP 客户端
# 复制 mcp_config.json 内容到你的 MCP 客户端配置中
```

## 配置说明

### 环境变量

可以在 `.env` 文件中配置以下选项：

```bash
# 音乐文件目录（可选，默认为 ./music）
MUSIC_DIR=/path/to/your/music

# 数据库路径（可选，默认为 ./music.db）
DATABASE_PATH=music.db

# 默认音量 0.0~1.0（可选，默认为 0.7）
DEFAULT_VOLUME=0.7
```

### MCP 客户端配置

#### Claude Desktop

在 `~/Library/Application Support/Claude/claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "ai-music-player": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

#### Cherry Studio

在设置 → MCP 服务器中添加：
- 名称: AI Music Player
- 类型: Command
- 命令: `/path/to/venv/bin/python`
- 参数: `/path/to/mcp_server.py`

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

## 示例对话

```
用户: 播放周杰伦的歌
AI: [调用 play_artist 工具] 正在播放周杰伦的歌曲，共 XX 首

用户: 暂停
AI: [调用 pause 工具] 已暂停

用户: 来首歌推荐一下
AI: [调用 smart_recommend 工具] 根据您的偏好，为您推荐...
```

## 故障排除

### 1. MCP 服务器未连接

- 检查 Python 路径是否正确
- 确认依赖已安装
- 重启 MCP 客户端

### 2. 音乐无法播放

- 检查音乐文件是否在 `music` 目录
- 确认音频格式被支持（mp3, flac, wav, m4a, ogg）
- 运行 "扫描音乐库" 重新扫描

### 3. LLM 不调用工具

有些 LLM 可能会直接回复而不调用工具。尝试：
- 使用更明确的命令："请暂停播放"
- 在系统提示词中添加规则

## 技术栈

- **FastMCP** - MCP 框架
- **pygame** - 音频播放
- **mutagen** - 音乐元数据
- **SQLAlchemy** - 数据存储

## 许可证

MIT License
