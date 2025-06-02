# Prompt优化器 Agent

基于多Agent协作的智能Prompt优化系统，使用LangGraph实现工作流编排，支持多种大语言模型，并提供A2A（Agent-to-Agent）服务接口和Web界面。

## ✨ 核心功能

- 🤖 **多Agent协作**: 基于LangGraph的专业化Agent工作流
- 🔄 **7步优化流程**: 完整的prompt工程优化管道
- 🌐 **多模型支持**: 支持Google Gemini和OpenAI GPT模型
- 🚀 **A2A服务**: 标准化的Agent-to-Agent接口
- 🌟 **Web界面**: 基于Gradio的流式交互界面
- 📊 **智能评估**: 自动生成评估指标和改进建议
- 🎯 **角色专项**: 针对不同用户角色定制优化策略
- 🔒 **代理支持**: 内置代理配置，支持网络受限环境
- 📝 **智能解析**: 支持JSON和自然语言输入
- 🛡️ **健壮性**: 完善的错误处理和状态管理
- 🔍 **示例验证**: 字段名一致性检查和格式验证
- 📋 **会话管理**: 智能状态管理和历史记录

## 🔧 支持的模型

| 模型提供商 | 模型名称 | 模型类型标识 | 配置要求 |
|------------|----------|--------------|----------|
| Google | Gemini 2.0 Flash | `gemini` | `GOOGLE_API_KEY` |
| OpenAI | GPT-4o-mini | `openai` | `OPENAI_API_KEY` |

## 🌐 代理配置

系统内置代理支持，方便在网络受限环境中使用：

### 环境变量配置

```bash
# 在 .env 文件中配置代理
HTTPS_PROXY=http://127.0.0.1:7890
HTTP_PROXY=http://127.0.0.1:7890

# 或者在启动时设置
export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
python main.py
```

### 默认代理设置

如果未设置环境变量，系统默认使用：
- HTTPS代理: `http://127.0.0.1:7890`
- HTTP代理: `http://127.0.0.1:7890`

### 常见代理软件端口

| 代理软件 | 默认端口 | 配置示例 |
|----------|----------|----------|
| Clash | 7890 | `http://127.0.0.1:7890` |
| V2Ray | 1081 | `http://127.0.0.1:1081` |
| SSR | 1080 | `http://127.0.0.1:1080` |

## 📋 7步优化流程

1. **生成工程指导** - 为特定角色生成详细的prompt工程指南
2. **分析角色和要求** - 理解用户角色和基本要求
3. **生成初始Prompt** - 根据角色和要求生成基础prompt
4. **创建评估框架** - 创建针对性的prompt评估框架
5. **执行Prompt评估** - 对生成的prompt进行全面评估
6. **生成改进方案** - 提供3个不同的优化版本
7. **选择最佳版本** - 自动推荐或用户选择最终prompt

## 🚀 快速开始

### 环境配置

1. **克隆项目**
```bash
git clone <repository-url>
cd prompt_agent
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置API密钥和服务器**
```bash
# 复制配置模板
cp config_example.env .env

# 编辑.env文件，添加你的API密钥和服务器设置
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # 可选

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=9999
LOG_LEVEL=info

# 代理配置（可选，默认使用 http://127.0.0.1:7890）
HTTPS_PROXY=http://127.0.0.1:7890
HTTP_PROXY=http://127.0.0.1:7890

# Web界面配置
WEB_HOST=0.0.0.0
WEB_PORT=7860
```

### 启动服务

#### A2A服务 (推荐)
```bash
python main.py
```
服务将在 http://localhost:9999 启动

#### Web界面
```bash
python web.py
```
Web界面将在 http://localhost:7860 启动

#### 开发模式
```bash
# 启用热重载和调试日志
export RELOAD=true
export LOG_LEVEL=debug
python main.py
```

## 🖥️ Web界面功能

### 🚀 Prompt优化页面
- **流式处理**: 实时显示优化进度
- **多格式支持**: JSON和文本格式示例输入
- **实时验证**: 输入参数自动验证
- **结果展示**: 格式化的优化结果显示

### 🔧 手动验证页面
- **变量管理**: 自动提取和验证prompt变量
- **实时预览**: 变量替换后的prompt预览
- **错误提示**: 详细的验证错误信息
- **变量提示**: 智能的变量定义建议

### 📖 使用说明页面
- **完整文档**: 详细的使用指南
- **示例展示**: 多种格式的输入示例
- **最佳实践**: Prompt工程最佳实践指导

## 📖 使用方法

### 快速开始示例

最简单的方式是直接发送关键词：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "software developer"
    }
  ]
}
```

系统会自动为软件开发者角色生成基础配置。

### A2A接口调用

发送POST请求到 `http://localhost:9999/` 

