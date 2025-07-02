# 置信检查测试说明

## 概述

本目录包含针对 `simulate_confidence_check` 方法的单元测试。这些测试确保置信检查功能能够正常工作，包括流式输出、错误处理、边界情况等。

## 测试文件

- `test_simulate_confidence_check.py` - 专门测试 `simulate_confidence_check` 方法
- `test_confidence.py` - 完整的置信检查API测试（包含API端点测试）

## 运行测试

### 方法1: 使用pytest直接运行

```bash
# 运行所有置信检查测试
pytest tests/test_simulate_confidence_check.py -v

# 运行特定测试
pytest tests/test_simulate_confidence_check.py::TestSimulateConfidenceCheck::test_basic_functionality -v

# 运行包含特定关键词的测试
pytest tests/test_simulate_confidence_check.py -k "basic" -v
```

### 方法2: 使用测试脚本

```bash
# 运行所有测试
python run_confidence_tests.py

# 运行特定测试
python run_confidence_tests.py "test_basic_functionality"
```

### 方法3: 使用Python模块方式

```bash
# 在backend目录下运行
python -m pytest tests/test_simulate_confidence_check.py -v
```

## 测试覆盖范围

### 基本功能测试
- ✅ 基本功能验证
- ✅ 输出结构验证
- ✅ 流式输出行为

### 进度步骤测试
- ✅ 验证所有预期的进度步骤
- ✅ 步骤顺序和内容正确性

### 置信度计算测试
- ✅ 短文本和长文本的置信度计算
- ✅ 分数范围验证（60-95%）
- ✅ 长文本通常比短文本置信度更高

### 边界情况测试
- ✅ 空文本处理
- ✅ 特殊字符工作流ID
- ✅ 完成信号验证

### 输出内容测试
- ✅ 工作流ID在输出中
- ✅ 分析报告结构完整性
- ✅ 必要部分的包含验证

## 测试用例说明

### 1. test_basic_functionality
验证方法的基本功能，确保有输出且格式正确。

### 2. test_output_structure
验证JSON输出结构的正确性，包括choices、delta、content等字段。

### 3. test_progress_steps
验证所有预期的进度步骤都包含在输出中：
- 开始分析工作流
- 正在提取关键信息
- 正在评估信息准确性
- 正在检查逻辑一致性
- 正在验证事实依据
- 正在生成置信度报告

### 4. test_confidence_score_calculation
验证置信度分数计算的逻辑：
- 短文本和长文本的分数差异
- 分数在合理范围内（60-95%）
- 长文本通常比短文本置信度更高

### 5. test_workflow_id_in_output
验证工作流ID正确显示在输出中。

### 6. test_completion_signal
验证流式输出最后有正确的完成信号 `"data: [DONE]\n\n"`。

### 7. test_empty_text_handling
验证空文本的处理，确保即使空文本也能生成分析报告。

### 8. test_special_characters_in_workflow_id
验证包含特殊字符的工作流ID能正确处理。

### 9. test_analysis_report_structure
验证分析报告包含所有必要部分：
- 智能置信度分析报告
- 基本信息
- 置信度评分
- 详细分析
- 智能建议
- 分析完成时间

### 10. test_streaming_behavior
验证流式输出的行为，确保有多个chunk且格式正确。

## 测试环境要求

- Python 3.8+
- pytest
- pytest-asyncio
- open_webui 模块

## 安装依赖

```bash
pip install pytest pytest-asyncio
```

## 故障排除

### 常见问题

1. **导入错误**: 确保在正确的目录下运行测试，或者将backend目录添加到Python路径。

2. **异步测试失败**: 确保安装了 `pytest-asyncio` 插件。

3. **模块找不到**: 检查 `open_webui.routers.confidence` 模块是否正确安装。

### 调试技巧

```bash
# 详细输出
pytest tests/test_simulate_confidence_check.py -v -s

# 只运行失败的测试
pytest tests/test_simulate_confidence_check.py --lf

# 显示最慢的测试
pytest tests/test_simulate_confidence_check.py --durations=10
```

## 扩展测试

如果需要添加新的测试用例，请遵循以下模式：

```python
@pytest.mark.asyncio
async def test_new_feature(self):
    """测试新功能"""
    # 准备测试数据
    text = "测试文本"
    workflow_id = "test_workflow"
    
    # 执行测试
    results = []
    async for chunk in simulate_confidence_check(text, workflow_id):
        results.append(chunk)
    
    # 验证结果
    assert len(results) > 0
    # 添加更多断言...
```

## 持续集成

这些测试可以集成到CI/CD流程中，确保代码质量：

```yaml
# GitHub Actions 示例
- name: Run Confidence Tests
  run: |
    cd backend
    python -m pytest tests/test_simulate_confidence_check.py -v
``` 