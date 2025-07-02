import pytest
import asyncio
import json
from unittest.mock import patch, AsyncMock
from open_webui.routers.confidence import simulate_confidence_check, ConfidenceCheckRequest, confidence_check, confidence_status
from fastapi.testclient import TestClient
from fastapi import FastAPI

# 创建测试应用
app = FastAPI()
app.include_router(confidence_check.router)
client = TestClient(app)

class TestSimulateConfidenceCheck:
    """测试simulate_confidence_check方法"""
    
    @pytest.mark.asyncio
    async def test_simulate_confidence_check_basic(self):
        """测试基本的置信检查功能"""
        text = "这是一个测试文本，用于验证置信检查功能是否正常工作。"
        workflow_id = "test_workflow_123"
        
        # 收集所有输出
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 验证输出不为空
        assert len(results) > 0
        
        # 验证输出格式
        for result in results:
            assert result.startswith("data: ")
            if result != "data: [DONE]\n\n":
                # 解析JSON数据
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                assert "choices" in data
                assert len(data["choices"]) > 0
                assert "delta" in data["choices"][0]
                assert "content" in data["choices"][0]["delta"]
    
    @pytest.mark.asyncio
    async def test_simulate_confidence_check_empty_text(self):
        """测试空文本的处理"""
        text = ""
        workflow_id = "test_workflow_123"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 即使空文本也应该有输出
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_simulate_confidence_check_long_text(self):
        """测试长文本的处理"""
        text = "这是一个很长的测试文本。" * 100  # 创建长文本
        workflow_id = "test_workflow_456"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 验证长文本也能正常处理
        assert len(results) > 0
        
        # 检查是否包含置信度分析
        content = ""
        for result in results:
            if result != "data: [DONE]\n\n":
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                content += data["choices"][0]["delta"]["content"]
        
        # 验证包含关键信息
        assert "智能置信度分析报告" in content
        assert "置信度评分" in content
        assert workflow_id in content
    
    @pytest.mark.asyncio
    async def test_simulate_confidence_check_special_workflow_id(self):
        """测试特殊字符的工作流ID"""
        text = "测试文本"
        workflow_id = "workflow_with_special_chars_!@#$%^&*()"
        
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
    async def test_simulate_confidence_check_progress_steps(self):
        """测试进度步骤的输出"""
        text = "测试进度步骤"
        workflow_id = "test_progress"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 验证包含进度信息
        content = ""
        for result in results:
            if result != "data: [DONE]\n\n":
                json_str = result.replace("data: ", "").strip()
                data = json.loads(json_str)
                content += data["choices"][0]["delta"]["content"]
        
        # 检查是否包含预期的步骤
        expected_steps = [
            "开始分析工作流",
            "正在提取关键信息",
            "正在评估信息准确性",
            "正在检查逻辑一致性",
            "正在验证事实依据",
            "正在生成置信度报告"
        ]
        
        for step in expected_steps:
            assert step in content
    
    @pytest.mark.asyncio
    async def test_simulate_confidence_check_completion_signal(self):
        """测试完成信号"""
        text = "测试完成信号"
        workflow_id = "test_completion"
        
        results = []
        async for chunk in simulate_confidence_check(text, workflow_id):
            results.append(chunk)
        
        # 验证最后有完成信号
        assert results[-1] == "data: [DONE]\n\n"
    
    @pytest.mark.asyncio
    async def test_simulate_confidence_check_confidence_score_calculation(self):
        """测试置信度分数计算"""
        # 测试短文本
        short_text = "短文本"
        results_short = []
        async for chunk in simulate_confidence_check(short_text, "test_short"):
            results_short.append(chunk)
        
        # 测试长文本
        long_text = "这是一个很长的文本。" * 50
        results_long = []
        async for chunk in simulate_confidence_check(long_text, "test_long"):
            results_long.append(chunk)
        
        # 提取置信度分数
        def extract_confidence_score(results):
            content = ""
            for result in results:
                if result != "data: [DONE]\n\n":
                    json_str = result.replace("data: ", "").strip()
                    data = json.loads(json_str)
                    content += data["choices"][0]["delta"]["content"]
            
            # 查找置信度分数
            import re
            match = re.search(r'置信度评分: ([\d.]+)%', content)
            return float(match.group(1)) if match else 0
        
        short_score = extract_confidence_score(results_short)
        long_score = extract_confidence_score(results_long)
        
        # 验证长文本的置信度应该更高（根据算法逻辑）
        assert long_score >= short_score

class TestConfidenceCheckAPI:
    """测试置信检查API端点"""
    
    def test_confidence_check_endpoint_success(self):
        """测试成功的置信检查请求"""
        request_data = {
            "text": "这是一个测试文本",
            "workflowId": "test_workflow_123"
        }
        
        response = client.post("/api/confidence/check", json=request_data)
        
        # 验证响应状态码
        assert response.status_code == 200
        
        # 验证响应内容类型
        assert response.headers["content-type"] == "text/plain"
        assert "text/event-stream" in response.headers.get("content-type", "")
    
    def test_confidence_check_endpoint_empty_text(self):
        """测试空文本的错误处理"""
        request_data = {
            "text": "",
            "workflowId": "test_workflow_123"
        }
        
        response = client.post("/api/confidence/check", json=request_data)
        
        # 验证错误响应
        assert response.status_code == 400
        assert "文本内容不能为空" in response.json()["detail"]
    
    def test_confidence_check_endpoint_empty_workflow_id(self):
        """测试空工作流ID的错误处理"""
        request_data = {
            "text": "测试文本",
            "workflowId": ""
        }
        
        response = client.post("/api/confidence/check", json=request_data)
        
        # 验证错误响应
        assert response.status_code == 400
        assert "工作流ID不能为空" in response.json()["detail"]
    
    def test_confidence_status_endpoint(self):
        """测试状态端点"""
        response = client.get("/api/confidence/status")
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "available"
        assert data["version"] == "1.0.0"
        assert "置信度检查服务正常运行" in data["description"]

class TestConfidenceCheckRequest:
    """测试请求模型"""
    
    def test_confidence_check_request_valid(self):
        """测试有效的请求数据"""
        request_data = {
            "text": "测试文本",
            "workflowId": "test_workflow_123"
        }
        
        request = ConfidenceCheckRequest(**request_data)
        assert request.text == "测试文本"
        assert request.workflowId == "test_workflow_123"
    
    def test_confidence_check_request_missing_fields(self):
        """测试缺少字段的情况"""
        with pytest.raises(ValueError):
            ConfidenceCheckRequest(text="测试文本")
        
        with pytest.raises(ValueError):
            ConfidenceCheckRequest(workflowId="test_workflow_123")

if __name__ == "__main__":
    pytest.main([__file__]) 