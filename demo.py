#!/usr/bin/env python3
"""
Prompt优化器演示脚本
展示如何使用多Agent协作进行prompt优化，支持多种模型
"""

import asyncio
import json
import os
from prompt_optimizer import PromptOptimizerWorkflow, PromptRequest


async def demo_software_development_gemini():
    """演示为软件开发优化prompt - 使用Gemini模型"""
    print("🔧 演示：软件开发prompt优化 - Gemini模型")
    print("=" * 60)
    
    # 创建工作流
    workflow = PromptOptimizerWorkflow()
    
    # 创建请求
    request = PromptRequest(
        role="software developers",
        basic_requirements="编写高质量、可维护的Python代码，包括函数、类和API设计",
        examples=[  # 可选的示例
            {
                "input": "Write a function to calculate fibonacci numbers",
                "output": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            },
            {
                "input": "Create a REST API endpoint",
                "output": "@app.route('/api/users', methods=['GET'])\ndef get_users():\n    return jsonify(users)"
            }
        ],
        additional_requirements="代码需要包含详细的注释和错误处理",
        model_type="gemini"
    )
    
    print(f"目标角色: {request.role}")
    print(f"基本要求: {request.basic_requirements}")
    print(f"模型类型: {request.model_type.upper()}")
    print(f"示例数量: {len(request.examples or [])}")
    print("开始优化...")
    
    try:
        # 执行优化
        result = await workflow.optimize_prompt(request)
        
        # 显示结果
        print("\n✅ 优化完成！")
        print(f"\n📝 生成的Prompt:")
        print("-" * 30)
        print(result.get('generated_prompt', 'N/A'))
        
        print(f"\n🔍 评估结果:")
        print("-" * 30)
        for i, evaluation in enumerate(result.get('evaluations', []), 1):
            print(f"评估 {i}: {evaluation[:200]}...")
        
        print(f"\n🚀 改进方案 ({len(result.get('alternative_prompts', []))}):")
        print("-" * 30)
        for i, alt in enumerate(result.get('alternative_prompts', []), 1):
            print(f"方案 {i}: {alt[:100]}...")
        
        print(f"\n💡 最终推荐:")
        print("-" * 30)
        print(result.get('final_recommendation', 'N/A')[:200] + "...")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


async def demo_software_development_openai():
    """演示为软件开发优化prompt - 使用OpenAI模型"""
    print("\n\n🔧 演示：软件开发prompt优化 - OpenAI模型")
    print("=" * 60)
    
    # 检查OpenAI API密钥
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        print("⚠️ 跳过OpenAI演示：未配置OPENAI_API_KEY")
        return
    
    # 创建工作流
    workflow = PromptOptimizerWorkflow()
    
    # 创建请求
    request = PromptRequest(
        role="software developers",
        basic_requirements="编写健壮、可扩展的Python代码，重点关注错误处理和文档",
        examples=[  # 可选的示例
            {
                "input": json.dumps({
                    "function_name": "validate_email",
                    "input_type": "str",
                    "output_type": "bool",
                    "description": "验证邮箱地址格式"
                }),
                "output": "def validate_email(email: str) -> bool:\n    \"\"\"验证邮箱地址格式的有效性\n    Args:\n        email: 要验证的邮箱地址\n    Returns:\n        bool: 邮箱格式是否有效\n    \"\"\"\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n    return re.match(pattern, email) is not None"
            },
            {
                "input": json.dumps({
                    "class_name": "DatabaseConnection",
                    "host": "localhost",
                    "database": "mydb",
                    "username": "admin"
                }),
                "output": "class DatabaseConnection:\n    def __init__(self, host: str = 'localhost', database: str = 'mydb', username: str = 'admin'):\n        self.host = host\n        self.database = database\n        self.username = username\n        self.connection = None"
            }
        ],
        additional_requirements="代码需要包含完整的类型提示和异常处理",
        model_type="openai"
    )
    
    print(f"目标角色: {request.role}")
    print(f"基本要求: {request.basic_requirements}")
    print(f"模型类型: {request.model_type.upper()}")
    print(f"示例数量: {len(request.examples or [])}")
    print("开始优化...")
    
    try:
        # 执行优化
        result = await workflow.optimize_prompt(request)
        
        # 显示结果
        print("\n✅ 优化完成！")
        print(f"生成的prompt长度: {len(result.get('generated_prompt', ''))} 字符")
        print(f"生成的prompt: {result.get('generated_prompt', '')}")
        print(f"评估数量: {len(result.get('evaluations', []))}")
        print(f"改进方案数量: {len(result.get('alternative_prompts', []))}")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


