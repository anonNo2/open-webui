import json


def main(history: list[str], turns: int) -> dict:

    history_references = '暂无历史信息\n'
    if history:
        history_references = '\n'.join(history[-turns:]) + '\n'
    
    return {
        "history_references": history_references
        
    }
