# HTML解析器使用说明

## 📋 概述

HTML解析器用于解析置信检查中的HTML文本，将其转换为结构化的实体，方便进行后续的置信度分析。

## 🎯 主要功能

- ✅ **HTML解析**: 解析复杂的HTML结构
- ✅ **工作流ID提取**: 自动提取隐藏的工作流ID
- ✅ **纯文本提取**: 去除HTML标签，获取纯文本内容
- ✅ **结构化分析**: 将内容分解为段落、标题、列表等
- ✅ **元数据统计**: 提供字符数、词数、段落数等统计信息

## 📁 文件结构

```
backend/
├── html_parser.py                    # HTML解析器主文件
├── confidence_with_html_parser.py    # 结合置信检查的示例
├── test_example.py                   # 测试示例
└── HTML_PARSER_USAGE.md             # 使用说明文档
```

## 🚀 快速开始

### 1. 基本使用

```python
from html_parser import parse_html_content, extract_workflow_id_from_html, extract_plain_text_from_html

# 解析HTML内容
html_text = "你的HTML文本"
parsed_content = parse_html_content(html_text)

# 获取工作流ID
workflow_id = parsed_content.get_workflow_id()

# 获取纯文本
plain_text = parsed_content.get_plain_text()

# 查看解析结果
print(f"工作流ID: {workflow_id}")
print(f"纯文本长度: {len(plain_text)} 字符")
```

### 2. 便捷函数

```python
# 快速提取工作流ID
workflow_id = extract_workflow_id_from_html(html_text)

# 快速提取纯文本
plain_text = extract_plain_text_from_html(html_text)
```

### 3. 完整分析

```python
# 获取完整的结构化信息
parsed_content = parse_html_content(html_text)

# 查看工作流信息
print(f"工作流ID: {parsed_content.workflow_info.workflow_id}")
print(f"计划时间: {parsed_content.workflow_info.planned_time}")

# 查看内容段落
for i, section in enumerate(parsed_content.sections, 1):
    print(f"{i}. {section.title or '无标题段落'}")
    print(f"   类型: {section.type}")
    print(f"   内容: {section.content[:100]}...")

# 查看元数据
print(f"字符数: {parsed_content.metadata['total_characters']}")
print(f"词数: {parsed_content.metadata['total_words']}")
print(f"段落数: {parsed_content.metadata['paragraph_count']}")
```

## 📊 数据结构

### ParsedContent 类

```python
@dataclass
class ParsedContent:
    workflow_info: WorkflowInfo      # 工作流信息
    sections: List[ContentSection]   # 内容段落列表
    raw_text: str                    # 原始HTML文本
    metadata: Dict[str, Any]         # 元数据统计
```

### WorkflowInfo 类

```python
@dataclass
class WorkflowInfo:
    workflow_id: str    # 工作流ID
    planned_time: str   # 计划时间
```

### ContentSection 类

```python
@dataclass
class ContentSection:
    title: str    # 段落标题
    content: str  # 段落内容
    type: str     # 段落类型 (text, list, heading)
```

## 🔧 主要方法

### ParsedContent 方法

- `get_plain_text()`: 获取纯文本内容
- `get_workflow_id()`: 获取工作流ID
- `get_section_by_title(title)`: 根据标题获取段落
- `to_dict()`: 转换为字典格式
- `to_json()`: 转换为JSON格式

### HTMLParser 方法

- `parse(html_text)`: 解析HTML文本
- `_extract_workflow_info()`: 提取工作流信息
- `_extract_sections()`: 提取内容段落
- `_extract_metadata()`: 提取元数据

## 📈 使用示例

### 示例1: 基本解析

```python
from html_parser import parse_html_content

html_text = "你的HTML文本"
parsed = parse_html_content(html_text)

print(f"工作流ID: {parsed.get_workflow_id()}")
print(f"纯文本: {parsed.get_plain_text()}")
```

### 示例2: 置信检查集成

```python
import asyncio
from html_parser import parse_html_content
from open_webui.routers.confidence import simulate_confidence_check

async def confidence_check_with_parsing(html_text):
    # 解析HTML
    parsed = parse_html_content(html_text)
    
    # 获取纯文本和工作流ID
    plain_text = parsed.get_plain_text()
    workflow_id = parsed.get_workflow_id()
    
    # 进行置信检查
    results = []
    async for chunk in simulate_confidence_check(plain_text, workflow_id):
        results.append(chunk)
    
    return {
        "parsed_content": parsed,
        "confidence_results": results
    }
```

