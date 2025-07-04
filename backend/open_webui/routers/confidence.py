import asyncio
import json
import time
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from open_webui.utils.auth import get_verified_user
from open_webui.models.users import UserModel
from open_webui.utils.redis import get_redis_connection
from open_webui.env import REDIS_URL, REDIS_SENTINEL_HOSTS, REDIS_SENTINEL_PORT,CONFIDENCE_CHECK_URL,CONFIDENCE_CHECK_TOKEN
from open_webui.utils.redis import get_sentinels_from_env
from open_webui.utils.reference_extractor import ReferenceExtractor

import httpx

router = APIRouter(prefix="/api/confidence", tags=["confidence"])

class ConfidenceCheckRequest(BaseModel):
    text: str
    workflowId: str

class ConfidenceCheckResponse(BaseModel):
    done: bool
    value: str
    error: str = None


def get_analysis_result(workflow_id,results):
    
    all_outputs = [i['data']['outputs'] for i in results]
        
    items_length = len(all_outputs)
    right_items_length = sum([1 for i in all_outputs if i['confidence_results']['status'] == 'yes'])
    error_items = [i for i in all_outputs if i['confidence_results']['status'] == 'no']
    error_items_content = [[i["content"].replace("#",""),i["confidence_results"]["reason"],i["ref_ids"]] for i in error_items]
    error_items_content = '\n\n'.join([
        f'<div style="display:flex; gap:20px; margin:10px 0" class="warning-item">\n'
        f'<div style="flex:1; border:1px solid #ffa39e; background:#fff2f0; padding:10px; border-radius:4px">\n'
        f'<div style="font-weight:bold">内容：</div><span class="warning-content">\n{i[0]}\n</span>'
        f'</div>\n'
        f'<div style="flex:1; border:1px solid #91caff; background:#e6f4ff; padding:10px; border-radius:4px">\n' 
        f'<div style="font-weight:bold">参考范围：</div><span class="warning-area">{i[2]}</span>\n'
        f'<div style="font-weight:bold">存疑原因：</div><span class="warning-reason">\n{i[1]}</span>\n'
        f'</div>\n'
        f'</div>' for i in error_items_content])
    error_items_content = error_items_content if error_items_content else '无存疑事实点'





    correct_items = [i for i in all_outputs if i['confidence_results']['status'] == 'yes']
    correct_items_content = [[i["content"].replace("#",""),i["confidence_results"]["reason"],i["ref_ids"]] for i in correct_items]
    correct_items_content = '\n\n'.join([
        f'<div style="display:flex; gap:20px; margin:10px 0" class="correct-item">\n'
        f'<div style="flex:1; border:1px solid #b7eb8f; background:#f6ffed; padding:10px; border-radius:4px">\n'
        f'<div style="font-weight:bold">内容：</div><span class="correct-content">\n{i[0]}\n</span>'
        f'</div>\n'
        f'<div style="flex:1; border:1px solid #95de64; background:#f6ffed; padding:10px; border-radius:4px">\n' 
        f'<div style="font-weight:bold">参考范围：</div><span class="correct-area">{i[2]}</span>\n'
        f'<div style="font-weight:bold">论证：</div><span class="correct-reason">\n{i[1]}\n</span>'
        f'</div>\n'
        f'</div>' for i in correct_items_content])
    correct_items_content = correct_items_content if correct_items_content else '无正确事实点'    
    confidence_score = right_items_length * 1.0 / items_length * 100
    confidence_score = min(100, max(0, confidence_score))
    analysis_result = f"""
🎯 **智能置信度分析报告**

📋 **基本信息**
• 工作流ID: `{workflow_id}`
• 关键事实点数量: {items_length} 
• 可信事实点数量: {right_items_length} 个词

📊 **置信度评分: {confidence_score:.1f}%**

🔍 **存疑事实点**

{error_items_content}

🔍 **正确事实点**

{correct_items_content}

🎉 **分析完成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
    """
    return analysis_result




def step_status(index,workflow_id):
    steps = [
        f"🚀 开始分析工作流 {workflow_id} 的响应内容...",
        "🔍 正在提取关键信息...",
        "⚡ 正在评估信息关联性...",
        "📊 正在生成置信度报告..."
    ]
    step = steps[index]
    

    # 模拟处理进度
    progress = (index + 1) / len(steps) * 100
    progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
    return f"data: {json.dumps({'choices': [{'delta': {'content': step + chr(10)}}]})}\n\ndata: {json.dumps({'choices': [{'delta': {'content': f'📈 进度: {progress_bar} {progress:.1f}%'+ chr(10)}}]})}\n\n"

