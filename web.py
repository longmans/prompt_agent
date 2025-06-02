#!/usr/bin/env python3
"""
基于Gradio的Prompt优化器Web界面
支持流式输出、手动验证和变量编辑
"""

import gradio as gr
import asyncio
import json
import re
import os
import logging
from typing import Dict, List, Any, Iterator, Tuple, Optional
from datetime import datetime
from prompt_optimizer import PromptOptimizerWorkflow, PromptRequest, ModelFactory
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class SessionState:
    """会话状态管理类，避免使用全局变量"""
    
    def __init__(self):
        self.current_result: Dict[str, Any] = {}
        self.last_update: Optional[datetime] = None
        self.optimization_history: List[Dict[str, Any]] = []
    
    def update_result(self, result: Dict[str, Any]) -> None:
        """更新当前结果"""
        self.current_result = result
        self.last_update = datetime.now()
        logger.info(f"结果已更新: {result.get('role', 'Unknown')}")
    
    def get_current_prompt(self) -> str:
        """获取当前生成的prompt"""
        return self.current_result.get('final_recommendation', 
                                     self.current_result.get('generated_prompt', ''))
    
    def add_to_history(self, result: Dict[str, Any]) -> None:
        """添加到优化历史"""
        if result and result.get('step') == 'completed':
            self.optimization_history.append({
                **result,
                'timestamp': datetime.now().isoformat()
            })
            logger.info(f"添加到历史记录，当前历史数量: {len(self.optimization_history)}")

# 创建会话状态实例
session_state = SessionState()

