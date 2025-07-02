#!/usr/bin/env python3
"""
结合HTML解析器和置信检查的示例
"""

import asyncio
import sys
import os
from html_parser import parse_html_content, extract_workflow_id_from_html, extract_plain_text_from_html
from open_webui.routers.confidence import simulate_confidence_check

async def confidence_check_with_html_parser():
    """使用HTML解析器进行置信检查的示例"""
    
    # 测试HTML文本
    html_text = '''<div><div id="" class="w-full space-y-1"><div class="w-fit text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition cursor-pointer"><div class="w-full font-medium flex items-center justify-between gap-2 "> <div class="">Planned for 0 seconds</div> <div class="flex self-center translate-y-[1px]"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3.5" stroke="currentColor" class="size-3.5"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5"></path></svg><!--<ChevronDown>--></div></div></div> </div><!--<Collapsible>--><p dir="auto">您好！我是一名政务助手，专门为用户提供政务、法规等方面的咨询和帮助。以下是我的简要介绍：<!--<MarkdownInlineTokens>--> </p><div class="my-2"></div><h3 dir="auto">功能概述<!--<MarkdownInlineTokens>--> </h3><ul dir="auto"><li class="text-start"> <strong>政务咨询<!--<MarkdownInlineTokens>--></strong>：提供关于政务流程、政策法规等方面的信息。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li><li class="text-start"> <strong>常识解答<!--<MarkdownInlineTokens>--></strong>：回答各类常识性问题，如历史、文化等。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li><li class="text-start"> <strong>非实时性信息<!--<MarkdownInlineTokens>--></strong>：根据内部知识库或预设规则，提供准确、简洁的回答。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li> </ul><div class="my-2"></div><h3 dir="auto">使用说明<!--<MarkdownInlineTokens>--> </h3><ul dir="auto"><li class="text-start"> <strong>非联网版本<!--<MarkdownInlineTokens>--></strong>：当前助手为非联网版本，无法获取实时信息。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li><li class="text-start"> <strong>建议<!--<MarkdownInlineTokens>--></strong>：如需获取最新信息，建议开启"联网搜索"功能。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li> </ul><div class="my-2"></div><h3 dir="auto">联系方式<!--<MarkdownInlineTokens>--> </h3><p dir="auto">如有任何问题或需要进一步帮助，请随时联系我。我将竭诚为您服务！<!--<MarkdownInlineTokens>--> </p><div class="my-2"></div><p dir="auto">希望以上信息对您有所帮助！<!--<MarkdownInlineTokens>--> </p><div class="my-2"></div><div id="" class="w-full space-y-1"><div data-type="hide" style="display: none;"><div class="mb-1.5" slot="content"><p dir="auto">dd467b95-6b43-4331-848c-9aad9cf1e914<!--<MarkdownInlineTokens>--> </p><!--<MarkdownTokens>--> </div></div> </div><!--<Collapsible>--><!--<MarkdownTokens>--><!--<Markdown>--></div>'''
    
    print("🔍 开始HTML解析和置信检查...")
    print("=" * 60)
    
    # 1. 解析HTML
    print("📋 步骤1: 解析HTML内容")
    parsed_content = parse_html_content(html_text)
    
    print(f"✅ 工作流ID: {parsed_content.get_workflow_id()}")
    print(f"✅ 计划时间: {parsed_content.workflow_info.planned_time}")
    print(f"✅ 段落数量: {len(parsed_content.sections)}")
    print(f"✅ 字符数: {parsed_content.metadata['total_characters']}")
    print(f"✅ 词数: {parsed_content.metadata['total_words']}")
    
    # 2. 提取纯文本
    print("\n📝 步骤2: 提取纯文本内容")
    plain_text = parsed_content.get_plain_text()
    print(f"✅ 提取的纯文本长度: {len(plain_text)} 字符")
    print(f"📄 纯文本预览: {plain_text[:200]}...")
    
    # 3. 分析内容结构
    print("\n🏗️  步骤3: 分析内容结构")
    for i, section in enumerate(parsed_content.sections, 1):
        print(f"  {i}. {section.title or '无标题段落'}")
        print(f"     类型: {section.type}")
        print(f"     内容长度: {len(section.content)} 字符")
        if section.content:
            print(f"     内容预览: {section.content[:100]}...")
    
    # 4. 进行置信检查
    print("\n🎯 步骤4: 进行置信检查")
    workflow_id = parsed_content.get_workflow_id()
    
    if not workflow_id:
        print("❌ 未找到工作流ID，无法进行置信检查")
        return
    
    print(f"🔍 使用工作流ID: {workflow_id}")
    print(f"📝 分析文本: {plain_text[:100]}...")
    
    # 收集置信检查结果
    results = []
    async for chunk in simulate_confidence_check(plain_text, workflow_id):
        results.append(chunk)
    
    print(f"✅ 置信检查完成，收到 {len(results)} 个数据块")
    
    # 5. 分析置信检查结果
    print("\n📊 步骤5: 分析置信检查结果")
    
    # 提取完整内容
    confidence_content = ""
    for result in results:
        if result != "data: [DONE]\n\n":
            import json
            try:
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                confidence_content += data["choices"][0]["delta"]["content"]
            except:
                pass
    
    # 查找置信度分数
    import re
    confidence_match = re.search(r'置信度评分: ([\d.]+)%', confidence_content)
    if confidence_match:
        confidence_score = float(confidence_match.group(1))
        print(f"🎯 置信度评分: {confidence_score}%")
        
        # 根据分数给出建议
        if confidence_score >= 90:
            print("✅ 置信度很高，内容质量优秀")
        elif confidence_score >= 80:
            print("✅ 置信度较高，内容质量良好")
        elif confidence_score >= 70:
            print("⚠️  置信度中等，建议进一步验证")
        else:
            print("❌ 置信度较低，需要重新检查")
    else:
        print("❌ 未找到置信度评分")
    
    # 6. 生成结构化报告
    print("\n📋 步骤6: 生成结构化报告")
    
    report = {
        "html_analysis": {
            "workflow_id": parsed_content.get_workflow_id(),
            "planned_time": parsed_content.workflow_info.planned_time,
            "sections_count": len(parsed_content.sections),
            "total_characters": parsed_content.metadata['total_characters'],
            "total_words": parsed_content.metadata['total_words'],
            "structure": {
                "paragraphs": parsed_content.metadata['paragraph_count'],
                "headings": parsed_content.metadata['heading_count'],
                "lists": parsed_content.metadata['list_count']
            }
        },
        "content_sections": [
            {
                "title": section.title,
                "type": section.type,
                "content_length": len(section.content)
            }
            for section in parsed_content.sections
        ],
        "confidence_analysis": {
            "score": confidence_score if confidence_match else None,
            "text_analyzed": plain_text[:500] + "..." if len(plain_text) > 500 else plain_text,
            "analysis_complete": True
        }
    }
    
    print("✅ 结构化报告生成完成")
    print(f"📊 报告包含 {len(report['content_sections'])} 个内容段落")
    print(f"🎯 置信度分析: {'完成' if report['confidence_analysis']['analysis_complete'] else '未完成'}")
    
    return report

def quick_extract_and_check(html_text: str):
    """快速提取和检查的便捷函数"""
    print("⚡ 快速提取和检查...")
    
    # 快速提取
    workflow_id = extract_workflow_id_from_html(html_text)
    plain_text = extract_plain_text_from_html(html_text)
    
    print(f"🆔 工作流ID: {workflow_id}")
    print(f"📝 文本长度: {len(plain_text)} 字符")
    print(f"📄 文本预览: {plain_text[:150]}...")
    
    return {
        "workflow_id": workflow_id,
        "plain_text": plain_text,
        "text_length": len(plain_text)
    }

if __name__ == "__main__":
    # 运行完整示例
    print("🚀 运行HTML解析器和置信检查示例")
    print("=" * 60)
    
    # 运行完整分析
    report = asyncio.run(confidence_check_with_html_parser())
    
    print("\n" + "=" * 60)
    print("🎉 分析完成!")
    
    if report:
        print(f"📋 工作流ID: {report['html_analysis']['workflow_id']}")
        print(f"📊 置信度评分: {report['confidence_analysis']['score']}%")
        print(f"📝 分析文本长度: {len(report['confidence_analysis']['text_analyzed'])} 字符") 