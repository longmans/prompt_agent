#!/usr/bin/env python3
"""
测试Web界面组件
"""

import asyncio
import os
from web import StreamingOptimizer, validate_inputs, extract_variables, validate_prompt

def test_input_validation():
    """测试输入验证功能"""
    print("🧪 测试输入验证...")
    
    # 测试正常输入（完整字段）
    result = validate_inputs(
        role="software developers",
        basic_requirements="编写高质量、可维护的代码",
        examples='[{"input": "test", "output": "result"}]',
        model_type="gemini"
    )
    print(f"完整字段验证: {result}")
    
    # 测试必需字段（无示例）
    result = validate_inputs(
        role="content writers",
        basic_requirements="创作引人入胜的文章",
        examples="",
        model_type="openai"
    )
    print(f"必需字段验证: {result}")
    
    # 测试空角色
    result = validate_inputs(
        role="",
        basic_requirements="编写代码",
        examples='[{"input": "test", "output": "result"}]',
        model_type="gemini"
    )
    print(f"空角色验证: {result}")
    
    # 测试空基本要求
    result = validate_inputs(
        role="developers",
        basic_requirements="",
        examples='[{"input": "test", "output": "result"}]',
        model_type="gemini"
    )
    print(f"空基本要求验证: {result}")

def test_example_parsing():
    """测试示例解析功能"""
    print("\n🧪 测试示例解析...")
    
    optimizer = StreamingOptimizer()
    
    # 测试JSON格式
    json_examples = '[{"input": "Write a function", "output": "def example():"}]'
    parsed = optimizer._parse_examples(json_examples)
    print(f"JSON解析结果: {parsed}")
    
    # 测试文本格式
    text_examples = """Input: Write a function
Output: def example():

Input: Create a class
Output: class Example:"""
    parsed = optimizer._parse_examples(text_examples)
    print(f"文本解析结果: {parsed}")
    
    # 测试空示例（新增）
    empty_examples = ""
    parsed = optimizer._parse_examples(empty_examples)
    print(f"空示例解析结果: {parsed}")

def test_variable_extraction():
    """测试变量提取功能"""
    print("\n🧪 测试变量提取...")
    
    # 测试包含变量的prompt
    prompt_with_vars = "Hello {name}, today we will discuss {topic} in {year}."
    variables = extract_variables(prompt_with_vars)
    print(f"提取的变量: {variables}")
    
    # 测试不包含变量的prompt
    prompt_no_vars = "This is a simple prompt without variables."
    variables = extract_variables(prompt_no_vars)
    print(f"无变量prompt: {variables}")

def test_prompt_validation():
    """测试prompt验证功能"""
    print("\n🧪 测试prompt验证...")
    
    # 测试带变量的prompt验证
    prompt = "Hello {name}, let's discuss {topic}."
    variables = "name=张三\ntopic=人工智能"
    result = validate_prompt(prompt, variables)
    print(f"变量替换验证:\n{result}")
    
    # 测试缺少变量定义
    prompt = "Hello {name}, let's discuss {topic}."
    variables = "name=张三"  # 缺少topic
    result = validate_prompt(prompt, variables)
    print(f"缺少变量验证:\n{result}")

async def test_streaming_optimizer():
    """测试流式优化器（不实际调用API）"""
    print("\n🧪 测试流式优化器结构...")
    
    optimizer = StreamingOptimizer()
    
    # 测试示例解析
    examples = '[{"input": "Write a function", "output": "def example():"}]'
    parsed = optimizer._parse_examples(examples)
    
    if parsed:
        print("✅ 示例解析正常")
    else:
        print("❌ 示例解析失败")
    
    # 测试结果格式化（更新字段）
    test_result = {
        "role": "software developers",
        "basic_requirements": "编写高质量、可维护的代码",
        "model_type": "gemini",
        "original_examples": parsed,
        "generated_prompt": "Please write clean, maintainable code.",
        "evaluations": ["This prompt is clear and specific."],
        "alternative_prompts": ["Write code that is easy to understand.", "Create maintainable software."],
        "final_recommendation": "Please write clean, maintainable code that follows best practices.",
        "step": "completed"
    }
    
    formatted = optimizer._format_final_result(test_result)
    print("✅ 结果格式化正常")
    print(f"格式化结果长度: {len(formatted)} 字符")

def test_environment():
    """测试环境配置"""
    print("\n🧪 测试环境配置...")
    
    google_key = os.getenv('GOOGLE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"Google API Key: {'✅ 已配置' if google_key and google_key != 'your_google_api_key_here' else '❌ 未配置'}")
    print(f"OpenAI API Key: {'✅ 已配置' if openai_key and openai_key != 'your_openai_api_key_here' else '❌ 未配置'}")
    
    # 测试代理配置
    from prompt_optimizer import ModelFactory
    ModelFactory._setup_proxy()
    
    https_proxy = os.getenv('HTTPS_PROXY')
    http_proxy = os.getenv('HTTP_PROXY')
    
    print(f"HTTPS代理: {https_proxy}")
    print(f"HTTP代理: {http_proxy}")

async def main():
    """主测试函数"""
    print("🚀 开始测试Web界面组件...")
    print("=" * 50)
    
    # 运行所有测试
    test_input_validation()
    test_example_parsing()
    test_variable_extraction()
    test_prompt_validation()
    await test_streaming_optimizer()
    test_environment()
    
    print("\n" + "=" * 50)
    print("🎉 所有组件测试完成！")
    print("\n📝 Web界面功能说明：")
    print("1. 🚀 Prompt优化 - 流式输出优化过程")
    print("2. 🔧 手动验证 - 变量编辑和prompt验证")  
    print("3. 📖 使用说明 - 详细的操作指南")
    print("\n💡 启动Web界面: python web.py")
    print("📖 访问地址: http://localhost:7860")

if __name__ == "__main__":
    asyncio.run(main()) 