import json

def main(
    data_baidu: list[dict] = None,
    data_sogou: list[dict] = None,
    data_sogou_wechat: list[dict] = None,
    data_sogou_zhihu: list[dict] = None,
    data_chinaso: list[dict] = None,
    data_360so: list[dict] = None
    
) -> list[dict]:
    results = []
    references = []
    if data_baidu:
        for item in data_baidu:
            reduce_items = [{**item, "source": "baidu"} for item in item["searxng_results"]]            
            results.extend(reduce_items)
    if data_sogou:
        for item in data_sogou:
            reduce_items = [{**item, "source": "sogou"} for item in item["searxng_results"]]
            results.extend(reduce_items)
    if data_sogou_wechat:
        for item in data_sogou_wechat:
            reduce_items = [{**item, "source": "sogou_wechat"} for item in item["searxng_results"]]
            results.extend(reduce_items)
    if data_sogou_zhihu:
        for item in data_sogou_zhihu:
            reduce_items = [{**item, "source": "sogou_zhihu"} for item in item["searxng_results"]]
            results.extend(reduce_items)
    
    if data_chinaso:
        for item in data_chinaso:
            reduce_items = [{**item, "source": "chinaso"} for item in item["searxng_results"]]
            results.extend(reduce_items)
    if data_360so:
        for item in data_360so:
            reduce_items = [{**item, "source": "360so"} for item in item["searxng_results"]]
            results.extend(reduce_items)

    # 快速简单的去重
    # 根据 url，如果 url 相同，则认为是相同的信息
    seen_url = set()
    final_results = []
    for result in results:
        url = result["url"]
        if url == "":
            # 有的搜索结果没有 url，先保留
            final_results.append(result)
        elif url not in seen_url:
            seen_url.add(url)
            final_results.append(result)
    # 使用Jaccard相似度进行内容去重
    final_dedup_results = []
    for result in final_results:
        content = result.get("content", "")
        is_duplicate = False
        
        # 将内容分词成集合用于计算Jaccard相似度
        content_set = set(content.split())
        
        # 与已保留结果比较相似度
        for kept_result in final_dedup_results:
            kept_content = kept_result.get("content", "")
            kept_content_set = set(kept_content.split())
            
            # 计算Jaccard相似度
            intersection = len(content_set & kept_content_set)
            union = len(content_set | kept_content_set)
            
            if union > 0:
                similarity = intersection / union
                if similarity > 0.9:  # 90%相似度阈值
                    is_duplicate = True
                    break
                    
        if not is_duplicate:
            final_dedup_results.append(result)
            
    results = final_dedup_results
    # references_string 是 markdown 用于展示全部信息的．
    for idx, item in enumerate(results):
        url = item["url"]
        title = item["title"]
        reference = f"{idx + 1}. [{title}]({url})"
        references.append(reference)
    references_string = "\n".join(references)
    return {
        "results": json.dumps(results,ensure_ascii=False),
        "references_string": references_string,
    }