class StreamingOptimizer:
    """流式处理Prompt优化器"""
    
    def __init__(self):
        self.workflow: Optional[PromptOptimizerWorkflow] = None
        self.current_step: str = ""
        
    async def optimize_with_streaming(
        self,
        role: str,
        basic_requirements: str,
        examples: List[Dict[str, str]],
        additional_requirements: str,
        model_type: str
    ) -> Iterator[Tuple[str, str, str]]:
        """执行优化并流式返回结果"""
        logger.info(f"开始优化流程: role={role}, model={model_type}")
        
        try:
            # 输入预处理和验证
            role = role.strip()
            basic_requirements = basic_requirements.strip()
            additional_requirements = additional_requirements.strip()
            model_type = model_type.lower()
            
            if not role:
                raise ValueError("角色不能为空")
            if not basic_requirements:
                raise ValueError("基本要求不能为空")
            
            # 创建请求
            request = PromptRequest(
                role=role,
                basic_requirements=basic_requirements,
                examples=examples,
                additional_requirements=additional_requirements,
                model_type=model_type
            )
            
            # 初始化工作流
            yield "🚀 开始", f"正在初始化 {model_type.upper()} 模型...", ""
            logger.info(f"初始化工作流，模型类型: {model_type}")
            
            try:
                self.workflow = PromptOptimizerWorkflow()
            except Exception as e:
                logger.error(f"工作流初始化失败: {str(e)}")
                raise ConnectionError(f"无法初始化{model_type}模型，请检查API密钥配置")
            
            yield "📋 验证", "正在验证输入参数...", ""
            
            # 创建初始状态
            from prompt_optimizer import PromptOptimizerState
            initial_state = PromptOptimizerState(
                messages=[],
                role=request.role,
                basic_requirements=request.basic_requirements,
                examples=request.examples or [],
                current_prompt="",
                evaluations=[],
                alternative_prompts=[],
                final_prompt="",
                step="started",
                model_type=request.model_type
            )
            
            # 逐步执行工作流
            yield "📖 生成指导", "正在生成prompt工程指导...", ""
            try:
                guide_result = await self.workflow._generate_guide_node(initial_state)
                initial_state.update(guide_result)
                logger.debug("prompt工程指导生成完成")
            except Exception as e:
                logger.warning(f"生成指导失败，使用默认配置: {str(e)}")
            
            yield "✏️ 生成Prompt", "正在根据角色和要求生成初始prompt...", ""
            try:
                prompt_result = await self.workflow._generate_prompt_node(initial_state)
                initial_state.update(prompt_result)
                generated_prompt = initial_state.get('current_prompt', '')
                logger.debug(f"初始prompt生成完成，长度: {len(generated_prompt)}")
            except Exception as e:
                logger.error(f"生成prompt失败: {str(e)}")
                raise RuntimeError("生成prompt失败，请重试")
            
            yield "📊 评估准备", "正在准备评估框架...", ""
            try:
                eval_guide_result = await self.workflow._generate_eval_guide_node(initial_state)
                initial_state.update(eval_guide_result)
            except Exception as e:
                logger.warning(f"评估框架准备失败: {str(e)}")
            
            yield "🔍 执行评估", "正在评估prompt质量...", ""
            try:
                evaluation_result = await self.workflow._evaluate_prompt_node(initial_state)
                initial_state.update(evaluation_result)
                logger.debug("prompt评估完成")
            except Exception as e:
                logger.warning(f"prompt评估失败: {str(e)}")
            
            yield "🚀 生成改进", "正在生成改进方案...", ""
            try:
                improvement_result = await self.workflow._improve_prompts_node(initial_state)
                initial_state.update(improvement_result)
                logger.debug(f"生成了 {len(initial_state.get('alternative_prompts', []))} 个改进方案")
            except Exception as e:
                logger.warning(f"生成改进方案失败: {str(e)}")
            
            yield "🎯 最终确定", "正在选择最佳prompt...", ""
            try:
                final_result = await self.workflow._finalize_node(initial_state)
                initial_state.update(final_result)
            except Exception as e:
                logger.error(f"最终确定失败: {str(e)}")
                raise RuntimeError("最终确定失败，请重试")
            
            # 整理最终结果
            result = {
                "role": initial_state["role"],
                "basic_requirements": initial_state["basic_requirements"],
                "model_type": initial_state["model_type"],
                "original_examples": initial_state["examples"],
                "generated_prompt": initial_state.get("current_prompt", ""),
                "evaluations": initial_state.get("evaluations", []),
                "alternative_prompts": initial_state.get("alternative_prompts", []),
                "final_recommendation": initial_state.get("final_prompt", ""),
                "step": initial_state.get("step", "completed")
            }
            
            # 更新会话状态
            session_state.update_result(result)
            session_state.add_to_history(result)
            
            # 格式化最终输出
            final_output = self._format_final_result(result)
            
            yield "✅ 完成", "Prompt优化已完成！", final_output
            logger.info("优化流程成功完成")
            
        except ValueError as e:
            error_msg = f"输入验证错误: {str(e)}"
            logger.warning(error_msg)
            yield "❌ 输入错误", error_msg, ""
        except ConnectionError as e:
            error_msg = f"连接错误: {str(e)}"
            logger.error(error_msg)
            yield "❌ 连接错误", error_msg, ""
        except RuntimeError as e:
            error_msg = f"运行时错误: {str(e)}"
            logger.error(error_msg)
            yield "❌ 运行错误", error_msg, ""
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            yield "❌ 系统错误", error_msg, ""
    
    def _parse_examples(self, examples_text: str) -> List[Dict[str, str]]:
        """解析示例文本，增强健壮性"""
        if not examples_text or not examples_text.strip():
            logger.debug("未提供示例文本")
            return []
        
        # 规范化输入
        examples_text = examples_text.replace('\r\n', '\n').strip()
        
        try:
            if examples_text.startswith('['):
                # JSON数组格式
                examples = json.loads(examples_text)
                if not isinstance(examples, list):
                    raise ValueError("示例必须是数组格式")
                
                # 验证和规范化每个示例
                normalized_examples = []
                for i, example in enumerate(examples):
                    if not isinstance(example, dict):
                        raise ValueError(f"示例 {i+1} 必须是对象格式")
                    if 'input' not in example or 'output' not in example:
                        raise ValueError(f"示例 {i+1} 必须包含 'input' 和 'output' 字段")
                    
                    # 确保input字段是JSON字符串
                    if isinstance(example['input'], dict):
                        example['input'] = json.dumps(example['input'], ensure_ascii=False)
                    elif not isinstance(example['input'], str):
                        example['input'] = str(example['input'])
                    
                    # 确保output是字符串
                    if not isinstance(example['output'], str):
                        example['output'] = str(example['output'])
                    
                    normalized_examples.append(example)
                
                logger.info(f"成功解析JSON格式示例，数量: {len(normalized_examples)}")
                return normalized_examples
            else:
                # 简单文本格式，转换为JSON
                examples = []
                current_input = {}
                current_output = ""
                mode = None
                
                # 分割成行并移除空行
                lines = [line.strip() for line in examples_text.split('\n') if line.strip()]
                
                for line in lines:
                    line_lower = line.lower()
                    if line_lower.startswith('input:'):
                        # 保存上一个示例
                        if current_input and current_output:
                            examples.append({
                                "input": json.dumps(current_input, ensure_ascii=False), 
                                "output": current_output.strip()
                            })
                        current_input = {}
                        current_output = ""
                        mode = "input"
                    elif line_lower.startswith('output:'):
                        current_output = line[7:].strip()
                        mode = "output"
                    elif line and mode == "input":
                        # 尝试解析key=value格式
                        if '=' in line:
                            key, value = line.split('=', 1)
                            current_input[key.strip()] = value.strip()
                        else:
                            # 如果不是key=value格式，作为纯文本处理
                            current_input['text'] = current_input.get('text', '') + ' ' + line
                    elif line and mode == "output":
                        current_output += "\n" + line
                
                # 添加最后一组示例
                if current_input and current_output:
                    examples.append({
                        "input": json.dumps(current_input, ensure_ascii=False), 
                        "output": current_output.strip()
                    })
                
                if not examples:
                    logger.warning("未能从文本中解析出有效示例")
                    return []
                
                logger.info(f"成功解析文本格式示例，数量: {len(examples)}")
                return examples
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {str(e)}")
            raise ValueError(f"示例格式错误，请检查JSON语法: {str(e)}")
        except Exception as e:
            logger.error(f"解析示例时出错: {str(e)}")
            raise ValueError(f"解析示例失败: {str(e)}")
    
    def _format_final_result(self, result: Dict) -> str:
        """格式化最终结果"""
        try:
            output = f"""
# 🎉 Prompt优化结果

## 💡 最终推荐的Prompt
```
{result.get('final_recommendation', 'N/A')}
```

## 📊 基本信息
- **目标角色**: {result.get('role', 'N/A')}
- **基本要求**: {result.get('basic_requirements', 'N/A')}
- **使用模型**: {result.get('model_type', 'unknown').upper()}
- **示例数量**: {len(result.get('original_examples', []))}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📝 生成的主要Prompt
```
{result.get('generated_prompt', 'N/A')}
```

## 🔍 评估结果
{result.get('evaluations', ['N/A'])[0][:500] + ('...' if len(result.get('evaluations', [''])[0]) > 500 else '') if result.get('evaluations') else 'N/A'}

## 🚀 改进方案 ({len(result.get('alternative_prompts', []))}) 个)
"""
            
            for i, alt_prompt in enumerate(result.get('alternative_prompts', [])[:3], 1):
                output += f"""
### 方案 {i}
```
{alt_prompt[:200]}{'...' if len(alt_prompt) > 200 else ''}
```
"""
            
            return output
        except Exception as e:
            logger.error(f"格式化结果时出错: {str(e)}")
            return f"格式化结果时出现错误: {str(e)}"