async def simulate_confidence_check(text: str, workflow_id: str) -> AsyncGenerator[str, None]:
    """
    模拟置信检查过程，这是一个耗时的异步操作
    在实际应用中，这里可能是调用AI模型进行置信度分析
    """
    workflow_id = workflow_id.strip()
    ref_search_data = {}
    reference_pairs = []
    # 从 Redis 中读取数据
    # 获取 Redis 连接配置
    redis_sentinels = get_sentinels_from_env(REDIS_SENTINEL_HOSTS, REDIS_SENTINEL_PORT)
    redis_conn = get_redis_connection(REDIS_URL, redis_sentinels, decode_responses=True)
    analysis_redis_key = f"analysis_:{workflow_id}"

    result = redis_conn.get(analysis_redis_key)
    if result:
        results = json.loads(result)
        analysis_result = get_analysis_result(workflow_id,results)
        yield f"data: {json.dumps({'choices': [{'delta': {'content': f'🎯 key: {workflow_id} 已进行过置信度检查，结果如下：' + chr(10)}}]})}\n\n"
        yield f"data: {json.dumps({'choices': [{'delta': {'content': analysis_result + chr(10)}}]})}\n\n"
        yield "data: [DONE]\n\n"
        return


    try:
        
        # 从 Redis 中读取 name 为 "search"，key 为 workflow_id 的数据
        search_redis_key = f"search_:{workflow_id}"
        content_redis_key = f"content_:{workflow_id}"
        time_redis_key = f"time_:{workflow_id}"
        title_redis_key = f"title_:{workflow_id}"
        search_data = redis_conn.get(search_redis_key)
        content_data = redis_conn.get(content_redis_key)
        content_time = redis_conn.get(time_redis_key)
        title_data = redis_conn.get(title_redis_key)

        if not search_data or not content_data or not content_time or not title_data:
            yield f"data: {json.dumps({'choices': [{'delta': {'content': f'[ERROR]⚠️ 未找到 key: {workflow_id} 的数据(仅可对生成时间一天内的联网参考内容进行置信度检查)' + chr(10)}}]})}\n\n"
            yield "data: [DONE]\n\n"
            return

        pure_results = content_data.split('</think>')[1]

        
        
        if search_data and content_data:
            # 发送从 Redis 读取到的数据
            ref_search_data = {i['id']:i for i in json.loads(search_data)}
            
        else:
            # 如果没有找到数据，发送提示信息
            yield f"data: {json.dumps({'choices': [{'delta': {'content': f'[ERROR]⚠️ 未找到 key: {workflow_id} 的数据(仅可对生成时间一天内的联网参考内容进行置信度检查)' + chr(10)}}]})}\n\n"
             # 发送完成信号
            yield "data: [DONE]\n\n"
            return
            
    except Exception as e:
        # 如果 Redis 操作失败，发送错误信息但继续执行
        yield f"data: {json.dumps({'choices': [{'delta': {'content': f'[ERROR]❌ Redis 读取失败: {str(e)}' + chr(10)}}]})}\n\n"
         # 发送完成信号
        yield "data: [DONE]\n\n"
        return
    
    
    

        
    # 1、开始分析
    yield step_status(0,workflow_id)
    
    extractor = ReferenceExtractor()
    reference_pairs = extractor.extract_reference_pairs(pure_results)
    print(f"reference_pairs: {reference_pairs}")

    
    yield step_status(1,workflow_id)

    # 准备并行请求
    async def make_request(sentence, ref_ids):
        ref_items = [{k: ref_search_data[i][k] for k in ('id', 'title', 'content', 'publishedDate')} for i in ref_ids if i in ref_search_data]
        ref_content = json.dumps(ref_items, ensure_ascii=False)
        inputs_dict = {
            "content": sentence,
            "content_time":content_time,
            "reference": ref_content,
            "main_title": title_data,
            "ref_ids": json.dumps(ref_ids,ensure_ascii=False)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                CONFIDENCE_CHECK_URL,
                headers={
                    'Authorization': f'Bearer {CONFIDENCE_CHECK_TOKEN}',
                    'Content-Type': 'application/json'
                },
                json={
                    "inputs": inputs_dict,
                    "response_mode": "blocking", 
                    "user": "abc-123"
                },
                timeout=60.0
            )
            result = response.json()
            raw_reason_content = result['data']['outputs']['confidence_results']
            reason, status = raw_reason_content.split('status')
            label = ""
            if '低置信' in status:
                label = "no"
            elif '高置信' in status:
                label = "yes"
            reason = reason.replace('#',"").replace('``',"").strip()
            result['data']['outputs']['confidence_results'] = {'status':label,'reason':reason}
            result['data']['outputs']['raw_content'] = raw_reason_content
            if len(ref_items) != len(ref_ids):
                result['data']['outputs']['ref_ids'] = result['data']['outputs']['ref_ids'] + '--预警：可能出现幻觉引用'
            return result
    
    # 创建异步任务
    tasks = []
    for _, (sentence, ref_ids) in enumerate(reference_pairs):
        task = make_request(sentence, ref_ids)
        tasks.append(task)
    
    # 并行执行所有请求
    results = await asyncio.gather(*tasks)
    yield step_status(2,workflow_id)

    
    try:
        # 基于文本内容生成模拟的置信度分析

        yield step_status(3,workflow_id)
        
        analysis_result = get_analysis_result(workflow_id,results)

        redis_conn.set(analysis_redis_key,json.dumps(results,ensure_ascii=False))
   
        yield f"data: {json.dumps({'choices': [{'delta': {'content': analysis_result}}]})}\n\n"
        
        # 发送完成信号
        yield "data: [DONE]\n\n"
        return
    except Exception as e:
        yield f"data: {json.dumps({'choices': [{'delta': {'content': f'[ERROR]❌ 置信检查失败: {str(e)}' + chr(10)}}]})}\n\n"
        yield "data: [DONE]\n\n"
        return

@router.post("/check")
async def confidence_check(
    request: ConfidenceCheckRequest,
    current_user: UserModel = Depends(get_verified_user)
):
    """
    流式置信检查API
    接收文本和工作流ID，返回流式的置信度分析结果
    """
    try:
        # 验证输入
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="文本内容不能为空")
        
        if not request.workflowId.strip():
            raise HTTPException(status_code=400, detail="工作流ID不能为空")
        
        # 创建流式响应
        async def generate_response():
            async for chunk in simulate_confidence_check(request.text, request.workflowId):
                yield chunk
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"置信检查失败: {str(e)}")

@router.get("/status")
async def confidence_status(current_user: UserModel = Depends(get_verified_user)):
    """
    获取置信检查服务状态
    """
    return {
        "status": "available",
        "version": "1.0.0",
        "description": "置信度检查服务正常运行"
    } 