**标准请求格式:**
```json
{
  "messages": [
    {
      "role": "user", 
      "content": {
        "role": "目标用户角色",
        "basic_requirements": "基本任务要求",
        "examples": [...],  // 可选
        "additional_requirements": "额外要求",  // 可选
        "model_type": "模型类型"  // 可选，默认openai
      }
    }
  ]
}
```

### 🤖 Gemini模型示例

```json
{
  "messages": [
    {
      "role": "user",
      "content": {
        "role": "software developers",
        "basic_requirements": "编写高质量、可维护的Python代码，包括函数、类和API设计",
        "model_type": "gemini",
        "examples": [
          {
            "input": "{\"function_name\": \"calculate_fibonacci\", \"input_type\": \"int\", \"output_type\": \"int\", \"description\": \"计算斐波那契数列第n个数\"}",
            "output": "def calculate_fibonacci(n: int) -> int:\n    \"\"\"计算斐波那契数列第n个数\n    Args:\n        n: 要计算的位置\n    Returns:\n        int: 斐波那契数\n    \"\"\"\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)"
          }
        ],
        "additional_requirements": "Include type hints and documentation"
      }
    }
  ]
}
```

### 🧠 OpenAI模型示例

```json
{
  "messages": [
    {
      "role": "user", 
      "content": {
        "role": "content creators",
        "basic_requirements": "创作引人入胜、结构清晰的博客文章和营销文案",
        "model_type": "openai",
        "examples": [
          {
            "input": "{\"topic\": \"AI trends\", \"target_audience\": \"tech professionals\", \"tone\": \"professional\", \"word_count\": \"1000\"}",
            "output": "# The Future of AI: 5 Trends That Will Shape 2024\n\nArtificial Intelligence is revolutionizing how we work..."
          }
        ],
        "additional_requirements": "Engaging and accessible tone"
      }
    }
  ]
}
```

### 📝 示例格式说明

#### 字段名一致性要求
每个示例的input必须是一个JSON对象，**所有示例的input字段名必须保持一致**：

✅ **正确示例**（字段名一致）：
```json
[
  {
    "input": "{\"function_name\": \"validate_email\", \"input_type\": \"str\", \"output_type\": \"bool\"}",
    "output": "def validate_email(email: str) -> bool: ..."
  },
  {
    "input": "{\"function_name\": \"calculate_sum\", \"input_type\": \"list\", \"output_type\": \"int\"}",
    "output": "def calculate_sum(numbers: list) -> int: ..."
  }
]
```

❌ **错误示例**（字段名不一致）：
```json
[
  {
    "input": "{\"function_name\": \"validate_email\", \"input_type\": \"str\"}",
    "output": "def validate_email(email: str) -> bool: ..."
  },
  {
    "input": "{\"method_name\": \"calculate_sum\", \"param_type\": \"list\"}",  // 字段名不同！
    "output": "def calculate_sum(numbers: list) -> int: ..."
  }
]
```

#### 支持的输入格式

**JSON格式**（推荐）：
```json
[
  {
    "input": "{\"topic\": \"sustainability\", \"audience\": \"general public\", \"tone\": \"casual\"}",
    "output": "🌱 Small changes, BIG impact! ..."
  }
]
```

**简单文本格式**：
```
Input:
topic=sustainability
audience=general public
tone=casual
Output:
🌱 Small changes, BIG impact! Here are 3 easy tips...

Input:
topic=AI trends
audience=tech professionals
tone=professional
Output:
# The Future of AI: 5 Trends That Will Shape 2024...
```

### 支持的用户角色

- `software developers` - 软件开发者
- `content creators` - 内容创作者  
- `customer support representatives` - 客服代表
- `data scientists` - 数据科学家
- `marketing professionals` - 市场营销专家
- `teachers` - 教师
- 或任何自定义角色

## 🛠️ 本地开发和测试

### 运行演示脚本

```bash
# 完整功能演示
python demo.py

# 测试Web界面组件
python test_web.py

# 测试代理配置和优化
python test_proxy_optimization.py

# A2A客户端测试
python test_client.py
```

### 开发环境配置

```bash
# 开发模式环境变量
export RELOAD=true
export LOG_LEVEL=debug
export VERBOSE_LOGGING=true
export SERVER_PORT=8888
export WEB_PORT=7861

# 启动开发服务器
python main.py
```

## 📊 输出格式

```json
{
  "role": "目标用户角色",
  "basic_requirements": "基本任务要求",
  "model_type": "使用的模型",
  "original_examples": [
    {
      "input": "示例输入",
      "output": "示例输出"
    }
  ],
  "generated_prompt": "生成的初始prompt",
  "evaluations": [
    "评估结果1",
    "评估结果2"
  ],
  "alternative_prompts": [
    "改进方案1",
    "改进方案2",
    "改进方案3"
  ],
  "final_recommendation": "最终推荐的prompt",
  "step": "completed"
}
```

## 🏗️ 系统架构

