#!/usr/bin/env python3
"""
HTML解析器，用于解析置信检查中的HTML文本
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
import json

@dataclass
class WorkflowInfo:
    """工作流信息"""
    workflow_id: str
    planned_time: str = ""
    
@dataclass
class ContentSection:
    """内容段落"""
    title: str = ""
    content: str = ""
    type: str = "text"  # text, list, heading
    
@dataclass
class ListItem:
    """列表项"""
    text: str
    emphasis: List[str] = field(default_factory=list)
    
@dataclass
class ParsedContent:
    """解析后的内容结构"""
    workflow_info: WorkflowInfo = field(default_factory=lambda: WorkflowInfo(workflow_id=""))
    sections: List[ContentSection] = field(default_factory=list)
    raw_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_plain_text(self) -> str:
        """获取纯文本内容"""
        text_parts = []
        
        for section in self.sections:
            if section.title:
                text_parts.append(f"{section.title}: {section.content}")
            else:
                text_parts.append(section.content)
        
        return "\n".join(text_parts)
    
    def get_workflow_id(self) -> str:
        """获取工作流ID"""
        return self.workflow_info.workflow_id
    
    def get_section_by_title(self, title: str) -> Optional[ContentSection]:
        """根据标题获取段落"""
        for section in self.sections:
            if section.title.lower() == title.lower():
                return section
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "workflow_info": {
                "workflow_id": self.workflow_info.workflow_id,
                "planned_time": self.workflow_info.planned_time
            },
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "type": section.type
                }
                for section in self.sections
            ],
            "raw_text": self.raw_text,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """转换为JSON格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

class HTMLParser:
    """HTML解析器"""
    
    def __init__(self):
        self.soup = None
    
    def parse(self, html_text: str) -> ParsedContent:
        """解析HTML文本"""
        self.soup = BeautifulSoup(html_text, 'html.parser')
        
        # 创建解析结果
        parsed_content = ParsedContent()
        parsed_content.raw_text = html_text
        
        # 提取工作流信息
        parsed_content.workflow_info = self._extract_workflow_info()
        
        # 提取内容段落
        parsed_content.sections = self._extract_sections()
        
        # 提取元数据
        parsed_content.metadata = self._extract_metadata()
        
        return parsed_content
    
    def _extract_workflow_info(self) -> WorkflowInfo:
        """提取工作流信息"""
        workflow_info = WorkflowInfo(workflow_id="")
        
        # 查找工作流ID
        workflow_div = self.soup.find('div', {'data-type': 'hide'})
        if workflow_div:
            workflow_text = workflow_div.get_text(strip=True)
            # 使用正则表达式提取UUID格式的工作流ID
            uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
            match = re.search(uuid_pattern, workflow_text)
            if match:
                workflow_info.workflow_id = match.group(0)
        
        # 查找计划时间
        time_div = self.soup.find('div', string=re.compile(r'Planned for'))
        if time_div:
            workflow_info.planned_time = time_div.get_text(strip=True)
        
        return workflow_info
    
    def _extract_sections(self) -> List[ContentSection]:
        """提取内容段落"""
        sections = []
        
        # 查找所有段落和标题
        elements = self.soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol'])
        
        current_section = None
        
        for element in elements:
            if element.name.startswith('h'):  # 标题
                if current_section:
                    sections.append(current_section)
                
                current_section = ContentSection(
                    title=element.get_text(strip=True),
                    type="heading"
                )
                
            elif element.name in ['ul', 'ol']:  # 列表
                if current_section:
                    list_items = []
                    for li in element.find_all('li'):
                        item_text = li.get_text(strip=True)
                        emphasis = [em.get_text(strip=True) for em in li.find_all(['strong', 'b'])]
                        list_items.append(ListItem(text=item_text, emphasis=emphasis))
                    
                    current_section.content = "\n".join([f"• {item.text}" for item in list_items])
                    current_section.type = "list"
                    sections.append(current_section)
                    current_section = None
                
            elif element.name == 'p':  # 段落
                text = element.get_text(strip=True)
                if text and not text.startswith('Planned for'):
                    if current_section:
                        current_section.content += f"\n{text}"
                    else:
                        current_section = ContentSection(content=text, type="text")
        
        # 添加最后一个段落
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """提取元数据"""
        metadata = {}
        
        # 提取文本统计信息
        plain_text = self.soup.get_text()
        metadata['total_characters'] = len(plain_text)
        metadata['total_words'] = len(plain_text.split())
        
        # 提取HTML结构信息
        metadata['has_workflow_id'] = bool(self.soup.find('div', {'data-type': 'hide'}))
        metadata['has_floating_buttons'] = bool(self.soup.find('div', {'id': re.compile(r'floating-buttons')}))
        
        # 提取段落数量
        paragraphs = self.soup.find_all('p')
        metadata['paragraph_count'] = len(paragraphs)
        
        # 提取标题数量
        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        metadata['heading_count'] = len(headings)
        
        # 提取列表数量
        lists = self.soup.find_all(['ul', 'ol'])
        metadata['list_count'] = len(lists)
        
        return metadata