async def demo_customer_support():
    """演示为客服优化prompt"""
    print("\n\n📞 演示：客服对话prompt优化 - Gemini模型")
    print("=" * 60)
    
    workflow = PromptOptimizerWorkflow()
    
    request = PromptRequest(
        role="customer support representatives",
        basic_requirements="提供专业、有同理心的客户服务，快速解决客户问题",
        examples=[  # 可选的示例
            {
                "input": "Customer complains about delayed delivery",
                "output": "I sincerely apologize for the delay. Let me check your order status and provide an update."
            },
            {
                "input": "Customer asks for refund",
                "output": "I understand your concern. I'd be happy to help with the refund process."
            }
        ],
        additional_requirements="保持积极友好的语气，提供明确的解决方案",
        model_type="openai"
    )
    
    print(f"目标角色: {request.role}")
    print(f"基本要求: {request.basic_requirements}")
    print(f"模型类型: {request.model_type.upper()}")
    print("开始优化...")
    
    try:
        result = await workflow.optimize_prompt(request)
        print("✅ 客服prompt优化完成！")
        print(f"生成的prompt长度: {len(result.get('generated_prompt', ''))} 字符")
        print(f"评估数量: {len(result.get('evaluations', []))}")
        print(f"改进方案数量: {len(result.get('alternative_prompts', []))}")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


async def demo_content_creation():
    """演示为内容创作优化prompt"""
    print("\n\n✍️ 演示：内容创作prompt优化 - OpenAI模型")
    print("=" * 60)
    
    workflow = PromptOptimizerWorkflow()
    
    request = PromptRequest(
        role="content creators",
        basic_requirements="创作引人入胜、结构清晰的内容，包括博客文章和社交媒体帖子",
        examples=[  # 可选的示例
            {
                "input": json.dumps({
                    "topic": "AI trends",
                    "target_audience": "tech professionals",
                    "tone": "professional",
                    "word_count": "1000"
                }),
                "output": "# The Future of AI: 5 Trends That Will Shape 2024\n\nArtificial Intelligence continues to evolve rapidly, transforming industries and reshaping how we work..."
            },
            {
                "input": json.dumps({
                    "topic": "sustainability",
                    "target_audience": "general public",
                    "tone": "casual",
                    "word_count": "200"
                }),
                "output": "🌱 Small changes, BIG impact! Here are 3 easy sustainability tips that anyone can follow to help protect our planet..."
            }
        ],
        additional_requirements="内容需要包含吸引人的标题和清晰的行动号召",
        model_type="openai"
    )
    
    print(f"目标角色: {request.role}")
    print(f"基本要求: {request.basic_requirements}")
    print(f"模型类型: {request.model_type.upper()}")
    print("开始优化...")
    
    try:
        result = await workflow.optimize_prompt(request)
        print("✅ 内容创作prompt优化完成！")
        
        # 显示简化的结果
        print(f"\n📊 优化结果摘要:")
        print(f"- 模型类型: {result.get('model_type', 'unknown').upper()}")
        print(f"- 原始示例: {len(result.get('original_examples', []))}")
        print(f"- 生成prompt长度: {len(result.get('generated_prompt', ''))} 字符")
        print(f"- 评估报告: {len(result.get('evaluations', []))} 份")
        print(f"- 改进方案: {len(result.get('alternative_prompts', []))} 个")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


async def demo_no_examples():
    """演示无示例的prompt优化"""
    print("\n\n🎯 演示：无示例的prompt优化 - OpenAI模型")
    print("=" * 60)
    
    # 检查OpenAI API密钥
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        print("⚠️ 跳过OpenAI演示：未配置OPENAI_API_KEY")
        return
    
    workflow = PromptOptimizerWorkflow()
    
    request = PromptRequest(
        role="data scientists",
        basic_requirements="进行数据分析和可视化，生成清晰的见解报告",
        examples=[],  # 不提供示例
        additional_requirements="报告需要包含数据来源、方法论和关键发现",
        model_type="openai"
    )
    
    print(f"目标角色: {request.role}")
    print(f"基本要求: {request.basic_requirements}")
    print(f"模型类型: {request.model_type.upper()}")
    print("开始优化...")
    
    try:
        result = await workflow.optimize_prompt(request)
        print("✅ 无示例prompt优化完成！")
        
        # 显示简化的结果
        print(f"\n📊 优化结果摘要:")
        print(f"- 生成prompt长度: {len(result.get('generated_prompt', ''))} 字符")
        print(f"- 评估报告: {len(result.get('evaluations', []))} 份")
        print(f"- 改进方案: {len(result.get('alternative_prompts', []))} 个")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


async def main():
    """主演示函数"""
    print("🚀 启动Prompt优化器演示...")
    print("\n💡 本演示将展示不同场景下的prompt优化过程")
    print("包括软件开发、客服对话、内容创作等场景")
    print("同时演示不同模型（Gemini/OpenAI）的效果")
    
    # 运行所有演示
    #await demo_software_development_gemini()
    await demo_software_development_openai()
    await demo_customer_support()
    await demo_content_creation()
    await demo_no_examples()  # 新增：演示无示例的情况
    
    print("\n🎉 演示完成！")
    print("\n📝 总结：")
    print("1. 支持多种用户角色和场景")
    print("2. 可以使用不同的模型")
    print("3. 示例是可选的，基本要求是必需的")
    print("4. 提供详细的评估和改进建议")
    print("5. 支持流式输出和格式化展示")

if __name__ == "__main__":
    asyncio.run(main()) 