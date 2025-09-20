# XHS-ai-auto - 小红书自动化发布系统

一个基于AI的小红书内容自动生成和发布系统，支持多个AI提供商（Google、ModelScope、DashScope），实现文本和图像的智能生成及自动发布。

## 功能特点

- 🤖 **多AI提供商支持**：
  - Google (Gemini + Imagen)-ok	（main）
  - ModelScope API-Inference (2000次/天免费额度)-ok	分支（branch：feature/modelscope-api）
  - DashScope/阿里云百炼 (通义千问 + 通义万相)--没测试
- 🎨 **智能图像生成**：根据内容自动生成高质量配图
- 📤 **自动发布**：通过xiaohongshu-mcp服务自动发布到小红书平台
- 🔄 **灵活切换**：通过配置文件轻松切换不同的AI服务
- 📝 **完整工作流**：从主题输入到发布完成的一站式解决方案

## 项目结构

```
xhs-auto/
├── xhs-ai-auto/              # 主程序
│   ├── main.py              # 主入口
│   ├── config/              # 配置模块
│   │   └── settings.py      # 配置文件
│   └── services/            # 服务模块
│       ├── ai_service.py    # AI服务抽象接口
│       ├── google_service.py # Google AI实现
│       ├── modelscope_service.py # ModelScope实现
│       ├── dashscope_service.py  # DashScope实现
│       ├── service_factory.py    # 服务工厂
│       └── publish_service.py    # 发布服务
├── xiaohongshu-mcp/         # MCP服务（子模块）
├── data/                    # 生成内容存储
├── venv/                    # Python虚拟环境
└── requirements.txt         # Python依赖
```

## 安装指南

### 前置要求

- Python 3.8+
- Go 1.19+（用于xiaohongshu-mcp，）
- AI服务密钥（至少配置一个）：
  - Google Cloud API密钥（Gemini和Imagen）
  - 或 ModelScope API Token（总共免费2000次/天）
  - 或 DashScope/阿里云百炼 API密钥

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
# === AI Provider Selection ===
# 选择要使用的AI提供商: google, modelscope, dashscope
AI_PROVIDER=google

# === Google AI配置（如果使用Google） ===
GEMINI_API_KEY=your_gemini_api_key
IMAGEN_API_KEY=your_imagen_api_key

# === ModelScope配置（如果使用ModelScope） ===
# 免费2000次/天，获取Token: https://modelscope.cn/my/myaccesstoken
MODELSCOPE_API_KEY=your_modelscope_token

# === DashScope配置（如果使用阿里云百炼） ===
# 获取密钥: https://dashscope.console.aliyun.com/apiKey
DASHSCOPE_API_KEY=your_dashscope_api_key
```

完整配置示例请参考`.env.example`文件（复制到xhs-ai-auto/.env）。

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

## 使用方法(可自行查看xiaohongshu-mcp)

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

## AI提供商对比

| 提供商 | 文本生成模型 | 图像生成模型 | 免费额度 | 特点 |
|--------|-------------|-------------|----------|------|
| **Google** | Gemini-1.5-flash | Imagen-4.0 | 第一层级可用 | 稳定性高，图像质量好 |
| **ModelScope** | Qwen3-235B | Qwen-Image | 500次/天 | 完全免费，深度思考模式，不怎么好用 |
| **DashScope** | 通义千问-Plus | 通义万相/Qwen-Image | 100万tokens起 | 企业级稳定，中文优化 |

### 选择建议

- **开发测试**：使用ModelScope（每天2000次免费）
- **生产环境**：使用DashScope（稳定可靠）
- **国际用户**：使用Google（全球服务）

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
- [ModelScope](https://modelscope.cn) - 魔搭社区AI模型平台
- [DashScope](https://dashscope.aliyun.com) - 阿里云百炼平台

## License

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请提交Issue或联系项目维护者。