import pytest
import asyncio
import json
import re
from open_webui.routers.confidence import simulate_confidence_check

class TestSimulateConfidenceCheck:
    """测试simulate_confidence_check方法"""
    
    @pytest.mark.asyncio
    async def test_basic_functionality(self):
        """测试基本功能"""
        text = "这是一个测试文本"
        workflow_id = "test_workflow_123"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 验证有输出
        assert len(results) > 0
        
        # 验证输出格式
        for result in results:
            assert result.startswith("data: ")
    
    @pytest.mark.asyncio
    async def test_output_structure(self):
        """测试输出结构"""
        text = "测试输出结构"
        workflow_id = "test_structure"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 验证JSON结构
        for result in results:
            if result != "data: [DONE]\n\n":
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                
                # 验证数据结构
                assert "choices" in data
                assert len(data["choices"]) > 0
                assert "delta" in data["choices"][0]
                assert "content" in data["choices"][0]["delta"]
    
    @pytest.mark.asyncio
    async def test_progress_steps(self):
        """测试进度步骤"""
        text = "测试进度"
        workflow_id = "test_progress"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 提取所有内容
        content = ""
        for result in results:
            if result != "data: [DONE]\n\n":
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                content += data["choices"][0]["delta"]["content"]
        
        # 验证包含预期的步骤
        expected_steps = [
            "开始分析工作流",
            "正在提取关键信息", 
            "正在评估信息准确性",
            "正在检查逻辑一致性",
            "正在验证事实依据",
            "正在生成置信度报告"
        ]
        
        for step in expected_steps:
            assert step in content, f"缺少步骤: {step}"
    
    @pytest.mark.asyncio
    async def test_confidence_score_calculation(self):
        """测试置信度分数计算"""
        # 测试短文本
        short_text = "短"
        results_short = []
        async for chunk in simulate_confidence_check(short_text, "test_short"):
            results_short.append(chunk)
        
        # 测试长文本
        long_text = "这是一个很长的文本。" * 50
        results_long = []
        async for chunk in simulate_confidence_check(long_text, "test_long"):
            results_long.append(chunk)
        
        # 提取置信度分数
        def extract_score(results):
            content = ""
            for result in results:
                if result != "data: [DONE]\n\n":
                    json_str = result.replace("data: ", "").strip()
                    data = json.loads(json_str)
                    content += data["choices"][0]["delta"]["content"]
            
            match = re.search(r'置信度评分: ([\d.]+)%', content)
            return float(match.group(1)) if match else 0
        
        short_score = extract_score(results_short)
        long_score = extract_score(results_long)
        
        # 验证分数在合理范围内
        assert 60 <= short_score <= 95
        assert 60 <= long_score <= 95
        
        # 验证长文本分数通常更高
        assert long_score >= short_score
    
    @pytest.mark.asyncio
    async def test_workflow_id_in_output(self):
        """测试工作流ID在输出中"""
        text = "测试工作流ID"
        workflow_id = "special_workflow_123"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 提取内容
        content = ""
        for result in results:
            if result != "data: [DONE]\n\n":
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                content += data["choices"][0]["delta"]["content"]
        
        # 验证工作流ID在输出中
        assert workflow_id in content
    
    @pytest.mark.asyncio
    async def test_completion_signal(self):
        """测试完成信号"""
        text = "测试完成"
        workflow_id = "test_completion"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 验证最后有完成信号
        assert results[-1] == "data: [DONE]\n\n"
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self):
        """测试空文本处理"""
        text = ""
        workflow_id = "test_empty"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 即使空文本也应该有输出
        assert len(results) > 0
        
        # 验证包含分析报告
        content = ""
        for result in results:
            if result != "data: [DONE]\n\n":
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                content += data["choices"][0]["delta"]["content"]
        
        assert "智能置信度分析报告" in content
    
    @pytest.mark.asyncio
    async def test_special_characters_in_workflow_id(self):
        """测试工作流ID中的特殊字符"""
        text = "测试特殊字符"
        workflow_id = "workflow!@#$%^&*()"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 验证特殊字符能正确处理
        assert len(results) > 0
        
        content = ""
        for result in results:
            if result != "data: [DONE]\n\n":
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                content += data["choices"][0]["delta"]["content"]
        
        assert workflow_id in content
    
    @pytest.mark.asyncio
    async def test_analysis_report_structure(self):
        """测试分析报告结构"""
        text = "测试分析报告结构"
        workflow_id = "test_report"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 提取完整内容
        content = ""
        for result in results:
            if result != "data: [DONE]\n\n":
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                content += data["choices"][0]["delta"]["content"]
        
        # 验证报告包含必要部分
        required_sections = [
            "智能置信度分析报告",
            "基本信息",
            "置信度评分",
            "详细分析",
            "智能建议",
            "分析完成时间"
        ]
        
        for section in required_sections:
            assert section in content, f"缺少部分: {section}"
    
    @pytest.mark.asyncio
    async def test_streaming_behavior(self):
        """测试流式输出行为"""
        text = "测试流式输出"
        workflow_id = "test_streaming"
        
        chunk_count = 0
        async for chunk in simulate_confidence_check(text, workflow_id):
            chunk_count += 1
            # 验证每个chunk都是字符串
            assert isinstance(chunk, str)
            # 验证格式
            assert chunk.startswith("data: ")
        
        # 验证有多个chunk（流式输出）
        assert chunk_count > 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 