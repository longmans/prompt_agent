import json
import os
from typing import Dict, List, TypedDict, Annotated, Optional
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END, add_messages
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# 状态管理
class PromptOptimizerState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    role: str  # 目标用户角色 (如 "software developers", "book authors")
    examples: List[Dict[str, str]]  # few-shot examples [{"input": "...", "output": "..."}]
    current_prompt: str
    evaluations: List[str]
    alternative_prompts: List[str]
    final_prompt: str
    step: str  # 当前处理步骤
    model_type: str  # 模型类型


@dataclass
class PromptRequest:
    role: str
    examples: List[Dict[str, str]]
    additional_requirements: str = ""
    model_type: str = "gemini"  # 默认使用gemini，支持"gemini"和"openai"


class ModelFactory:
    """模型工厂类，用于创建不同类型的模型，支持代理配置"""
    
    _model_instances = {}  # 缓存模型实例以提高性能
    
    @staticmethod
    def create_model(model_type: str = "gemini"):
        """根据模型类型创建相应的模型实例，支持实例缓存和代理配置"""
        # 使用缓存避免重复创建模型实例
        cache_key = f"{model_type.lower()}"
        if cache_key in ModelFactory._model_instances:
            return ModelFactory._model_instances[cache_key]
        
        # 设置代理环境变量
        ModelFactory._setup_proxy()
        
        try:
            if model_type.lower() == "openai":
                model = ModelFactory._create_openai_model()
            elif model_type.lower() == "gemini":
                model = ModelFactory._create_gemini_model()
            else:
                raise ValueError(f"Unsupported model type: {model_type}. Supported types: openai, gemini")
            
            # 缓存模型实例
            ModelFactory._model_instances[cache_key] = model
            return model
            
        except Exception as e:
            raise RuntimeError(f"Failed to create {model_type} model: {str(e)}")
    
    @staticmethod
    def _setup_proxy():
        """设置代理配置"""
        # 从环境变量获取代理设置，如果没有则使用默认值
        https_proxy = os.getenv("HTTPS_PROXY", "http://127.0.0.1:7890")
        http_proxy = os.getenv("HTTP_PROXY", "http://127.0.0.1:7890")
        
        # 设置代理环境变量
        if https_proxy and not os.environ.get("https_proxy"):
            os.environ["https_proxy"] = https_proxy
        if http_proxy and not os.environ.get("http_proxy"):
            os.environ["http_proxy"] = http_proxy
            
        # 确保代理设置对所有HTTP请求生效
        if https_proxy:
            os.environ["HTTPS_PROXY"] = https_proxy
        if http_proxy:
            os.environ["HTTP_PROXY"] = http_proxy
    
    @staticmethod
    def _create_openai_model():
        """创建OpenAI模型"""
        try:
            from langchain_openai import ChatOpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
                
            return ChatOpenAI(
                model="gpt-4o-mini",
                api_key=api_key,
                temperature=0.7,
                timeout=60,  # 设置超时时间
                max_retries=3  # 设置重试次数
            )
        except ImportError:
            raise ImportError("Please install langchain-openai: pip install langchain-openai")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI model: {str(e)}")
    
    @staticmethod
    def _create_gemini_model():
        """创建Gemini模型"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required")
                
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=api_key,
                temperature=0.7,
                timeout=60,  # 设置超时时间
                max_retries=3  # 设置重试次数
            )
        except ImportError:
            raise ImportError("Please install langchain-google-genai: pip install langchain-google-genai")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini model: {str(e)}")
    
    @classmethod
    def clear_cache(cls):
        """清除模型实例缓存"""
        cls._model_instances.clear()


class PromptGeneratorAgent:
    """Prompt生成器Agent - 负责生成初始prompt工程指导和prompt"""
    
    def __init__(self, model=None, model_type: str = "gemini"):
        self.model_type = model_type
        self.model = model or ModelFactory.create_model(model_type)
    
    async def generate_prompt_engineering_guide(self, state: PromptOptimizerState) -> Dict:
        """生成针对特定角色的prompt工程指导"""
        if not state.get('role'):
            raise ValueError("Role is required for generating prompt engineering guide")
            
        guide_prompt = f"""
        Generate a detailed prompt engineering guide. The audience is {state['role']}.
        
        Include best practices, common patterns, and specific techniques that work well for {state['role']}.
        Focus on clarity, specificity, and effectiveness for this particular audience.
        
        Provide the guide in a structured format with examples.
        """
        
        try:
            response = await self.model.ainvoke([HumanMessage(content=guide_prompt)])
            return {
                "messages": [response],
                "step": "guide_generated"
            }
        except Exception as e:
            raise RuntimeError(f"Failed to generate prompt engineering guide: {str(e)}")
    
    async def generate_prompt_from_examples(self, state: PromptOptimizerState) -> Dict:
        """根据示例生成能产生这些输出的prompt"""
        if not state.get('examples'):
            raise ValueError("Examples are required for generating prompt")
            
        examples_text = "\n\n".join([
            f"Example {i+1}:\nInput: {ex.get('input', '')}\nOutput: {ex.get('output', '')}"
            for i, ex in enumerate(state['examples']) if isinstance(ex, dict)
        ])
        
        if not examples_text.strip():
            raise ValueError("Valid examples with 'input' and 'output' keys are required")
        
        generation_prompt = f"""
        Based on these {len(state['examples'])} examples of how I want my prompt to work:

        {examples_text}

        Generate a prompt that could have generated the examples' outputs, and include a better set of examples.

        The target audience is {state['role']}.

        Provide:
        1. A well-crafted prompt that would generate similar outputs
        2. 3-5 additional high-quality examples that demonstrate the prompt's effectiveness
        3. Brief explanation of the prompt's design principles

        Format your response as:
        
        PROMPT:
        [Your generated prompt here]
        
        ADDITIONAL_EXAMPLES:
        [New examples in the same input/output format]
        
        DESIGN_PRINCIPLES:
        [Brief explanation]
        """
        
        try:
            response = await self.model.ainvoke([HumanMessage(content=generation_prompt)])
            prompt_content = response.content if hasattr(response, 'content') else str(response)
            
            # 解析生成的prompt
            current_prompt = self._extract_prompt_from_response(prompt_content)
            
            return {
                "messages": [response],
                "current_prompt": current_prompt,
                "step": "prompt_generated"
            }
        except Exception as e:
            raise RuntimeError(f"Failed to generate prompt from examples: {str(e)}")
    
    def _extract_prompt_from_response(self, response: str) -> str:
        """从响应中提取prompt部分"""
        if not response:
            return ""
            
        lines = response.split('\n')
        prompt_lines = []
        in_prompt_section = False
        
        for line in lines:
            if 'PROMPT:' in line:
                in_prompt_section = True
                continue
            elif 'ADDITIONAL_EXAMPLES:' in line or 'DESIGN_PRINCIPLES:' in line:
                in_prompt_section = False
            elif in_prompt_section:
                prompt_lines.append(line)
        
        return '\n'.join(prompt_lines).strip()


class PromptEvaluatorAgent:
    """Prompt评估器Agent - 负责评估prompt质量"""
    
    def __init__(self, model=None, model_type: str = "gemini"):
        self.model_type = model_type
        self.model = model or ModelFactory.create_model(model_type)
    
    async def generate_evaluation_guide(self, state: PromptOptimizerState) -> Dict:
        """生成针对特定角色的prompt评估指导"""
        if not state.get('role'):
            raise ValueError("Role is required for generating evaluation guide")
            
        eval_guide_prompt = f"""
        Generate a detailed prompt evaluation guide. The audience is {state['role']}.
        
        Include criteria for evaluating prompts specifically for {state['role']}, such as:
        - Clarity and specificity
        - Effectiveness for the target use case
        - Potential edge cases
        - Performance considerations
        - Maintainability and scalability
        
        Provide a structured evaluation framework.
        """
        
        try:
            response = await self.model.ainvoke([HumanMessage(content=eval_guide_prompt)])
            return {
                "messages": [response],
                "step": "evaluation_guide_generated"
            }
        except Exception as e:
            raise RuntimeError(f"Failed to generate evaluation guide: {str(e)}")
    
    async def evaluate_prompt(self, state: PromptOptimizerState) -> Dict:
        """评估当前prompt"""
        if not state.get('current_prompt'):
            raise ValueError("Current prompt is required for evaluation")
            
        evaluation_prompt = f"""
        Evaluate this prompt for {state['role']}:

        PROMPT TO EVALUATE:
        {state['current_prompt']}

        ORIGINAL EXAMPLES IT SHOULD HANDLE:
        {self._format_examples(state.get('examples', []))}

        Provide a detailed evaluation including:
        1. Strengths of the current prompt
        2. Potential weaknesses or limitations
        3. How well it addresses the target audience ({state['role']})
        4. Specific areas for improvement
        5. Overall score (1-10) with justification

        Be thorough and constructive in your evaluation.
        """
        
        try:
            response = await self.model.ainvoke([HumanMessage(content=evaluation_prompt)])
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "messages": [response],
                "evaluations": state.get("evaluations", []) + [response_content],
                "step": "prompt_evaluated"
            }
        except Exception as e:
            raise RuntimeError(f"Failed to evaluate prompt: {str(e)}")
    
    def _format_examples(self, examples: List[Dict[str, str]]) -> str:
        """格式化示例，增加错误处理"""
        if not examples:
            return "No examples provided"
            
        formatted_examples = []
        for ex in examples:
            if isinstance(ex, dict) and 'input' in ex and 'output' in ex:
                formatted_examples.append(f"Input: {ex['input']}\nOutput: {ex['output']}")
        
        return "\n\n".join(formatted_examples) if formatted_examples else "No valid examples found"


class PromptImproverAgent:
    """Prompt改进器Agent - 负责生成改进的prompt版本"""
    
    def __init__(self, model=None, model_type: str = "gemini"):
        self.model_type = model_type
        self.model = model or ModelFactory.create_model(model_type)
    
    async def generate_improved_prompts(self, state: PromptOptimizerState) -> Dict:
        """生成3个改进的prompt变体"""
        if not state.get('current_prompt'):
            raise ValueError("Current prompt is required for generating improvements")
            
        if not state.get('evaluations'):
            raise ValueError("Evaluation feedback is required for generating improvements")
        
        improvement_prompt = f"""
        Based on the evaluation, generate 3 improved alternative prompts for {state['role']}.

        CURRENT PROMPT:
        {state['current_prompt']}

        EVALUATION FEEDBACK:
        {state['evaluations'][-1] if state['evaluations'] else "No evaluation available"}

        ORIGINAL EXAMPLES TO HANDLE:
        {self._format_examples(state.get('examples', []))}

        Generate 3 distinct improved versions that address the identified weaknesses while maintaining the strengths. Each should:
        1. Be specifically tailored for {state['role']}
        2. Address the feedback from the evaluation
        3. Maintain or improve upon the original prompt's capabilities
        4. Have a clear improvement focus (e.g., clarity, specificity, edge case handling)

        Format as:
        
        ALTERNATIVE 1: [Focus: specific improvement area]
        [Improved prompt 1]

        ALTERNATIVE 2: [Focus: specific improvement area]  
        [Improved prompt 2]

        ALTERNATIVE 3: [Focus: specific improvement area]
        [Improved prompt 3]

        For each alternative, briefly explain the key improvements made.
        """
        
        try:
            response = await self.model.ainvoke([HumanMessage(content=improvement_prompt)])
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # 解析生成的alternative prompts
            alternative_prompts = self._extract_alternatives(response_content)
            
            # 确保至少有一个改进方案
            if not alternative_prompts:
                alternative_prompts = [state['current_prompt']]  # 如果解析失败，使用原prompt
            
            return {
                "messages": [response],
                "alternative_prompts": alternative_prompts,
                "step": "alternatives_generated"
            }
        except Exception as e:
            raise RuntimeError(f"Failed to generate improved prompts: {str(e)}")
    
    def _extract_alternatives(self, response: str) -> List[str]:
        """从响应中提取alternative prompts，改进解析逻辑"""
        if not response:
            return []
            
        alternatives = []
        lines = response.split('\n')
        current_alternative = []
        in_alternative = False
        
        for line in lines:
            if 'ALTERNATIVE' in line and ':' in line:
                if current_alternative and in_alternative:
                    alt_text = '\n'.join(current_alternative).strip()
                    if alt_text:  # 确保内容不为空
                        alternatives.append(alt_text)
                current_alternative = []
                in_alternative = True
            elif in_alternative and line.strip():
                # 跳过Focus说明行
                if not (line.strip().startswith('[Focus:') and line.strip().endswith(']')):
                    current_alternative.append(line)
        
        # 添加最后一个alternative
        if current_alternative and in_alternative:
            alt_text = '\n'.join(current_alternative).strip()
            if alt_text:
                alternatives.append(alt_text)
        
        return alternatives
    
    def _format_examples(self, examples: List[Dict[str, str]]) -> str:
        """格式化示例，与评估器保持一致"""
        if not examples:
            return "No examples provided"
            
        formatted_examples = []
        for ex in examples:
            if isinstance(ex, dict) and 'input' in ex and 'output' in ex:
                formatted_examples.append(f"Input: {ex['input']}\nOutput: {ex['output']}")
        
        return "\n\n".join(formatted_examples) if formatted_examples else "No valid examples found"


class PromptOptimizerWorkflow:
    """协调多个Agent的工作流，优化错误处理和状态管理"""
    
    def __init__(self, model_type: str = "gemini"):
        self.model_type = model_type
        try:
            self.generator = PromptGeneratorAgent(model_type=model_type)
            self.evaluator = PromptEvaluatorAgent(model_type=model_type)
            self.improver = PromptImproverAgent(model_type=model_type)
            self.workflow = self._build_workflow()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize workflow with {model_type} model: {str(e)}")
    
    def _build_workflow(self) -> StateGraph:
        """构建LangGraph工作流"""
        workflow = StateGraph(PromptOptimizerState)
        
        # 添加节点
        workflow.add_node("generate_guide", self._generate_guide_node)
        workflow.add_node("generate_prompt", self._generate_prompt_node)
        workflow.add_node("generate_eval_guide", self._generate_eval_guide_node)
        workflow.add_node("evaluate_prompt", self._evaluate_prompt_node)
        workflow.add_node("improve_prompts", self._improve_prompts_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # 定义流程
        workflow.add_edge(START, "generate_guide")
        workflow.add_edge("generate_guide", "generate_prompt")
        workflow.add_edge("generate_prompt", "generate_eval_guide")
        workflow.add_edge("generate_eval_guide", "evaluate_prompt")
        workflow.add_edge("evaluate_prompt", "improve_prompts")
        workflow.add_edge("improve_prompts", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _generate_guide_node(self, state: PromptOptimizerState):
        """生成指导节点，增加错误处理"""
        try:
            return await self.generator.generate_prompt_engineering_guide(state)
        except Exception as e:
            print(f"Warning: Failed to generate guide: {str(e)}")
            return {"step": "guide_skipped", "messages": []}
    
    async def _generate_prompt_node(self, state: PromptOptimizerState):
        """生成prompt节点，增加错误处理"""
        try:
            return await self.generator.generate_prompt_from_examples(state)
        except Exception as e:
            print(f"Error: Failed to generate prompt: {str(e)}")
            # 返回一个基本的prompt作为fallback
            return {
                "current_prompt": "Please provide a clear and specific response to the user's request.",
                "step": "prompt_fallback"
            }
    
    async def _generate_eval_guide_node(self, state: PromptOptimizerState):
        """生成评估指导节点"""
        try:
            return await self.evaluator.generate_evaluation_guide(state)
        except Exception as e:
            print(f"Warning: Failed to generate evaluation guide: {str(e)}")
            return {"step": "eval_guide_skipped", "messages": []}
    
    async def _evaluate_prompt_node(self, state: PromptOptimizerState):
        """评估prompt节点"""
        try:
            return await self.evaluator.evaluate_prompt(state)
        except Exception as e:
            print(f"Warning: Failed to evaluate prompt: {str(e)}")
            # 提供基本评估
            return {
                "evaluations": state.get("evaluations", []) + ["Basic evaluation: The prompt appears functional but may need refinement."],
                "step": "evaluation_fallback"
            }
    
    async def _improve_prompts_node(self, state: PromptOptimizerState):
        """改进prompt节点"""
        try:
            return await self.improver.generate_improved_prompts(state)
        except Exception as e:
            print(f"Warning: Failed to generate improvements: {str(e)}")
            # 如果改进失败，使用当前prompt作为alternative
            current_prompt = state.get('current_prompt', '')
            return {
                "alternative_prompts": [current_prompt] if current_prompt else [],
                "step": "improvement_fallback"
            }
    
    async def _finalize_node(self, state: PromptOptimizerState):
        """最终化处理，选择最佳prompt，改进选择逻辑"""
        current_prompt = state.get("current_prompt", "")
        alternative_prompts = state.get("alternative_prompts", [])
        
        # 改进的选择逻辑
        if alternative_prompts:
            # 选择最长的alternative作为最终推荐（通常更详细）
            final_prompt = max(alternative_prompts, key=len)
        else:
            final_prompt = current_prompt
        
        # 确保final_prompt不为空
        if not final_prompt.strip():
            final_prompt = "Please provide a clear and specific response to the user's request."
        
        return {
            "final_prompt": final_prompt,
            "step": "completed"
        }
    
    async def optimize_prompt(self, request: PromptRequest) -> Dict:
        """执行prompt优化流程，增加输入验证和错误处理"""
        # 输入验证
        if not request.role.strip():
            raise ValueError("Role cannot be empty")
            
        if not request.examples:
            raise ValueError("At least one example is required")
            
        for i, example in enumerate(request.examples):
            if not isinstance(example, dict):
                raise ValueError(f"Example {i+1} must be a dictionary")
            if 'input' not in example or 'output' not in example:
                raise ValueError(f"Example {i+1} must have 'input' and 'output' keys")
            if not example['input'].strip() or not example['output'].strip():
                raise ValueError(f"Example {i+1} input and output cannot be empty")
        
        initial_state = PromptOptimizerState(
            messages=[],
            role=request.role.strip(),
            examples=request.examples,
            current_prompt="",
            evaluations=[],
            alternative_prompts=[],
            final_prompt="",
            step="started",
            model_type=request.model_type
        )
        
        try:
            # 执行工作流
            result = await self.workflow.ainvoke(initial_state)
            
            return {
                "role": result["role"],
                "model_type": result["model_type"],
                "original_examples": result["examples"],
                "generated_prompt": result.get("current_prompt", ""),
                "evaluations": result.get("evaluations", []),
                "alternative_prompts": result.get("alternative_prompts", []),
                "final_recommendation": result.get("final_prompt", ""),
                "step": result.get("step", "unknown")
            }
        except Exception as e:
            raise RuntimeError(f"Workflow execution failed: {str(e)}") 