# 全局优化器实例
optimizer = StreamingOptimizer()

def validate_inputs(role: str, basic_requirements: str, examples: str, model_type: str) -> str:
    """验证输入参数，增强健壮性"""
    logger.debug(f"验证输入: role={bool(role.strip())}, basic_requirements={bool(basic_requirements.strip())}, examples={bool(examples.strip())}, model={model_type}")
    
    # 验证必需字段
    if not role or not role.strip():
        return "❌ 请填写目标角色"
    
    if not basic_requirements or not basic_requirements.strip():
        return "❌ 请填写基本要求"
    
    # 验证模型类型
    if model_type.lower() not in ["gemini", "openai"]:
        return f"❌ 不支持的模型类型: {model_type}。支持的类型: gemini, openai"
    
    # 如果提供了示例，验证格式
    if examples and examples.strip():
        try:
            # 尝试使用 StreamingOptimizer 的解析方法
            optimizer_temp = StreamingOptimizer()
            parsed_examples = optimizer_temp._parse_examples(examples)
            
            if parsed_examples:
                logger.info(f"示例验证成功，数量: {len(parsed_examples)}")
                
                # 验证字段名一致性（和 prompt_optimizer.py 保持一致）
                first_example_fields = None
                for i, example in enumerate(parsed_examples, 1):
                    try:
                        input_data = json.loads(example['input']) if isinstance(example['input'], str) else example['input']
                        if not isinstance(input_data, dict):
                            return f"❌ 示例 {i} 的 'input' 必须是有效的JSON对象"
                        
                        # 获取当前示例的字段名集合
                        current_fields = set(input_data.keys())
                        
                        # 如果是第一个示例，保存其字段名
                        if first_example_fields is None:
                            first_example_fields = current_fields
                        # 否则比较字段名是否一致
                        elif current_fields != first_example_fields:
                            # 找出不一致的字段
                            missing_fields = first_example_fields - current_fields
                            extra_fields = current_fields - first_example_fields
                            error_msg = f"❌ 示例 {i} 的字段名与第一个示例不一致。"
                            if missing_fields:
                                error_msg += f"\n缺少字段: {', '.join(missing_fields)}"
                            if extra_fields:
                                error_msg += f"\n多余字段: {', '.join(extra_fields)}"
                            return error_msg
                    except json.JSONDecodeError:
                        return f"❌ 示例 {i} 的 'input' 必须是有效的JSON格式"
                        
        except ValueError as e:
            return f"❌ 示例格式错误: {str(e)}"
        except Exception as e:
            logger.error(f"示例验证时出错: {str(e)}")
            return f"❌ 示例验证失败: {str(e)}"
    
    # 验证API密钥
    try:
        if model_type.lower() == "gemini":
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key or api_key == 'your_google_api_key_here':
                return "❌ 请先配置GOOGLE_API_KEY环境变量"
        elif model_type.lower() == "openai":
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key or api_key == 'your_openai_api_key_here':
                return "❌ 请先配置OPENAI_API_KEY环境变量"
    except Exception as e:
        logger.error(f"API密钥验证时出错: {str(e)}")
        return f"❌ API密钥验证失败: {str(e)}"
    
    logger.info("输入验证通过")
    return "✅ 输入验证通过"

