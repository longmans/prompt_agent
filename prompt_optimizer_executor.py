import json
import logging
from typing import Dict, Any, Optional
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
from prompt_optimizer import PromptOptimizerWorkflow, PromptRequest

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptOptimizerAgentExecutor(AgentExecutor):
    """Prompt优化器Agent执行器，集成多Agent工作流到A2A框架"""

    def __init__(self):
        # 不再预先创建workflow，而是在执行时根据模型类型动态创建
        self._workflows = {}  # 缓存不同模型类型的workflow

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """执行prompt优化流程"""
        try:
            # 解析输入消息 - 使用正确的A2A方法
            user_input = context.get_user_input()
            
            if not user_input:
                await self._send_error_message(event_queue, "请提供需要优化的prompt信息")
                return

            # 尝试解析JSON格式的输入
            request_data = self._parse_input(user_input)
            
            if not request_data:
                self._send_usage_help(event_queue)
                return

            # 验证输入数据
            validation_error = self._validate_request_data(request_data)
            if validation_error:
                await self._send_error_message(event_queue, validation_error)
                return

            # 提取模型类型，默认为gemini
            model_type = request_data.get("model_type", "gemini").lower()
            
            # 验证模型类型
            if model_type not in ["gemini", "openai"]:
                await self._send_error_message(
                    event_queue, 
                    f"❌ 不支持的模型类型: {model_type}。支持的类型: gemini, openai"
                )
                return

            # 创建prompt请求
            prompt_request = PromptRequest(
                role=request_data.get("role", "general user"),
                examples=request_data.get("examples", []),
                additional_requirements=request_data.get("additional_requirements", ""),
                model_type=model_type
            )

            # 发送开始处理的消息
            event_queue.enqueue_event(
                new_agent_text_message(f"🚀 开始为 '{prompt_request.role}' 使用 {model_type.upper()} 模型优化prompt...")
            )

            # 获取或创建workflow实例
            workflow = await self._get_workflow(model_type)

            # 执行优化工作流
            logger.info(f"Starting prompt optimization for role: {prompt_request.role}, model: {model_type}")
            result = await workflow.optimize_prompt(prompt_request)

            # 格式化并发送结果
            formatted_result = self._format_result(result)
            event_queue.enqueue_event(new_agent_text_message(formatted_result))
            
            logger.info(f"Prompt optimization completed successfully for role: {prompt_request.role}")

        except ValueError as e:
            await self._send_error_message(event_queue, f"❌ 输入验证错误: {str(e)}")
            logger.warning(f"Input validation error: {str(e)}")
        except RuntimeError as e:
            await self._send_error_message(event_queue, f"❌ 系统运行错误: {str(e)}")
            logger.error(f"Runtime error: {str(e)}")
        except Exception as e:
            await self._send_error_message(event_queue, f"❌ 处理过程中出现未知错误: {str(e)}")
            logger.error(f"Unexpected error during execution: {str(e)}", exc_info=True)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """取消执行"""
        event_queue.enqueue_event(
            new_agent_text_message("❌ Prompt优化任务已取消")
        )
        logger.info("Prompt optimization task cancelled")

    async def _get_workflow(self, model_type: str) -> PromptOptimizerWorkflow:
        """获取或创建workflow实例，使用缓存提高性能"""
        if model_type not in self._workflows:
            try:
                self._workflows[model_type] = PromptOptimizerWorkflow(model_type=model_type)
                logger.info(f"Created new workflow for model type: {model_type}")
            except Exception as e:
                logger.error(f"Failed to create workflow for {model_type}: {str(e)}")
                raise RuntimeError(f"无法创建 {model_type} 工作流: {str(e)}")
        
        return self._workflows[model_type]

    def _parse_input(self, content: str) -> Optional[Dict[str, Any]]:
        """解析用户输入，支持JSON和自然语言"""
        try:
            # 尝试解析JSON格式
            parsed_data = json.loads(content)
            logger.info("Successfully parsed JSON input")
            return parsed_data
        except json.JSONDecodeError:
            logger.info("JSON parsing failed, attempting natural language parsing")
            # 如果不是JSON，尝试解析自然语言
            return self._parse_natural_language(content)

    def _parse_natural_language(self, content: str) -> Optional[Dict[str, Any]]:
        """解析自然语言输入（改进实现）"""
        content = content.strip().lower()
        
        # 简单的自然语言解析逻辑
        if any(keyword in content for keyword in ['developer', 'programming', 'code', 'software']):
            return {
                "role": "software developers",
                "examples": [
                    {"input": "Write a function", "output": "def example_function():"},
                    {"input": "Create a class", "output": "class ExampleClass:"}
                ],
                "model_type": "gemini"
            }
        elif any(keyword in content for keyword in ['writer', 'author', 'content', 'writing']):
            return {
                "role": "content writers",
                "examples": [
                    {"input": "Write an article", "output": "Here's a compelling article..."},
                    {"input": "Create a blog post", "output": "Welcome to our blog..."}
                ],
                "model_type": "gemini"
            }
        else:
            logger.info("Could not parse natural language input")
            return None

    def _validate_request_data(self, request_data: Dict[str, Any]) -> Optional[str]:
        """验证请求数据的完整性和正确性"""
        if not isinstance(request_data, dict):
            return "请求数据必须是JSON对象格式"
        
        # 检查必需字段
        if "role" not in request_data:
            return "缺少必需字段: role"
        
        if "examples" not in request_data:
            return "缺少必需字段: examples"
        
        # 验证角色字段
        role = request_data.get("role", "")
        if not isinstance(role, str) or not role.strip():
            return "role字段必须是非空字符串"
        
        # 验证示例字段
        examples = request_data.get("examples", [])
        if not isinstance(examples, list):
            return "examples字段必须是数组"
        
        if len(examples) == 0:
            return "至少需要提供一个示例"
        
        # 验证每个示例
        for i, example in enumerate(examples):
            if not isinstance(example, dict):
                return f"示例 {i+1} 必须是对象格式"
            
            if "input" not in example or "output" not in example:
                return f"示例 {i+1} 必须包含 'input' 和 'output' 字段"
            
            if not isinstance(example["input"], str) or not isinstance(example["output"], str):
                return f"示例 {i+1} 的 'input' 和 'output' 必须是字符串"
            
            if not example["input"].strip() or not example["output"].strip():
                return f"示例 {i+1} 的 'input' 和 'output' 不能为空"
        
        return None

    async def _send_error_message(self, event_queue: EventQueue, error_message: str) -> None:
        """发送错误消息"""
        event_queue.enqueue_event(new_agent_text_message(error_message))

    def _send_usage_help(self, event_queue: EventQueue):
        """发送使用帮助信息"""
        help_message = """
📋 **Prompt优化器使用指南**

请提供JSON格式的输入，包含以下字段：

```json
{
    "role": "目标用户角色，如 'software developers', 'book authors', 'customer support reps'",
    "examples": [
        {
            "input": "示例输入1",
            "output": "期望输出1"
        },
        {
            "input": "示例输入2", 
            "output": "期望输出2"
        }
    ],
    "model_type": "模型类型，支持 'gemini'（默认）或 'openai'",
    "additional_requirements": "额外要求（可选）"
}
```

**🤖 支持的模型类型:**
- `gemini`: Google Gemini 2.0 Flash (默认)
- `openai`: OpenAI GPT-4o-mini

**🌐 代理配置:**
系统已配置代理支持，默认使用 `http://127.0.0.1:7890`
如需修改，请在环境变量中设置 `HTTPS_PROXY` 和 `HTTP_PROXY`

**💡 快速开始示例:**
直接发送 "software developer" 或 "content writer" 等关键词，系统会自动生成基础配置

**示例：使用OpenAI模型优化软件开发prompt**
```json
{
    "role": "software developers",
    "model_type": "openai",
    "examples": [
        {
            "input": "Write a function to calculate fibonacci numbers",
            "output": "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)"
        },
        {
            "input": "Create a REST API endpoint",
            "output": "@app.route('/api/users', methods=['GET'])\\ndef get_users():\\n    return jsonify(users)"
        }
    ],
    "additional_requirements": "Focus on clean, maintainable code"
}
```

**示例：使用Gemini模型优化客服对话prompt**
```json
{
    "role": "customer support representatives",
    "model_type": "gemini",
    "examples": [
        {
            "input": "Customer complains about delayed delivery",
            "output": "I sincerely apologize for the delay. Let me check your order status immediately."
        }
    ]
}
```
        """
        event_queue.enqueue_event(new_agent_text_message(help_message))

    def _format_result(self, result: Dict[str, Any]) -> str:
        """格式化优化结果，改进显示效果"""
        model_type = result.get('model_type', 'unknown').upper()
        role = result.get('role', 'Unknown')
        generated_prompt = result.get('generated_prompt', 'N/A')
        evaluations = result.get('evaluations', [])
        alternative_prompts = result.get('alternative_prompts', [])
        final_recommendation = result.get('final_recommendation', generated_prompt)
        original_examples_count = len(result.get('original_examples', []))
        
        formatted = f"""
✅ **Prompt优化完成**

🎯 **目标用户角色:** {role}
🤖 **使用模型:** {model_type}
📊 **处理示例数量:** {original_examples_count}

📝 **生成的主要Prompt:**
```
{generated_prompt}
```"""

        # 添加评估结果
        if evaluations:
            formatted += f"""

🔍 **评估结果:**
{evaluations[0][:500]}{'...' if len(evaluations[0]) > 500 else ''}"""

        # 添加改进方案
        if alternative_prompts:
            formatted += f"""

🚀 **改进方案 ({len(alternative_prompts)} 个):**"""
            
            for i, alt_prompt in enumerate(alternative_prompts[:3], 1):  # 限制显示前3个
                formatted += f"""

**方案 {i}:**
```
{alt_prompt[:300]}{'...' if len(alt_prompt) > 300 else ''}
```"""

        # 添加最终推荐
        formatted += f"""

💡 **最终推荐 (根据评估选择的最佳方案):**
```
{final_recommendation}
```

---
✨ **使用建议:** 您可以直接使用最终推荐的prompt，或根据具体需求选择其中一个改进方案。
"""
        
        return formatted 