### 核心组件
- **多Agent系统**: 专业化的生成器、评估器、改进器
- **LangGraph工作流**: 状态管理和流程编排
- **模型工厂**: 统一的模型创建和管理接口，支持实例缓存
- **A2A集成**: 标准化的Agent服务接口
- **Web界面**: 基于Gradio的交互界面，支持流式处理
- **会话状态**: SessionState类管理用户会话和历史记录

### 新增特性
- **错误处理**: 分类错误处理（输入错误、连接错误、运行时错误）
- **代理支持**: 内置代理配置，自动处理网络请求
- **日志系统**: 完整的日志记录，支持文件输出和不同级别
- **输入验证**: 全面的输入验证，包括字段名一致性检查
- **状态管理**: 安全的会话状态管理，避免全局变量
- **配置管理**: 丰富的环境变量配置选项

## 🔧 配置选项

### 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `GOOGLE_API_KEY` | 条件* | - | Google Gemini API密钥 |
| `OPENAI_API_KEY` | 条件* | - | OpenAI API密钥 |
| `SERVER_HOST` | 否 | `0.0.0.0` | 服务器主机地址 |
| `SERVER_PORT` | 否 | `9999` | 服务器端口 |
| `WEB_HOST` | 否 | `0.0.0.0` | Web界面主机地址 |
| `WEB_PORT` | 否 | `7860` | Web界面端口 |
| `LOG_LEVEL` | 否 | `info` | 日志级别 (debug/info/warning/error) |
| `WORKERS` | 否 | `1` | 工作进程数 |
| `RELOAD` | 否 | `false` | 是否启用热重载 |
| `HTTPS_PROXY` | 否 | `http://127.0.0.1:7890` | HTTPS代理地址 |
| `HTTP_PROXY` | 否 | `http://127.0.0.1:7890` | HTTP代理地址 |
| `MODEL_TEMPERATURE` | 否 | `0.7` | 模型温度参数 |
| `REQUEST_TIMEOUT` | 否 | `60` | 请求超时时间(秒) |
| `MAX_RETRIES` | 否 | `3` | 最大重试次数 |

*至少需要配置一个API密钥

### 性能优化

- **模型实例缓存**: 避免重复创建模型实例
- **工作流缓存**: 不同模型类型的工作流实例复用
- **错误恢复**: 单个步骤失败时的优雅降级
- **输入验证**: 提前验证避免无效请求
- **日志记录**: 详细的性能和错误日志
- **会话管理**: 智能状态管理和历史记录

## 🚨 故障排除

### 常见问题

1. **ImportError: cannot import name 'StateGraph'**
   - 解决: 确保安装了正确版本的langgraph: `pip install langgraph>=0.4.1`

2. **API密钥错误**
   - 检查.env文件中的API密钥配置
   - 确保至少配置了一个有效的API密钥
   - 检查密钥格式是否正确

3. **端口占用**
   - 修改环境变量中的端口配置: `SERVER_PORT=8888`
   - 或停止占用端口的进程: `lsof -ti:9999 | xargs kill`

4. **示例字段名不一致错误**
   - 确保所有示例的input字段名完全相同
   - 检查JSON格式是否正确
   - 参考文档中的示例格式

5. **代理连接问题**
   - 检查代理软件是否正常运行
   - 验证代理地址和端口配置
   - 尝试不同的代理端口

6. **Web界面无法访问**
   - 检查防火墙设置
   - 确认Web服务器正常启动
   - 检查端口是否被占用

### 日志和调试

```bash
# 启用详细日志
export LOG_LEVEL=debug
export VERBOSE_LOGGING=true

# 查看日志文件
tail -f prompt_optimizer.log

# 检查服务器状态
curl http://localhost:9999/.well-known/agent.json
```

### 环境检查

系统启动时会自动检查：
- API密钥配置状态
- 代理配置状态  
- 依赖包安装状态
- 端口可用性

## 📚 更多文档

- [系统架构](ARCHITECTURE.md) - 详细的系统架构说明
- [API文档](API.md) - A2A接口规范
- [开发指南](DEVELOPMENT.md) - 开发和贡献指南
- [更新日志](CHANGELOG.md) - 版本更新记录

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

[MIT License](LICENSE) - 详见许可证文件

## 🔗 相关链接

- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [A2A框架](https://github.com/a2a-dev/a2a)
- [Google Gemini API](https://ai.google.dev/)
- [OpenAI API](https://platform.openai.com/)
- [Gradio文档](https://gradio.app/docs/)

---

**开发者**: 基于LangGraph的多Agent prompt优化系统  
**版本**: 1.2.0 - 增强健壮性和Web界面版  
**最后更新**: 2024年12月

## 🎯 版本特性

### v1.2.0 新特性
- ✨ 完整的Web界面支持
- 🛡️ 增强的错误处理和状态管理
- 🔍 示例字段名一致性验证
- 📋 会话状态和历史记录管理
- 🔧 丰富的环境变量配置
- 📊 详细的日志记录和监控
- 🚀 流式处理和实时反馈