async def run_optimization(
    role: str,
    basic_requirements: str,
    examples: str,
    additional_requirements: str,
    model_type: str,
    progress=gr.Progress()
):
    """运行优化并更新进度，增强错误处理"""
    
    # 验证输入
    validation_result = validate_inputs(role, basic_requirements, examples, model_type)
    if validation_result.startswith("❌"):
        logger.warning(f"输入验证失败: {validation_result}")
        yield validation_result, "", gr.update(visible=False), gr.update(visible=False)
        return
    
    status_output = ""
    final_output = ""
    
    progress(0, desc="开始初始化...")
    logger.info(f"开始Prompt优化流程: role={role}, model={model_type}")
    
    try:
        # 解析示例（如果有）
        examples_list = []
        if examples.strip():
            try:
                examples_list = optimizer._parse_examples(examples)
                logger.info(f"成功解析示例，数量: {len(examples_list)}")
            except Exception as e:
                logger.error(f"解析示例失败: {str(e)}")
                yield f"❌ 解析示例失败: {str(e)}", "", gr.update(visible=False), gr.update(visible=False)
                return
        
        # 执行流式优化
        async for step, status, output in optimizer.optimize_with_streaming(
            role=role,
            basic_requirements=basic_requirements,
            examples=examples_list,
            additional_requirements=additional_requirements,
            model_type=model_type
        ):
            # 更新状态输出
            timestamp = datetime.now().strftime('%H:%M:%S')
            status_output += f"[{timestamp}] {step}: {status}\n"
            
            if output:
                final_output = output
                logger.info("优化结果已生成")
            
            # 更新进度条
            progress_value = 0.1
            if "验证" in step:
                progress_value = 0.2
            elif "生成指导" in step:
                progress_value = 0.3
            elif "生成Prompt" in step:
                progress_value = 0.5
            elif "评估准备" in step:
                progress_value = 0.6
            elif "执行评估" in step:
                progress_value = 0.7
            elif "生成改进" in step:
                progress_value = 0.8
            elif "最终确定" in step:
                progress_value = 0.9
            elif "完成" in step:
                progress_value = 1.0
                
            progress(progress_value, desc=status)
            
            # 返回更新的UI状态
            show_results = bool(final_output)
            yield status_output, final_output, gr.update(visible=show_results), gr.update(visible=show_results)
        
        logger.info("优化流程完成")
        
    except Exception as e:
        error_msg = f"优化过程中出现未知错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        yield error_msg, "", gr.update(visible=False), gr.update(visible=False)

