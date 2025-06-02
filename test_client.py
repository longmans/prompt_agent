import logging
import json

from typing import Any
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)


async def test_prompt_optimization(client: A2AClient, logger: logging.Logger) -> None:
    """测试Prompt优化请求"""
    
    # 测试用例1: 软件开发场景
    software_dev_payload = {
        "role": "software developers",
        "basic_requirements": "编写高质量、可维护的Python代码，包括函数、类和API设计",
        "examples": [
            {
                "input": "Write a function to calculate fibonacci numbers",
                "output": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            }
        ],
        "model_type": "openai"
    }
    
    logger.info("\n=== 测试软件开发场景 ===")
    request = SendMessageRequest(
        id=str(uuid4()),
        params=MessageSendParams(
            message={
                'role': 'user',
                'parts': [{'kind': 'text', 'text': json.dumps(software_dev_payload, ensure_ascii=False)}],
                'messageId': uuid4().hex,
            }
        )
    )
    
    response = await client.send_message(request)
    logger.info("软件开发场景响应:")
    logger.info(response.model_dump(mode='json', exclude_none=True))
    
    # 测试用例2: 内容创作场景
    content_creation_payload = {
        "role": "content creators",
        "basic_requirements": "创作引人入胜、结构清晰的内容，包括博客文章和社交媒体帖子",
        "examples": [
            {
                "input": "Write a blog post about AI trends",
                "output": "# The Future of AI: 5 Trends That Will Shape 2024\n\nAI continues to evolve rapidly..."
            }
        ],
        "model_type": "openai"
    }
    
    logger.info("\n=== 测试内容创作场景 ===")
    request = SendMessageRequest(
        id=str(uuid4()),
        params=MessageSendParams(
            message={
                'role': 'user',
                'parts': [{'kind': 'text', 'text': json.dumps(content_creation_payload, ensure_ascii=False)}],
                'messageId': uuid4().hex,
            }
        )
    )
    
    response = await client.send_message(request)
    logger.info("内容创作场景响应:")
    logger.info(response.model_dump(mode='json', exclude_none=True))
    
    # 测试用例3: 无示例场景
    no_examples_payload = {
        "role": "data scientists",
        "basic_requirements": "进行数据分析和可视化，生成清晰的见解报告",
        "examples": [],
        "model_type": "openai"
    }
    
    logger.info("\n=== 测试无示例场景 ===")
    request = SendMessageRequest(
        id=str(uuid4()),
        params=MessageSendParams(
            message={
                'role': 'user',
                'parts': [{'kind': 'text', 'text': json.dumps(no_examples_payload, ensure_ascii=False)}],
                'messageId': uuid4().hex,
            }
        )
    )
    
    response = await client.send_message(request)
    logger.info("无示例场景响应:")
    logger.info(response.model_dump(mode='json', exclude_none=True))
    
    # 测试用例4: 流式响应测试
    logger.info("\n=== 测试流式响应 ===")
    streaming_request = SendStreamingMessageRequest(
        id=str(uuid4()),
        params=MessageSendParams(
            message={
                'role': 'user',
                'parts': [{'kind': 'text', 'text': json.dumps(software_dev_payload, ensure_ascii=False)}],
                'messageId': uuid4().hex,
            }
        )
    )
    
    logger.info("开始接收流式响应:")
    async for chunk in client.send_message_streaming(streaming_request):
        logger.info(f"收到数据块: {chunk.model_dump(mode='json', exclude_none=True)}")


async def main() -> None:
    PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'
    EXTENDED_AGENT_CARD_PATH = '/agent/authenticatedExtendedCard'

    # Configure logging to show INFO level messages
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get a logger instance

    base_url = 'http://localhost:9999'

    # 设置较长的超时时间，因为prompt优化可能需要较长时间
    timeout_settings = httpx.Timeout(
        timeout=300.0,  # 总超时时间设为300秒
        connect=60.0,   # 连接超时时间
        read=240.0,     # 读取超时时间
        write=60.0      # 写入超时时间
    )

    async with httpx.AsyncClient(timeout=timeout_settings) as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        # Fetch Public Agent Card and Initialize Client
        final_agent_card_to_use: AgentCard | None = None

        try:
            logger.info(
                f'Attempting to fetch public agent card from: {base_url}{PUBLIC_AGENT_CARD_PATH}'
            )
            _public_card = await resolver.get_agent_card()
            logger.info('Successfully fetched public agent card:')
            logger.info(
                _public_card.model_dump_json(indent=2, exclude_none=True)
            )
            final_agent_card_to_use = _public_card
            logger.info(
                '\nUsing PUBLIC agent card for client initialization (default).'
            )

            if _public_card.supportsAuthenticatedExtendedCard:
                try:
                    logger.info(
                        f'\nPublic card supports authenticated extended card. Attempting to fetch from: {base_url}{EXTENDED_AGENT_CARD_PATH}'
                    )
                    auth_headers_dict = {
                        'Authorization': 'Bearer dummy-token-for-extended-card'
                    }
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs={'headers': auth_headers_dict},
                    )
                    logger.info(
                        'Successfully fetched authenticated extended agent card:'
                    )
                    logger.info(
                        _extended_card.model_dump_json(
                            indent=2, exclude_none=True
                        )
                    )
                    final_agent_card_to_use = _extended_card
                    logger.info(
                        '\nUsing AUTHENTICATED EXTENDED agent card for client initialization.'
                    )
                except Exception as e_extended:
                    logger.warning(
                        f'Failed to fetch extended agent card: {e_extended}. Will proceed with public card.',
                        exc_info=True,
                    )
            elif _public_card:
                logger.info(
                    '\nPublic card does not indicate support for an extended card. Using public card.'
                )

        except Exception as e:
            logger.error(
                f'Critical error fetching public agent card: {e}', exc_info=True
            )
            raise RuntimeError(
                'Failed to fetch the public agent card. Cannot continue.'
            ) from e

        client = A2AClient(
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )
        logger.info('A2AClient initialized.')
        
        # 运行Prompt优化测试
        await test_prompt_optimization(client, logger)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
