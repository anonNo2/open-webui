import { WEBUI_BASE_URL } from '$lib/constants';
import { createOpenAITextStream } from './streaming';

export interface ConfidenceCheckRequest {
	text: string;
	workflowId: string;
}

export interface ConfidenceCheckResponse {
	done: boolean;
	value: string;
	error?: any;
}

/**
 * 流式置信检查API调用
 * @param token 用户token
 * @param request 请求参数
 * @returns 异步生成器，用于流式接收响应
 */
export async function* confidenceCheckStream(
	token: string,
	request: ConfidenceCheckRequest
): AsyncGenerator<ConfidenceCheckResponse> {
	try {
		const response = await fetch(`${WEBUI_BASE_URL}/api/confidence/check`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				...(token && { authorization: `Bearer ${token}` })
			},
			body: JSON.stringify(request)
		});

		if (!response.ok) {
			const error = await response.json();
			yield { done: true, value: '', error };
			return;
		}

		if (!response.body) {
			yield { done: true, value: '', error: 'No response body' };
			return;
		}

		// 使用现有的流式处理逻辑
		const stream = await createOpenAITextStream(response.body, false);
		
		for await (const chunk of stream) {
			yield {
				done: chunk.done,
				value: chunk.value,
				error: chunk.error
			};
		}
	} catch (error) {
		console.error('Confidence check error:', error);
		yield { done: true, value: '', error };
	}
}

/**
 * 非流式置信检查API调用（用于简单场景）
 * @param token 用户token
 * @param request 请求参数
 * @returns Promise<string> 完整的响应文本
 */
export async function confidenceCheck(
	token: string,
	request: ConfidenceCheckRequest
): Promise<string> {
	let result = '';
	
	for await (const chunk of confidenceCheckStream(token, request)) {
		if (chunk.error) {
			throw new Error(chunk.error);
		}
		if (chunk.done) {
			break;
		}
		result += chunk.value;
	}
	
	return result;
} 