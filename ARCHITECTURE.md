# Prompt优化器架构设计

## 🏗️ 整体架构

本项目实现了一个基于LangGraph多Agent协作的Prompt优化系统，遵循您描述的工作流程，并通过A2A框架对外提供服务。

## 🤖 多Agent架构

### 1. PromptGeneratorAgent (Prompt生成器)
**职责：**
- 生成针对特定用户角色的prompt工程指导
- 基于few-shot示例逆向工程生成prompt
- 提供额外的高质量示例

**关键方法：**
```python
async def generate_prompt_engineering_guide(state) -> Dict
async def generate_prompt_from_examples(state) -> Dict
```

### 2. PromptEvaluatorAgent (Prompt评估器)
**职责：**
- 创建针对特定角色的评估框架
- 对生成的prompt进行多维度评估
- 识别prompt的优缺点

**关键方法：**
```python
async def generate_evaluation_guide(state) -> Dict
async def evaluate_prompt(state) -> Dict
```

### 3. PromptImproverAgent (Prompt改进器)
**职责：**
- 基于评估结果生成改进版本
- 提供3个不同角度的优化方案
- 每个方案聚焦特定的改进领域

**关键方法：**
```python
async def generate_improved_prompts(state) -> Dict
```

## 🔄 LangGraph工作流

### 工作流图
```
开始 → 生成工程指导 → 生成Prompt → 生成评估指导 → 评估Prompt → 生成改进方案 → 完成
```

### 状态管理
```python
class PromptOptimizerState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    role: str
    examples: List[Dict[str, str]]
    current_prompt: str
    evaluations: List[str]
    alternative_prompts: List[str]
    final_prompt: str
    step: str
```

### 节点定义
1. **generate_guide**: 生成工程指导
2. **generate_prompt**: 基于示例生成prompt
3. **generate_eval_guide**: 生成评估指导
4. **evaluate_prompt**: 评估prompt质量
5. **improve_prompts**: 生成改进方案
6. **finalize**: 选择最佳方案

## 🔌 A2A集成架构

### PromptOptimizerAgentExecutor
实现`AgentExecutor`接口，将LangGraph工作流集成到A2A框架：

```python
class PromptOptimizerAgentExecutor(AgentExecutor):
    async def execute(context, event_queue) -> None
    async def cancel(context, event_queue) -> None
```

### 输入处理
- 支持JSON格式的结构化输入
- 包含错误处理和用户指导
- 提供详细的使用帮助

### 输出格式化
- 结构化的markdown输出
- 包含所有优化步骤的结果
- 用户友好的展示格式

## 📊 数据流

### 输入数据结构
```json
{
    "role": "目标用户角色",
    "examples": [
        {"input": "示例输入", "output": "期望输出"}
    ],
    "additional_requirements": "额外要求"
}
```

### 处理流程
1. **输入验证** → 检查JSON格式和必需字段
2. **状态初始化** → 创建PromptOptimizerState
3. **工作流执行** → 按顺序执行所有Agent节点
4. **结果聚合** → 收集所有Agent的输出
5. **格式化输出** → 生成用户友好的结果

### 输出数据结构
```python
{
    "role": str,
    "original_examples": List[Dict],
    "generated_prompt": str,
    "evaluations": List[str],
    "alternative_prompts": List[str],
    "final_recommendation": str,
    "step": str
}
```

## 🎯 设计原则

### 1. 模块化设计
- 每个Agent专注单一职责
- 清晰的接口定义
- 易于扩展和维护

### 2. 状态管理
- 使用TypedDict确保类型安全
- 状态在Agent间透明传递
- 支持中间结果的保存和恢复

### 3. 错误处理
- 全流程错误捕获
- 用户友好的错误消息
- 优雅的降级处理

### 4. 可扩展性
- 支持不同的LLM模型
- 可添加新的Agent角色
- 灵活的工作流配置

## 🔧 技术实现细节

### LLM集成
- 默认使用Google Generative AI
- 支持多种模型提供商
- 统一的模型接口

### 消息处理
- 基于LangChain的消息系统
- 支持流式输出
- 异步处理优化性能

### 配置管理
- 环境变量配置
- 支持多环境部署
- 安全的API密钥管理

## 📁 文件结构

```
prompt_agent/
├── main.py                     # 主服务入口
├── prompt_optimizer.py         # 多Agent工作流实现
├── prompt_optimizer_executor.py # A2A集成层
├── setup_and_run.py           # 快速启动脚本
├── demo.py                     # 演示脚本
├── test_prompt_optimizer.py    # 测试客户端
├── config_example.env          # 配置示例
├── requirements.txt            # 依赖管理
├── README.md                   # 使用说明
└── ARCHITECTURE.md             # 架构文档
```

## 🚀 部署和扩展

### 水平扩展
- 每个Agent可独立扩展
- 支持分布式部署
- 状态持久化支持

### 性能优化
- 异步处理提升吞吐量
- 缓存机制减少重复计算
- 并行执行Compatible的操作

### 监控和观测
- LangSmith集成支持
- 详细的执行日志
- 性能指标收集

## 🔄 工作流优化思路

您描述的优化流程完美地映射到了我们的多Agent架构：

1. **"Generate a detailed prompt engineering guide"** → `PromptGeneratorAgent.generate_prompt_engineering_guide()`
2. **"Paste in 5 examples"** → 通过输入参数提供
3. **"Generate a prompt that could have generated the examples' outputs"** → `PromptGeneratorAgent.generate_prompt_from_examples()`
4. **"Generate a detailed prompt evaluation guide"** → `PromptEvaluatorAgent.generate_evaluation_guide()`
5. **"Evaluate the prompt"** → `PromptEvaluatorAgent.evaluate_prompt()`
6. **"Generate 3 improved alternative prompts"** → `PromptImproverAgent.generate_improved_prompts()`
7. **"Pick the best one, and edit as necessary"** → `finalize_node()` + 用户选择

这种设计充分利用了"LLM's own weights influence how the prompt is generated and evaluated"的优势，每个Agent都使用同一模型家族，确保一致性和最佳效果。 