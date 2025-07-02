#!/usr/bin/env python3
"""
置信检查API测试脚本
"""

import asyncio
import json
import aiohttp

async def test_confidence_check():
    """测试置信检查API"""
    
    # 测试数据
    test_data = {
        "text": "这是一个测试响应内容，包含了一些信息和逻辑推理。因为我们需要验证这个响应的准确性，所以进行了详细的分析。",
        "workflowId": "test-workflow-123"
    }
    
    # API端点
    url = "http://localhost:8080/api/confidence/check"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=test_data) as response:
                print(f"状态码: {response.status}")
                print(f"响应头: {response.headers}")
                
                if response.status == 200:
                    print("开始接收流式响应:")
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            data = line_str[6:]  # 移除 'data: ' 前缀
                            if data == '[DONE]':
                                print("响应完成")
                                break
                            try:
                                parsed = json.loads(data)
                                if 'choices' in parsed and parsed['choices']:
                                    content = parsed['choices'][0].get('delta', {}).get('content', '')
                                    if content:
                                        print(f"内容: {content}")
                            except json.JSONDecodeError:
                                print(f"无法解析JSON: {data}")
                else:
                    error_text = await response.text()
                    print(f"错误: {error_text}")
                    
    except Exception as e:
        print(f"请求失败: {e}")

async def test_confidence_status():
    """测试置信检查服务状态"""
    
    url = "http://localhost:8080/api/confidence/status"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"状态检查状态码: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"服务状态: {data}")
                else:
                    error_text = await response.text()
                    print(f"状态检查错误: {error_text}")
                    
    except Exception as e:
        print(f"状态检查失败: {e}")

async def main():
    """主函数"""
    print("=== 置信检查API测试 ===")
    
    print("\n1. 测试服务状态:")
    await test_confidence_status()
    
    print("\n2. 测试置信检查:")
    await test_confidence_check()

if __name__ == "__main__":
    asyncio.run(main()) 