import uvicorn
import os
import logging
from typing import Optional

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from prompt_optimizer_executor import (
    PromptOptimizerAgentExecutor,  # type: ignore[import-untyped]
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('prompt_optimizer.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def check_environment() -> bool:
    """检查环境配置是否正确"""
    try:
        google_api_key = os.getenv('GOOGLE_API_KEY')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # 至少需要一个API密钥
        has_google = google_api_key and google_api_key != 'your_google_api_key_here'
        has_openai = openai_api_key and openai_api_key != 'your_openai_api_key_here'
        
        logger.info(f"Google API Key: {'✅ 已配置' if has_google else '❌ 未配置'}")
        logger.info(f"OpenAI API Key: {'✅ 已配置' if has_openai else '❌ 未配置'}")
        
        if not (has_google or has_openai):
            logger.error("❌ 至少需要配置一个API密钥(GOOGLE_API_KEY 或 OPENAI_API_KEY)")
            return False
        
        # 检查代理配置
        https_proxy = os.getenv('HTTPS_PROXY')
        http_proxy = os.getenv('HTTP_PROXY')
        
        if https_proxy or http_proxy:
            logger.info(f"代理配置: HTTPS={https_proxy}, HTTP={http_proxy}")
        else:
            logger.info("未配置代理，将使用默认代理设置")
        
        return True
        
    except Exception as e:
        logger.error(f"环境检查失败: {str(e)}")
        return False

def create_agent_skills() -> tuple[AgentSkill, AgentSkill]:
    """创建Agent技能定义"""
    try:
        basic_skill = AgentSkill(
            id='prompt_optimization',
            name='Prompt优化服务',
            description='通过多Agent协作优化prompt，支持角色定义、基本要求和可选示例',
            tags=['prompt engineering', 'optimization', 'multi-agent'],
            examples=[
                '为软件开发者优化代码生成prompt，包含基本编码规范和最佳实践',
                '为内容创作者优化写作prompt，定义创作风格和结构要求',
                '为数据分析师优化数据处理prompt，设定分析标准和输出格式'
            ],
        )

        advanced_skill = AgentSkill(
            id='advanced_prompt_optimization',
            name='高级Prompt优化服务',
            description='提供深度定制的prompt优化服务，包含详细的角色分析、任务分解和性能评估',
            tags=['prompt engineering', 'optimization', 'multi-agent', 'advanced', 'deep-analysis'],
            examples=[
                '基于详细的角色分析和任务要求进行多轮迭代优化',
                '针对特定业务场景的深度定制，包含完整的任务分解和评估标准',
                '结合性能指标和用户反馈的综合优化方案'
            ],
        )
        
        logger.info("Agent技能定义创建成功")
        return basic_skill, advanced_skill
        
    except Exception as e:
        logger.error(f"创建Agent技能失败: {str(e)}")
        raise

def create_agent_cards(basic_skill: AgentSkill, advanced_skill: AgentSkill) -> tuple[AgentCard, AgentCard]:
    """创建Agent卡片"""
    try:
        # 获取服务器配置
        host = os.getenv('SERVER_HOST', 'localhost')
        port = int(os.getenv('SERVER_PORT', '9999'))
        
        public_agent_card = AgentCard(
            name='Prompt优化器 Agent',
            description='智能Prompt优化系统，支持角色定义、基本要求和示例，帮助用户生成高质量的prompt',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=['text'],
            defaultOutputModes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=[basic_skill],
            supportsAuthenticatedExtendedCard=True,
        )

        # 认证扩展agent卡片 - 包含高级功能
        extended_agent_card = public_agent_card.model_copy(
            update={
                'name': 'Prompt优化器 Agent - 专业版',
                'description': '专业级Prompt优化系统，提供深度角色分析、任务分解和定制化优化服务',
                'version': '1.1.0',
                'skills': [basic_skill, advanced_skill],  # 包含基础和高级技能
            }
        )
        
        logger.info(f"Agent卡片创建成功: {public_agent_card.url}")
        return public_agent_card, extended_agent_card
        
    except Exception as e:
        logger.error(f"创建Agent卡片失败: {str(e)}")
        raise

def create_server(public_card: AgentCard, extended_card: AgentCard) -> A2AStarletteApplication:
    """创建服务器应用"""
    try:
        # 创建请求处理器
        request_handler = DefaultRequestHandler(
            agent_executor=PromptOptimizerAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )
        
        # 创建服务器应用
        server = A2AStarletteApplication(
            agent_card=public_card,
            http_handler=request_handler,
            extended_agent_card=extended_card,
        )
        
        logger.info("服务器应用创建成功")
        return server
        
    except Exception as e:
        logger.error(f"创建服务器失败: {str(e)}")
        raise

def main():
    """主函数"""
    try:
        logger.info("🚀 启动Prompt优化器服务...")
        
        # 检查环境配置
        if not check_environment():
            logger.error("❌ 环境配置检查失败，服务无法启动")
            return
        
        # 创建Agent组件
        basic_skill, advanced_skill = create_agent_skills()
        public_card, extended_card = create_agent_cards(basic_skill, advanced_skill)
        server = create_server(public_card, extended_card)
        
        # 获取服务器配置
        host = os.getenv('SERVER_HOST', '0.0.0.0')
        port = int(os.getenv('SERVER_PORT', '9999'))
        log_level = os.getenv('LOG_LEVEL', 'info').lower()
        workers = int(os.getenv('WORKERS', '1'))
        
        logger.info(f"服务器配置: host={host}, port={port}, log_level={log_level}, workers={workers}")
        
        # 启动服务器
        uvicorn.run(
            server.build(),
            host=host,
            port=port,
            log_level=log_level,
            timeout_keep_alive=30,
            workers=workers,
            access_log=True,
            reload=os.getenv('RELOAD', 'false').lower() == 'true'
        )
        
    except KeyboardInterrupt:
        logger.info("👋 服务器已手动停止")
    except Exception as e:
        logger.error(f"❌ 服务器启动失败: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