### 示例3: 内容分析

```python
from html_parser import parse_html_content

def analyze_content(html_text):
    parsed = parse_html_content(html_text)
    
    analysis = {
        "workflow_id": parsed.get_workflow_id(),
        "text_length": len(parsed.get_plain_text()),
        "sections": len(parsed.sections),
        "structure": parsed.metadata
    }
    
    # 分析段落类型
    type_counts = {}
    for section in parsed.sections:
        type_counts[section.type] = type_counts.get(section.type, 0) + 1
    
    analysis["section_types"] = type_counts
    
    return analysis
```

## 🎯 置信检查集成

### 在置信检查中使用

```python
# 在置信检查按钮点击事件中
async def confidence_check_handler(html_text):
    # 1. 解析HTML
    parsed = parse_html_content(html_text)
    
    # 2. 提取必要信息
    text = parsed.get_plain_text()
    workflow_id = parsed.get_workflow_id()
    
    # 3. 验证信息
    if not text.strip() or not workflow_id:
        toast.error('无法获取响应内容或工作流ID')
        return
    
    # 4. 进行置信检查
    try:
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 5. 处理结果
        # ... 处理置信检查结果
        
    except Exception as error:
        toast.error(f'置信检查失败: {error}')
```

## 📊 输出格式

### JSON格式输出

```python
parsed = parse_html_content(html_text)
json_output = parsed.to_json()

# 输出示例:
{
  "workflow_info": {
    "workflow_id": "dd467b95-6b43-4331-848c-9aad9cf1e914",
    "planned_time": "Planned for 0 seconds"
  },
  "sections": [
    {
      "title": "",
      "content": "您好！我是一名政务助手...",
      "type": "text"
    },
    {
      "title": "功能概述",
      "content": "• 政务咨询：提供关于政务流程...",
      "type": "list"
    }
  ],
  "metadata": {
    "total_characters": 306,
    "total_words": 16,
    "paragraph_count": 4,
    "heading_count": 3,
    "list_count": 2
  }
}
```

## 🔍 解析能力

### 支持的HTML元素

- ✅ **段落**: `<p>` 标签
- ✅ **标题**: `<h1>`, `<h2>`, `<h3>`, `<h4>`, `<h5>`, `<h6>` 标签
- ✅ **列表**: `<ul>`, `<ol>`, `<li>` 标签
- ✅ **强调**: `<strong>`, `<b>` 标签
- ✅ **隐藏内容**: `data-type="hide"` 属性
- ✅ **工作流ID**: UUID格式的ID提取

### 特殊处理

- 🔍 **工作流ID提取**: 自动从隐藏的div中提取UUID格式的工作流ID
- 📝 **纯文本转换**: 去除所有HTML标签，保留文本内容
- 📊 **结构分析**: 识别段落、标题、列表等结构
- 📈 **统计信息**: 提供字符数、词数、段落数等统计

## 🛠️ 错误处理

### 常见错误及解决方案

1. **工作流ID未找到**
   ```python
   workflow_id = parsed.get_workflow_id()
   if not workflow_id:
       print("未找到工作流ID，请检查HTML结构")
   ```

2. **HTML解析失败**
   ```python
   try:
       parsed = parse_html_content(html_text)
   except Exception as e:
       print(f"HTML解析失败: {e}")
   ```

3. **空内容处理**
   ```python
   plain_text = parsed.get_plain_text()
   if not plain_text.strip():
       print("提取的文本内容为空")
   ```

## 📈 性能优化

### 建议

1. **缓存解析结果**: 对于重复的HTML内容，可以缓存解析结果
2. **批量处理**: 如果需要处理多个HTML，可以批量解析
3. **异步处理**: 对于大量数据，使用异步处理

### 示例

```python
import asyncio
from html_parser import parse_html_content

async def batch_parse_html(html_list):
    results = []
    for html in html_list:
        parsed = parse_html_content(html)
        results.append(parsed)
        await asyncio.sleep(0.1)  # 避免阻塞
    return results
```

## 🎉 总结

HTML解析器提供了完整的HTML内容解析功能，能够：

- ✅ 自动提取工作流ID
- ✅ 转换为纯文本格式
- ✅ 分析内容结构
- ✅ 提供统计信息
- ✅ 支持多种输出格式
- ✅ 易于集成到置信检查流程中

这使得置信检查功能能够更好地处理复杂的HTML内容，提供更准确的分析结果。 