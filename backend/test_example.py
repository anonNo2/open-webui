#!/usr/bin/env python3
"""
简单的测试示例，用于验证 simulate_confidence_check 方法
"""

import asyncio
import json
import sys
import os,traceback

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_webui.routers.confidence import simulate_confidence_check

async def test_simulate_confidence_check():
    """简单的测试函数"""
    print("🧪 开始测试 simulate_confidence_check 方法...")
    
    # 测试数据
    text = ''''''
    workflow_id = "9b5bf909-e240-49f9-9e42-b65d2e761b53"
    
    print(f"📝 测试文本: {text}")
    print(f"🆔 工作流ID: {workflow_id}")
    print("-" * 50)
    
    # 收集输出
    results = []
    chunk_count = 0
    
    try:
        async for chunk in simulate_confidence_check(text, workflow_id):
            chunk_count += 1
            results.append(chunk)
            
            # 实时显示进度
            if chunk_count <= 5:  # 只显示前5个chunk
                print(f"📦 Chunk {chunk_count}: {chunk[:100]}...")
            elif chunk_count == 6:
                print("... (更多chunks)")
            
            # 解析并显示内容
            if chunk != "data: [DONE]\n\n":
                try:
                    json_str = chunk.replace("data: ", "").strip()
                    data = json.loads(json_str)
                    content = data["choices"][0]["delta"]["content"]
                    if "置信度评分" in content:
                        print(f"🎯 找到置信度评分: {content.strip()}")
                except Exception as e:
                    pass
    
    except Exception as e:
        traceback.print_exc()
        print(f"❌ 测试失败: {e}")
        return False
    
    print("-" * 50)
    print(f"✅ 测试完成! 总共收到 {chunk_count} 个chunks")
    
    # 验证结果
    if len(results) > 0:
        print("✅ 有输出结果")
    else:
        print("❌ 没有输出结果")
        return False
    
    if results[-1] == "data: [DONE]\n\n":
        print("✅ 完成信号正确")
    else:
        print("❌ 完成信号不正确")
        return False
    
    # 提取完整内容
    full_content = ""
    for result in results:
        if result != "data: [DONE]\n\n":
            try:
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                full_content += data["choices"][0]["delta"]["content"]
            except:
                pass
    
    # 验证关键内容
    if "智能置信度分析报告" in full_content:
        print("✅ 包含分析报告标题")
    else:
        print("❌ 缺少分析报告标题")
        return False
    
    if workflow_id in full_content:
        print("✅ 工作流ID在输出中")
    else:
        print("❌ 工作流ID不在输出中")
        return False
    
    if "置信度评分" in full_content:
        print("✅ 包含置信度评分")
    else:
        print("❌ 缺少置信度评分")
        return False
    
    print("\n🎉 所有测试通过!")
    return True

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_simulate_confidence_check())
    
    if success:
        print("\n✅ 测试成功完成!")
        sys.exit(0)
    else:
        print("\n❌ 测试失败!")
        sys.exit(1) 