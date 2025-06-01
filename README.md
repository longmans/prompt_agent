# Prompt优化器 Agent

基于多Agent协作的智能Prompt优化系统，使用LangGraph实现工作流编排，支持多种大语言模型，并提供A2A（Agent-to-Agent）服务接口。

## ✨ 核心功能

- 🤖 **多Agent协作**: 基于LangGraph的专业化Agent工作流
- 🔄 **7步优化流程**: 完整的prompt工程优化管道
- 🌐 **多模型支持**: 支持Google Gemini和OpenAI GPT模型
- 🚀 **A2A服务**: 标准化的Agent-to-Agent接口
- 📊 **智能评估**: 自动生成评估指标和改进建议
- 🎯 **角色专项**: 针对不同用户角色定制优化策略
- 🔒 **代理支持**: 内置代理配置，支持网络受限环境
- 📝 **智能解析**: 支持JSON和自然语言输入

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
2. **提供示例集** - 基于用户提供的示例生成更多高质量示例
3. **生成初始Prompt** - 根据示例生成能产生期望输出的prompt
4. **生成评估指导** - 创建针对性的prompt评估框架
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

3. **配置API密钥和代理**
```bash
# 复制配置模板
cp config_example.env .env

# 编辑.env文件，添加你的API密钥和代理设置
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # 可选

# 代理配置（可选，默认使用 http://127.0.0.1:7890）
HTTPS_PROXY=http://127.0.0.1:7890
HTTP_PROXY=http://127.0.0.1:7890
```

### 启动服务

```bash
python main.py
```

服务将在 http://localhost:9999 启动

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
      "content": "{\"role\": \"目标用户角色\", \"model_type\": \"模型类型\", \"examples\": [...], \"additional_requirements\": \"额外要求\"}"
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
      "content": "{\"role\": \"software developers\", \"model_type\": \"gemini\", \"examples\": [{\"input\": \"Write a function to calculate fibonacci\", \"output\": \"def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)\"}], \"additional_requirements\": \"Include type hints and documentation\"}"
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
      "content": "{\"role\": \"content creators\", \"model_type\": \"openai\", \"examples\": [{\"input\": \"Write a blog post intro about AI\", \"output\": \"Artificial Intelligence is revolutionizing how we work and interact with technology...\"}], \"additional_requirements\": \"Engaging and accessible tone\"}"
    }
  ]
}
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

# 快速功能测试
python quick_test.py

# 多模型支持测试
python test_multimodel.py
```

### 自动化设置

```bash
python setup_and_run.py
```

### 单元测试

```bash
python test_prompt_optimizer.py
```

## 📊 输出格式

系统将返回结构化的优化结果：

```markdown
✅ **Prompt优化完成**

🎯 **目标用户角色:** software developers
🤖 **使用模型:** GEMINI
📊 **处理示例数量:** 2

📝 **生成的主要Prompt:**
[优化后的prompt内容]

🔍 **评估结果:**
[详细的评估分析]

🚀 **改进方案 (3个):**
**方案1:** [重点改进领域]
[改进后的prompt1]

**方案2:** [重点改进领域]  
[改进后的prompt2]

**方案3:** [重点改进领域]
[改进后的prompt3]

💡 **最终推荐 (根据评估选择的最佳方案):**
[推荐的最佳prompt版本]

---
✨ **使用建议:** 您可以直接使用最终推荐的prompt，或根据具体需求选择其中一个改进方案。
```

## 🏗️ 架构设计

- **多Agent系统**: 专业化的生成器、评估器、改进器
- **LangGraph工作流**: 状态管理和流程编排
- **模型工厂**: 统一的模型创建和管理接口，支持实例缓存
- **A2A集成**: 标准化的Agent服务接口
- **错误处理**: 完善的异常处理和用户指导
- **代理支持**: 内置代理配置，自动处理网络请求
- **日志系统**: 完整的日志记录，便于调试和监控

## 🔧 配置选项

### 环境变量

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `GOOGLE_API_KEY` | 是 | Google Gemini API密钥 | `AIza...` |
| `OPENAI_API_KEY` | 否 | OpenAI API密钥 | `sk-...` |
| `HTTPS_PROXY` | 否 | HTTPS代理地址 | `http://127.0.0.1:7890` |
| `HTTP_PROXY` | 否 | HTTP代理地址 | `http://127.0.0.1:7890` |

### 性能优化

- **模型实例缓存**: 避免重复创建模型实例
- **工作流缓存**: 不同模型类型的工作流实例复用
- **错误恢复**: 单个步骤失败时的优雅降级
- **输入验证**: 提前验证避免无效请求
- **日志记录**: 详细的性能和错误日志

### 模型配置

可以通过修改 `ModelFactory` 类来添加新的模型支持或调整现有模型参数：

- 模型名称
- API密钥
- 温度参数
- 超时设置
- 重试次数
- 代理配置

## 🚨 故障排除

### 常见问题

1. **ImportError: cannot import name 'StateGraph'**
   - 解决: 确保安装了正确版本的langgraph: `pip install langgraph>=0.4.1`

2. **API密钥错误**
   - 解决: 检查.env文件中的API密钥配置

3. **端口占用**
   - 解决: 修改main.py中的端口号或停止占用9999端口的进程

4. **模型不支持错误**
   - 解决: 确保model_type为"gemini"或"openai"

### 日志和调试

- 服务器日志: 查看控制台输出
- 错误信息: 检查API响应中的error字段
- 网络问题: 确认API密钥和网络连接

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

[MIT License](LICENSE)

## 🔗 相关链接

- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [A2A框架](https://github.com/a2a-dev/a2a)
- [Google Gemini API](https://ai.google.dev/)
- [OpenAI API](https://platform.openai.com/)

---

**开发者**: 基于LangGraph的多Agent prompt优化系统
**版本**: 1.1.0 - 多模型支持版
