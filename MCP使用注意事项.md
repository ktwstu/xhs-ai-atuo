# MCP (xiaohongshu-mcp) 使用注意事项

## 初次使用必读

本文档记录了在Windows环境下使用xiaohongshu-mcp服务的关键注意事项和常见问题解决方案。

## 一、环境准备

### 1.1 服务端口配置
- **MCP服务默认端口**：18060
- **API端点**：`http://localhost:18060/mcp`
- 确保端口未被占用

### 1.2 目录结构
```
xhs-auto/
├── xhs-ai-auto/          # 主程序
│   ├── config/
│   │   └── settings.py   # 配置文件（端口设置）
│   └── services/
│       └── publish_service.py  # 发布服务（MCP协议调用）
├── xiaohongshu-mcp/      # MCP服务
│   ├── xiaohongshu-login-windows-amd64.exe    # 登录工具
│   └── xiaohongshu-mcp-windows-amd64.exe      # MCP服务
└── data/                 # 生成的内容存储
```

## 二、Windows Defender 问题处理

### 2.1 问题描述
Windows Defender可能会将`leakless.exe`（无头浏览器组件）误报为病毒，导致以下错误：
```
Operation did not complete successfully because the file contains a virus or potentially unwanted software
```

### 2.2 解决方案

#### 方案一：添加排除项（推荐）
1. 打开Windows设置（Win + I）
2. 进入"隐私和安全性" → "Windows安全中心" → "病毒和威胁防护"
3. 点击"管理设置"
4. 找到"排除项"，点击"添加或删除排除项"
5. 添加以下文件夹排除：
   - `E:\DevSouce\ccrcode\xhs-auto`（整个项目文件夹）
   - `C:\Users\Admin\AppData\Local\Temp`（临时文件夹）

**注意**：`C:\Users\Admin\AppData\Local\rod`路径在Windows上不存在，无需添加。

#### 方案二：使用非无头模式
如果排除项设置后仍有问题，可以使用非无头模式运行（会显示浏览器窗口）：
```bash
./xiaohongshu-mcp-windows-amd64.exe -headless=false
```

## 三、使用流程

### 3.1 首次登录（必须）
```bash
# 在xiaohongshu-mcp目录下运行
./xiaohongshu-login-windows-amd64.exe
```
- 会弹出浏览器窗口
- 手动登录小红书账号
- 登录成功后cookies会自动保存

### 3.2 启动MCP服务
```bash
# 推荐：非无头模式（避免权限问题）-也可以选择使用无头
./xiaohongshu-mcp-windows-amd64.exe -headless=false

# 或使用源码运行
go run . -headless=false
```

### 3.3 运行主程序
在另一个终端窗口：
```bash
# 激活虚拟环境并运行
venv/Scripts/python.exe xhs-ai-auto/main.py
```

## 四、MCP协议要点

### 4.1 请求格式
MCP使用JSON-RPC 2.0协议，请求格式示例：
```json
{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "publish_content",
        "arguments": {
            "title": "标题（最多20字）",
            "content": "内容",
            "images": ["图片路径1", "图片路径2"]
        }
    },
    "id": 1
}
```

### 4.2 响应处理
- 成功响应包含`result`字段
- 错误响应包含`error`字段
- 即使发布成功，result可能是空dict `{}`，需要灵活判断

## 五、常见问题

### 5.1 端口连接错误
**问题**：`Max retries exceeded with url: /api/v1/publish`

**解决**：
1. 检查`settings.py`中的端口配置：
   ```python
   XHS_MCP_BASE_URL = os.getenv("XHS_MCP_BASE_URL", "http://localhost:18060")
   ```
2. 确保MCP服务正在运行

### 5.2 发布显示失败但实际成功
**问题**：提示"Failed to publish: Unknown error"但内容已发布

**原因**：MCP响应格式判断过于严格

**解决**：已在`publish_service.py`中改进响应判断逻辑

### 5.3 Cookie过期
**问题**：`failed to load cookies`

**解决**：重新运行登录工具进行登录

## 六、注意事项

1. **账号限制**：小红书同一账号不能在多个网页端同时登录，登录MCP后不要在其他浏览器登录
2. **标题限制**：小红书标题最多20个字符，超出会被截断
3. **发帖限制**：每天发帖量上限约50篇
4. **首次运行**：会自动下载约150MB的浏览器组件，需要良好的网络连接
5. **图片路径**：必须使用绝对路径

## 七、调试技巧

### 7.1 查看详细日志
在`publish_service.py`中已添加DEBUG输出，可以看到：
- 发送的请求内容
- MCP返回的完整响应
- 错误详情

### 7.2 测试MCP连接
使用MCP Inspector测试：
```bash
npx @modelcontextprotocol/inspector
```
然后连接到：`http://localhost:18060/mcp`

### 7.3 清理缓存
如果遇到浏览器组件问题：
```bash
rmdir /s /q C:\Users\Admin\AppData\Local\Temp\leakless*
```

## 八、完整工作流程确认

1. ✅ 文本生成（Google Gemini API）
2. ✅ 图像生成（Google Imagen API）
3. ✅ 内容发布（xiaohongshu-mcp）

所有组件均已调试完成并可正常工作。

---

*文档创建日期：2025年9月19日*
*适用版本：xiaohongshu-mcp v1.0+*