def get_current_prompt() -> str:
    """获取当前生成的prompt，使用会话状态"""
    try:
        return session_state.get_current_prompt()
    except Exception as e:
        logger.error(f"获取当前prompt失败: {str(e)}")
        return ""

def extract_variables(prompt: str) -> List[str]:
    """提取prompt中的变量（如{name}, {topic}等），增强健壮性"""
    try:
        if not prompt or not isinstance(prompt, str):
            return []
        variables = re.findall(r'\{([^}]+)\}', prompt)
        unique_variables = list(set(variables))
        logger.debug(f"提取到变量: {unique_variables}")
        return unique_variables
    except Exception as e:
        logger.error(f"提取变量时出错: {str(e)}")
        return []

def validate_prompt(prompt: str, variables: str) -> str:
    """验证prompt并替换变量，增强错误处理"""
    try:
        if not prompt or not isinstance(prompt, str):
            return "❌ prompt不能为空"
            
        # 解析变量
        if variables and variables.strip():
            var_dict = {}
            try:
                for line in variables.strip().split('\n'):
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value:  # 确保键和值都不为空
                            var_dict[key] = value
                        else:
                            return f"❌ 变量定义格式错误: '{line}' (键或值不能为空)"
                    elif line:  # 忽略空行
                        return f"❌ 变量定义格式错误: '{line}' (应使用 key=value 格式)"
            except Exception as e:
                return f"❌ 解析变量定义时出错: {str(e)}"
            
            # 替换变量
            test_prompt = prompt
            for key, value in var_dict.items():
                test_prompt = test_prompt.replace(f'{{{key}}}', value)
            
            # 检查是否还有未替换的变量
            remaining_vars = extract_variables(test_prompt)
            if remaining_vars:
                return f"❌ 以下变量未定义: {', '.join(remaining_vars)}\n\n替换后的Prompt:\n{test_prompt}"
            else:
                return f"✅ 验证通过！所有变量已正确替换。\n\n验证后的Prompt:\n{test_prompt}"
        else:
            # 检查是否有变量但未定义
            vars_in_prompt = extract_variables(prompt)
            if vars_in_prompt:
                return f"⚠️ 发现未定义的变量: {', '.join(vars_in_prompt)}\n请在变量定义区域定义这些变量。\n\n原始Prompt:\n{prompt}"
            else:
                return f"✅ 验证通过！没有需要替换的变量。\n\nPrompt:\n{prompt}"
    
    except Exception as e:
        logger.error(f"验证prompt时出错: {str(e)}")
        return f"❌ 验证过程中出现错误: {str(e)}"

def update_variables_hint(prompt: str) -> str:
    """更新变量提示，增强用户体验"""
    try:
        if not prompt:
            return "请先输入prompt内容"
            
        variables = extract_variables(prompt)
        if variables:
            hint = "发现以下变量，请定义其值：\n"
            for var in sorted(variables):  # 排序以保持一致性
                hint += f"{var}=在此输入{var}的值\n"
            logger.debug(f"更新变量提示，发现 {len(variables)} 个变量")
            return hint
        else:
            return "未发现变量，如需添加变量请使用{变量名}格式"
    except Exception as e:
        logger.error(f"更新变量提示时出错: {str(e)}")
        return "更新变量提示时出现错误"

