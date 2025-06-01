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
    workflow = PromptOptimizerWorkflow(model_type="gemini")
    
    # 创建请求
    request = PromptRequest(
        role="software developers",
        examples=[
            {
                "input": "Write a function to calculate fibonacci numbers",
                "output": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            },
            {
                "input": "Create a REST API endpoint",
                "output": "@app.route('/api/users', methods=['GET'])\ndef get_users():\n    return jsonify(users)"
            }
        ],
        additional_requirements="Focus on clean, maintainable code",
        model_type="gemini"
    )
    
    print(f"目标角色: {request.role}")
    print(f"模型类型: {request.model_type.upper()}")
    print(f"示例数量: {len(request.examples)}")
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
    workflow = PromptOptimizerWorkflow(model_type="openai")
    
    # 创建请求
    request = PromptRequest(
        role="software developers",
        examples=[
            {
                "input": "Write a function to validate email addresses",
                "output": "import re\n\ndef validate_email(email):\n    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'\n    return re.match(pattern, email) is not None"
            },
            {
                "input": "Create a class for handling database connections",
                "output": "class DatabaseConnection:\n    def __init__(self, host, database, user, password):\n        self.host = host\n        self.database = database\n        self.user = user\n        self.password = password\n        self.connection = None"
            }
        ],
        additional_requirements="Include error handling and documentation",
        model_type="openai"
    )
    
    print(f"目标角色: {request.role}")
    print(f"模型类型: {request.model_type.upper()}")
    print(f"示例数量: {len(request.examples)}")
    print("开始优化...")
    
    try:
        # 执行优化
        result = await workflow.optimize_prompt(request)
        
        # 显示结果
        print("\n✅ 优化完成！")
        print(f"生成的prompt长度: {len(result.get('generated_prompt', ''))} 字符")
        print(f"评估数量: {len(result.get('evaluations', []))}")
        print(f"改进方案数量: {len(result.get('alternative_prompts', []))}")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


async def demo_customer_support():
    """演示为客服优化prompt"""
    print("\n\n📞 演示：客服对话prompt优化 - Gemini模型")
    print("=" * 60)
    
    workflow = PromptOptimizerWorkflow(model_type="gemini")
    
    request = PromptRequest(
        role="customer support representatives",
        examples=[
            {
                "input": "Customer complains about delayed delivery",
                "output": "I sincerely apologize for the delay. Let me check your order status and provide an update."
            },
            {
                "input": "Customer asks for refund",
                "output": "I understand your concern. I'd be happy to help with the refund process."
            }
        ],
        additional_requirements="Maintain empathetic and professional tone",
        model_type="gemini"
    )
    
    print(f"目标角色: {request.role}")
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
    print("\n\n✍️ 演示：内容创作prompt优化 - Gemini模型")
    print("=" * 60)
    
    workflow = PromptOptimizerWorkflow(model_type="gemini")
    
    request = PromptRequest(
        role="content creators",
        examples=[
            {
                "input": "Write a blog post about AI trends",
                "output": "# The Future of AI: 5 Trends That Will Shape 2024\n\nAI continues to evolve rapidly..."
            },
            {
                "input": "Create social media content about sustainability",
                "output": "🌱 Small changes, BIG impact! Here are 3 easy sustainability tips..."
            }
        ],
        additional_requirements="Engaging tone with clear call-to-action",
        model_type="gemini"
    )
    
    print(f"目标角色: {request.role}")
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


def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查Google API密钥
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key or google_api_key == 'your_google_api_key_here':
        print("❌ 未配置GOOGLE_API_KEY")
        google_configured = False
    else:
        print("✅ Google API密钥已配置")
        google_configured = True
    
    # 检查OpenAI API密钥
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key or openai_api_key == 'your_openai_api_key_here':
        print("⚠️ 未配置OPENAI_API_KEY (OpenAI功能将被跳过)")
        openai_configured = False
    else:
        print("✅ OpenAI API密钥已配置")
        openai_configured = True
    
    if not google_configured:
        print("\n请先配置Google API密钥：")
        print("export GOOGLE_API_KEY='your_actual_api_key'")
        print("或编辑.env文件")
        return False
    
    return True


async def main():
    """主演示函数"""
    print("🤖 Prompt优化器多Agent协作演示")
    print("基于LangGraph的智能prompt工程系统 - 多模型支持")
    print("=" * 70)
    
    # 检查环境
    if not check_environment():
        return
    
    print("\n开始演示多个使用场景和模型...\n")
    
    # 运行演示
    try:
        await demo_software_development_gemini()
        await demo_software_development_openai()
        await demo_customer_support()
        await demo_content_creation()
        
        print("\n" + "=" * 70)
        print("🎉 所有演示完成！")
        print("\n📋 总结:")
        print("- 多Agent协作架构成功展示")
        print("- 支持Gemini和OpenAI两种模型")
        print("- 针对不同用户角色的prompt优化")
        print("- 生成、评估、改进的完整流程")
        print("- 可扩展的LangGraph工作流")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")


if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 运行演示
    asyncio.run(main()) 