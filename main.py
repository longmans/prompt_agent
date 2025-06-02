import uvicorn

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


if __name__ == '__main__':
    # --8<-- [start:AgentSkill]
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
    # --8<-- [end:AgentSkill]

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

    # --8<-- [start:AgentCard]
    # 公开的agent卡片
    public_agent_card = AgentCard(
        name='Prompt优化器 Agent',
        description='智能Prompt优化系统，支持角色定义、基本要求和示例，帮助用户生成高质量的prompt',
        url='http://localhost:9999/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[basic_skill],
        supportsAuthenticatedExtendedCard=True,
    )
    # --8<-- [end:AgentCard]

    # 认证扩展agent卡片
    # 包含高级功能
    extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'Prompt优化器 Agent - 专业版',
            'description': '专业级Prompt优化系统，提供深度角色分析、任务分解和定制化优化服务',
            'version': '1.1.0',
            'skills': [
                basic_skill,
                advanced_skill,
            ],  # 包含基础和高级技能
        }
    )

    request_handler = DefaultRequestHandler(
        agent_executor=PromptOptimizerAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
        extended_agent_card=extended_agent_card,
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9999)
