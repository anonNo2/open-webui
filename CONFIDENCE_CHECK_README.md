# 置信检查功能

这是一个为Open WebUI添加的置信检查功能，可以对AI响应进行置信度分析。

## 功能特性

- **流式响应**: 支持实时流式输出分析结果
- **异步处理**: 后端异步处理，不会阻塞用户界面
- **详细分析**: 提供置信度评分、信息完整性、逻辑一致性等多维度分析
- **用户友好**: 直观的UI界面，实时显示分析进度

## 文件结构

### 前端文件
- `src/lib/apis/confidence.ts` - 置信检查API调用方法
- `src/lib/components/chat/Messages/ResponseMessage.svelte` - 置信检查按钮和UI

### 后端文件
- `backend/open_webui/routers/confidence.py` - 置信检查API路由
- `backend/open_webui/main.py` - 主应用路由注册

### 测试文件
- `test_confidence.py` - API测试脚本

## API接口

### 1. 置信检查接口

**POST** `/api/confidence/check`

**请求体:**
```json
{
  "text": "要分析的文本内容",
  "workflowId": "工作流ID"
}
```

**响应格式:**
```
data: {"choices": [{"delta": {"content": "分析内容"}}]}

data: [DONE]
```

### 2. 服务状态接口

**GET** `/api/confidence/status`

**响应:**
```json
{
  "status": "available",
  "version": "1.0.0",
  "description": "置信度检查服务正常运行"
}
```

## 使用方法

### 1. 启动后端服务

确保后端服务正在运行，置信检查路由会自动注册。

### 2. 前端集成

置信检查按钮已经集成到消息响应组件中，用户点击"置信检查"按钮即可触发分析。

### 3. 测试API

运行测试脚本：
```bash
python test_confidence.py
```

## 实现细节

### 前端实现

1. **API调用**: 使用`confidenceCheckStream`函数进行流式API调用
2. **UI更新**: 实时更新分析结果到页面
3. **错误处理**: 完善的错误处理和用户提示
4. **加载状态**: 显示加载动画和进度

### 后端实现

1. **异步处理**: 使用`asyncio`进行异步处理
2. **流式响应**: 使用`StreamingResponse`返回流式数据
3. **模拟分析**: 当前使用模拟数据，可以替换为真实的AI分析
4. **错误处理**: 完善的输入验证和错误处理

## 自定义分析逻辑

在`backend/open_webui/routers/confidence.py`中的`simulate_confidence_check`函数可以替换为真实的置信度分析逻辑：

```python
async def simulate_confidence_check(text: str, workflow_id: str) -> AsyncGenerator[str, None]:
    # 这里可以集成真实的AI模型进行置信度分析
    # 例如：调用OpenAI API、本地模型等
    
    # 示例：调用AI模型进行分析
    # result = await ai_model.analyze_confidence(text, workflow_id)
    
    # 返回分析结果
    yield f"data: {json.dumps({'choices': [{'delta': {'content': result}}]})}\n\n"
```

## 配置选项

可以在配置文件中添加置信检查相关的配置：

```python
# 置信检查配置
CONFIDENCE_CHECK_ENABLED = True
CONFIDENCE_CHECK_MODEL = "gpt-4"
CONFIDENCE_CHECK_TIMEOUT = 30
```

## 注意事项

1. 确保后端服务正常运行
2. 检查网络连接和API端点
3. 注意API调用的频率限制
4. 在生产环境中替换模拟分析为真实AI分析

## 故障排除

### 常见问题

1. **API调用失败**: 检查后端服务是否启动，端口是否正确
2. **流式响应中断**: 检查网络连接和超时设置
3. **UI不更新**: 检查前端JavaScript错误和DOM操作

### 调试方法

1. 查看浏览器控制台错误信息
2. 检查后端日志输出
3. 使用测试脚本验证API功能
4. 检查网络请求和响应

## 扩展功能

可以考虑添加以下扩展功能：

1. **批量分析**: 支持批量分析多个响应
2. **历史记录**: 保存分析历史记录
3. **自定义指标**: 允许用户自定义置信度指标
4. **导出报告**: 支持导出分析报告
5. **集成其他模型**: 支持多种AI模型进行分析 