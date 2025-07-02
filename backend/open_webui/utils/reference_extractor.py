import re
from typing import Dict, List, Tuple


class ReferenceExtractor:
    """引用提取器，用于从文本中提取引用标记"""
    
    def __init__(self):
        # 匹配引用标记的正则表达式，支持[1][2]这样的格式
        self.reference_pattern = r'\[(\d+)\]'
    
    def extract_references(self, text: str) -> Dict[str, List[str]]:
        """
        从文本中提取引用标记
        
        Args:
            text: 输入的文本，如 "这是第一句话[1][2]。这是第二句话[2]。这是第三句话[3]。"
            
        Returns:
            Dict[str, List[str]]: 键为句子，值为引用标记列表
        """
        # 找到所有引用标记的位置
        matches = list(re.finditer(r'\[\d+\]', text))
        if not matches:
            return {}
        
        result = {}
        i = 0
        
        while i < len(matches):
            # 找到当前位置开始的连续引用标记组
            j = i
            while j + 1 < len(matches) and matches[j + 1].start() == matches[j].end():
                j += 1
            
            # 收集这组连续的引用标记
            refs = [matches[k].group() for k in range(i, j + 1)]
            
            # 找到这组引用标记前面的文本
            start_pos = matches[i - 1].end() if i > 0 else 0
            end_pos = matches[i].start()
            text_content = text[start_pos:end_pos].strip()
            
            if text_content:
                result[text_content] = refs
            
            i = j + 1
        
        return result
    
    def extract_references_simple(self, text: str) -> List[Tuple[str, str]]:
        """
        简化版本的引用提取，返回(key, val)格式的列表
        
        Args:
            text: 输入的文本
            
        Returns:
            List[Tuple[str, str]]: (句子, 引用标记)的列表
        """
        references_dict = self.extract_references(text)
        result = []
        
        for sentence, refs in references_dict.items():
            # 将引用标记列表合并为一个字符串
            refs_str = ''.join(refs)
            result.append((sentence, refs_str))
        
        return result

    def extract_reference_pairs(self,text: str) -> List[Tuple[str, str]]:
        """
        提取引用对
        """
        raw_pairs = self.extract_references_simple(text)
        reference_pairs = []
        for sentence, refs in raw_pairs:
            print(f"sentence: {sentence}, refs: {refs}")
            ref_ids = [int(i) for i in refs[1:-1].split('][')]
            reference_pairs.append((sentence, ref_ids))
        return reference_pairs


def main():
    """测试函数"""
    extractor = ReferenceExtractor()
    
    # 测试文本
    test_text = '''
这是第一句话[1][2]。这是第二句话[2]。这是第三句话[3]。
# 2025年6月27日黄金价格最新行情

## 一、实时国际金价
1. **现货黄金**：最新报价 **765.87元/克**（更新时间：11:04:18），较前日下跌5.88元[3][6]。
2. **美元计价**：国际金价 **3304.97美元/盎司**（折合人民币约761.92元/克），较昨日下跌22.63美元[6][7]。

## 二、国内市场行情
1. **基础金价**：
   - **上海黄金交易所(AU9999)**： **763.15元/克**（最低触及761.99元）[1][7]。
   - **投资金条**： **784元/克**（6月26日数据，品牌金店基准价）[5]。
2. **品牌金店零售价**：
   - **周大福/周生生**： **998-1006元/克**[2][5]
   - **老凤祥/菜百首饰**： **1006元/克（老凤祥）** / **989元/克（菜百）**[2][5]

## 三、贵金属衍生行情
1. **黄金回收**：足金999回收价 **755元/克**，铂金 **289元/克**[6][8]。
2. **期货价格**：纽约黄金期货 **3317.25美元/盎司**（下跌30.75美元）[6][9]。

## 四、其他参考数据
1. **汇率基准**：1美元=7.1705人民币，1盎司=31.10348克[6]。
2. **白银及钯金**：现货白银 **8.251元/克**，钯金 **257.1元/克**[3][8]。

'''
    
    print("输入文本:")
    print(test_text)
    print("\n输出结果:")
    
    # 使用简化版本
    results = extractor.extract_reference_pairs(test_text)
    
    for key, val in results:
        print(f"key:{key}    val: {val}")


if __name__ == "__main__":
    main()
