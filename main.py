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
        description='通过多Agent协作优化prompt，包括生成、评估和改进',
        tags=['prompt engineering', 'optimization', 'multi-agent'],
        examples=[
            '为软件开发者优化代码生成prompt',
            '为客服人员优化对话prompt',
            '为内容创作者优化写作prompt'
        ],
    )
    # --8<-- [end:AgentSkill]

    advanced_skill = AgentSkill(
        id='advanced_prompt_optimization',
        name='高级Prompt优化服务',
        description='包含深度分析、多轮优化和自定义评估指标的高级prompt优化服务',
        tags=['prompt engineering', 'optimization', 'multi-agent', 'advanced', 'deep-analysis'],
        examples=[
            '进行多轮迭代的prompt优化',
            '基于特定业务场景的定制化优化',
            '包含性能基准测试的prompt评估'
        ],
    )

    # --8<-- [start:AgentCard]
    # 公开的agent卡片
    public_agent_card = AgentCard(
        name='Prompt优化器 Agent',
        description='基于多Agent协作的智能Prompt优化系统，帮助用户生成、评估和改进各种场景下的prompt',
        url='http://localhost:9999/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[basic_skill],  # 基础技能
        supportsAuthenticatedExtendedCard=True,
    )
    # --8<-- [end:AgentCard]

    # 认证扩展agent卡片
    # 包含高级功能
    extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'Prompt优化器 Agent - 专业版',
            'description': '专业级Prompt优化系统，提供深度分析、多轮优化和定制化服务',
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