# 创建Gradio界面
with gr.Blocks(title="Prompt优化器 - Web界面", theme=gr.themes.Soft()) as app:
    gr.HTML("""
    <div style="text-align: center; padding: 20px;">
        <h1>🤖 Prompt优化器</h1>
        <p>基于多Agent协作的智能Prompt优化系统</p>
        <p>支持流式输出、手动验证和变量编辑</p>
    </div>
    """)
    
    with gr.Tabs() as tabs:
        with gr.Tab("🚀 Prompt优化", id=0):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("<h3>📝 输入配置</h3>")
                    
                    role_input = gr.Textbox(
                        label="🎯 目标角色",
                        placeholder="例如: 一个专业的Python软件工程师，专注于后端开发和API设计",
                        value="",
                        lines=2
                    )
                    
                    basic_requirements = gr.Textbox(
                        label="📝 基本要求",
                        placeholder="描述这个角色需要做什么，例如：\n- 编写高质量、可维护的Python代码\n- 设计RESTful API\n- 处理数据库查询和优化",
                        lines=4,
                        value=""
                    )
                    
                    examples_input = gr.Textbox(
                        label="📚 示例 (可选)",
                        placeholder="""[
  {
    "input": {
      "function_name": "validate_email",
      "input_type": "str",
      "output_type": "bool",
      "description": "验证邮箱地址格式"
    },
    "output": "def validate_email(email: str) -> bool:\\n    if not isinstance(email, str):\\n        return False\\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\\n    return bool(re.match(pattern, email))"
  },
  {
    "input": {
      "class_name": "DatabaseConnection",
      "host": "localhost",
      "database": "mydb",
      "username": "admin"
    },
    "output": "@app.route('/api/users', methods=['GET'])\\ndef get_users():\\n    return jsonify(users)"
  }
]""",
                        lines=12,
                        value=""
                    )
                    
                    additional_requirements = gr.Textbox(
                        label="➕ 额外要求 (可选)",
                        placeholder="补充说明特殊要求，例如：\n- 代码需要包含详细的注释\n- 需要处理边界情况\n- 需要考虑性能优化",
                        lines=3,
                        value=""
                    )
                    
                    model_type = gr.Dropdown(
                        label="🤖 选择模型",
                        choices=["gemini", "openai"],
                        value="openai",
                        info="Gemini (Google) 或 OpenAI GPT"
                    )
                    
                    optimize_btn = gr.Button("🚀 开始优化", variant="primary", size="lg")
                
                with gr.Column(scale=2):
                    gr.HTML("<h3>📊 优化过程</h3>")
                    
                    status_output = gr.Textbox(
                        label="🔄 实时状态",
                        lines=10,
                        interactive=False,
                        show_copy_button=True
                    )
                    
                    with gr.Group():
                        result_output = gr.Markdown(
                            label="📋 优化结果",
                            visible=False
                        )
                        
                        with gr.Row():
                            copy_prompt_btn = gr.Button("📋 复制最终Prompt", variant="primary", visible=False)
                            view_prompt_btn = gr.Button("🔍 在验证页面查看", variant="secondary", visible=False)
        
        with gr.Tab("🔧 手动验证", id=1):
            gr.HTML("<h3>✨ Prompt验证和变量编辑</h3>")
            
            with gr.Row():
                with gr.Column():
                    manual_prompt = gr.Textbox(
                        label="📝 Prompt内容",
                        placeholder="请先运行优化或手动输入prompt...",
                        lines=10,
                        show_copy_button=True
                    )
                    
                    load_prompt_btn = gr.Button("📥 加载已生成的Prompt", variant="secondary")
                    
                    variables_hint = gr.Textbox(
                        label="💡 变量提示",
                        interactive=False,
                        lines=3
                    )
                    
                    variables_input = gr.Textbox(
                        label="🔧 变量定义",
                        placeholder="name=张三\ntopic=人工智能\ndate=2024年",
                        lines=5,
                        info="格式: 变量名=值 (每行一个)"
                    )
                    
                    validate_btn = gr.Button("✅ 验证Prompt", variant="primary")
                
                with gr.Column():
                    validation_result = gr.Markdown(
                        label="🎯 验证结果",
                        value="请输入prompt并点击验证..."
                    )
        
        with gr.Tab("📖 使用说明", id=2):
            gr.Markdown("""
            ## 📋 使用指南
            
            ### 🚀 基本使用流程
            1. **填写目标角色**: 描述prompt的目标用户群体
            2. **选择模型**: Gemini (推荐) 或 OpenAI
            3. **提供示例**: 输入期望的输入输出示例，使用JSON格式定义变量
            4. **添加要求**: 可选的额外要求和约束
            5. **开始优化**: 点击按钮开始流式优化过程
            
            ### 🔧 示例格式
            
            **JSON格式 (推荐):**
            ```json
            [
              {
                "input": {
                  "function_name": "validate_email",
                  "input_type": "str",
                  "output_type": "bool",
                  "description": "验证邮箱地址格式"
                },
                "output": "def validate_email(email: str) -> bool:\\n    if not isinstance(email, str):\\n        return False\\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\\n    return bool(re.match(pattern, email))"
              }
            ]
            ```
            
            **简单文本格式:**
            ```
            Input:
            function_name=validate_email
            input_type=str
            output_type=bool
            description=验证邮箱地址格式
            Output:
            def validate_email(email: str) -> bool:
                if not isinstance(email, str):
                    return False
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
                return bool(re.match(pattern, email))
            ```
            
            ### 🔧 手动验证功能
            
            1. **变量支持**: 在prompt中使用 `{变量名}` 定义动态变量
            2. **变量定义**: 在验证页面定义变量值
            3. **实时验证**: 查看替换变量后的最终prompt
            
            **变量定义示例:**
            ```
            function_name=validate_email
            input_type=str
            output_type=bool
            description=验证邮箱地址格式
            ```
            
            ### 🌐 环境配置
            
            需要配置相应的API密钥：
            - **Gemini**: `GOOGLE_API_KEY`
            - **OpenAI**: `OPENAI_API_KEY`
            
            ### 🔄 代理设置
            
            系统自动使用代理配置 `http://127.0.0.1:7890`，如需修改请设置环境变量：
            ```bash
            export HTTPS_PROXY=your_proxy_url
            export HTTP_PROXY=your_proxy_url
            ```
            """)
    
    # 事件绑定
    def switch_to_validation_tab():
        return gr.Tabs(selected=1), get_current_prompt()
    
    optimize_btn.click(
        fn=run_optimization,
        inputs=[role_input, basic_requirements, examples_input, additional_requirements, model_type],
        outputs=[status_output, result_output, copy_prompt_btn, view_prompt_btn],
        show_progress=True
    )
    
    copy_prompt_btn.click(
        fn=get_current_prompt,
        outputs=[gr.Textbox(visible=False)],
        js="(prompt) => navigator.clipboard.writeText(prompt)"
    )
    
    view_prompt_btn.click(
        fn=switch_to_validation_tab,
        outputs=[tabs, manual_prompt]
    )
    
    manual_prompt.change(
        fn=update_variables_hint,
        inputs=[manual_prompt],
        outputs=[variables_hint]
    )
    
    validate_btn.click(
        fn=validate_prompt,
        inputs=[manual_prompt, variables_input],
        outputs=[validation_result]
    )
    
    load_prompt_btn.click(
        fn=get_current_prompt,
        outputs=[manual_prompt]
    )

def main():
    """启动Web应用"""
    print("🚀 启动Prompt优化器Web界面...")
    print("🌐 代理配置: 自动使用 http://127.0.0.1:7890")
    print("📖 访问地址: http://localhost:7860")
    
    # 检查环境
    google_api_key = os.getenv('GOOGLE_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    print("\n🔑 API密钥状态:")
    print(f"   Google (Gemini): {'✅ 已配置' if google_api_key and google_api_key != 'your_google_api_key_here' else '❌ 未配置'}")
    print(f"   OpenAI (GPT): {'✅ 已配置' if openai_api_key and openai_api_key != 'your_openai_api_key_here' else '❌ 未配置'}")
    
    print("\n💡 提示: 请确保至少配置一个API密钥以使用相应的模型")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

if __name__ == "__main__":
    main() 