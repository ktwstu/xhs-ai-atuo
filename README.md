# XHS Auto - 小红书自动化发布系统

一个基于AI的小红书内容自动生成和发布系统，集成了Google Gemini文本生成、Google Imagen图像生成和xiaohongshu-mcp自动发布功能。

## 功能特点

- 🤖 **AI文本生成**：使用Google Gemini API自动生成小红书风格的标题、内容和标签
- 🎨 **AI图像生成**：使用Google Imagen API根据内容自动生成配图
- 📤 **自动发布**：通过xiaohongshu-mcp服务自动发布到小红书平台
- 📝 **完整工作流**：从主题输入到发布完成的一站式解决方案

## 项目结构

```
xhs-auto/
├── xhs-ai-auto/              # 主程序
│   ├── main.py              # 主入口
│   ├── config/              # 配置模块
│   │   └── settings.py      # 配置文件
│   └── services/            # 服务模块
│       ├── llm_service.py   # AI生成服务
│       └── publish_service.py # 发布服务
├── xiaohongshu-mcp/         # MCP服务（子模块）
├── data/                    # 生成内容存储
├── venv/                    # Python虚拟环境
└── requirements.txt         # Python依赖
```

## 安装指南

### 前置要求

- Python 3.8+
- Go 1.19+（用于xiaohongshu-mcp）
- Google Cloud API密钥（Gemini和Imagen）

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/xhs-auto.git
cd xhs-auto
```

### 2. 安装Python依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

创建`.env`文件并添加以下配置：

```env
# Google AI配置
GEMINI_API_KEY=your_gemini_api_key
IMAGEN_API_KEY=your_imagen_api_key
GEMINI_MODEL_NAME=gemini-1.5-flash
IMAGEN_MODEL_NAME=imagen-4.0-fast-generate-001
```

### 4. 设置xiaohongshu-mcp

克隆并设置xiaohongshu-mcp子模块：

```bash
# 进入xiaohongshu-mcp目录
cd xiaohongshu-mcp

# 下载预编译二进制文件（Windows）
# 从 https://github.com/xpzouying/xiaohongshu-mcp/releases 下载：
# - xiaohongshu-login-windows-amd64.exe
# - xiaohongshu-mcp-windows-amd64.exe
```

## 使用方法

### 1. 首次登录小红书

```bash
cd xiaohongshu-mcp
./xiaohongshu-login-windows-amd64.exe
```

### 2. 启动MCP服务

```bash
# 推荐使用非无头模式
./xiaohongshu-mcp-windows-amd64.exe -headless=false
```

### 3. 运行主程序

在新的终端窗口：

```bash
# 激活虚拟环境
venv\Scripts\activate

# 运行主程序
python xhs-ai-auto/main.py
```

按提示输入主题，系统将自动：
1. 生成文本内容
2. 生成配图
3. 发布到小红书

## 注意事项

### Windows Defender问题

如果遇到"病毒或有害软件"提示，需要将项目文件夹添加到Windows Defender排除项：

1. 打开Windows设置 → 隐私和安全性 → Windows安全中心
2. 进入病毒和威胁防护 → 管理设置
3. 在排除项中添加项目文件夹路径

### 其他注意事项

- 小红书标题限制20个字符
- 每天发帖上限约50篇
- 同一账号不能在多处同时登录
- 首次运行会下载约150MB浏览器组件

## 故障排除

详见[MCP使用注意事项.md](./MCP使用注意事项.md)

## 依赖项目

- [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) - 小红书MCP服务
- [Google Generative AI](https://github.com/googleapis/python-genai) - Google AI SDK

## License

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请提交Issue或联系项目维护者。