def parse_html_content(html_text: str) -> ParsedContent:
    """便捷函数：解析HTML内容"""
    parser = HTMLParser()
    return parser.parse(html_text)

def extract_workflow_id_from_html(html_text: str) -> str:
    """便捷函数：从HTML中提取工作流ID"""
    parser = HTMLParser()
    parsed = parser.parse(html_text)
    return parsed.workflow_info.workflow_id

def extract_plain_text_from_html(html_text: str) -> str:
    """便捷函数：从HTML中提取纯文本"""
    parser = HTMLParser()
    parsed = parser.parse(html_text)
    return parsed.get_plain_text()

# 测试函数
def test_parser():
    """测试解析器"""
    # 测试HTML文本
    test_html = '''<div><div id="" class="w-full space-y-1"><div class="w-fit text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition cursor-pointer"><div class="w-full font-medium flex items-center justify-between gap-2 "> <div class="">Planned for 0 seconds</div> <div class="flex self-center translate-y-[1px]"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="3.5" stroke="currentColor" class="size-3.5"><path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5"></path></svg><!--<ChevronDown>--></div></div></div> </div><!--<Collapsible>--><p dir="auto">您好！我是一名政务助手，专门为用户提供政务、法规等方面的咨询和帮助。以下是我的简要介绍：<!--<MarkdownInlineTokens>--> </p><div class="my-2"></div><h3 dir="auto">功能概述<!--<MarkdownInlineTokens>--> </h3><ul dir="auto"><li class="text-start"> <strong>政务咨询<!--<MarkdownInlineTokens>--></strong>：提供关于政务流程、政策法规等方面的信息。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li><li class="text-start"> <strong>常识解答<!--<MarkdownInlineTokens>--></strong>：回答各类常识性问题，如历史、文化等。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li><li class="text-start"> <strong>非实时性信息<!--<MarkdownInlineTokens>--></strong>：根据内部知识库或预设规则，提供准确、简洁的回答。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li> </ul><div class="my-2"></div><h3 dir="auto">使用说明<!--<MarkdownInlineTokens>--> </h3><ul dir="auto"><li class="text-start"> <strong>非联网版本<!--<MarkdownInlineTokens>--></strong>：当前助手为非联网版本，无法获取实时信息。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li><li class="text-start"> <strong>建议<!--<MarkdownInlineTokens>--></strong>：如需获取最新信息，建议开启"联网搜索"功能。<!--<MarkdownInlineTokens>--><!--<MarkdownTokens>--></li> </ul><div class="my-2"></div><h3 dir="auto">联系方式<!--<MarkdownInlineTokens>--> </h3><p dir="auto">如有任何问题或需要进一步帮助，请随时联系我。我将竭诚为您服务！<!--<MarkdownInlineTokens>--> </p><div class="my-2"></div><p dir="auto">希望以上信息对您有所帮助！<!--<MarkdownInlineTokens>--> </p><div class="my-2"></div><div id="" class="w-full space-y-1"><div data-type="hide" style="display: none;"><div class="mb-1.5" slot="content"><p dir="auto">dd467b95-6b43-4331-848c-9aad9cf1e914<!--<MarkdownInlineTokens>--> </p><!--<MarkdownTokens>--> </div></div> </div><!--<Collapsible>--><!--<MarkdownTokens>--><!--<Markdown>--></div>'''
    
    print("🧪 测试HTML解析器...")
    
    # 解析HTML
    parsed = parse_html_content(test_html)
    
    print(f"📋 工作流ID: {parsed.get_workflow_id()}")
    print(f"⏱️  计划时间: {parsed.workflow_info.planned_time}")
    print(f"📊 段落数量: {len(parsed.sections)}")
    print(f"📈 元数据: {parsed.metadata}")
    
    print("\n📝 解析后的段落:")
    for i, section in enumerate(parsed.sections, 1):
        print(f"\n{i}. {section.title or '无标题段落'}")
        print(f"   类型: {section.type}")
        print(f"   内容: {section.content[:100]}...")
    
    print(f"\n📄 纯文本内容:")
    print(parsed.get_plain_text())
    
    print(f"\n🔧 JSON格式:")
    print(parsed.to_json())
    
    return parsed

if __name__ == "__main__":
    test_parser() 