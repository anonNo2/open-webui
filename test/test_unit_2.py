import json
def main(rag_content: str, web_search_content: str) -> dict:

    web_search_results = ''
    web_search_references = ''
    if web_search_content.startswith("{"):
        web_search_content = json.loads(web_search_content)
        web_search_results = web_search_content["results"]
        web_search_references = web_search_content["references_string"]
    
    return {
        "rag_content": rag_content,
        "web_search_results": web_search_results,
        "web_search_references": web_search_references,
    }
