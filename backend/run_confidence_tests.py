#!/usr/bin/env python3
"""
运行置信检查测试的脚本
"""

import sys
import os
import subprocess
import pytest

def run_tests():
    """运行置信检查相关的测试"""
    
    # 添加当前目录到Python路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    print("🧪 开始运行置信检查测试...")
    print("=" * 50)
    
    # 运行专门的simulate_confidence_check测试
    print("📋 运行 simulate_confidence_check 方法测试...")
    test_file = "tests/test_simulate_confidence_check.py"
    
    if os.path.exists(test_file):
        result = pytest.main([
            test_file,
            "-v",
            "--tb=short",
            "--color=yes"
        ])
        
        if result == 0:
            print("✅ simulate_confidence_check 测试通过!")
        else:
            print("❌ simulate_confidence_check 测试失败!")
            return False
    else:
        print(f"⚠️  测试文件 {test_file} 不存在")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有置信检查测试完成!")
    
    return True

def run_specific_test(test_name=None):
    """运行特定的测试"""
    if test_name:
        print(f"🎯 运行特定测试: {test_name}")
        pytest.main([
            "tests/test_simulate_confidence_check.py",
            "-v",
            "-k", test_name,
            "--tb=short",
            "--color=yes"
        ])
    else:
        run_tests()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 如果提供了测试名称参数
        test_name = sys.argv[1]
        run_specific_test(test_name)
    else:
        # 运行所有测试
        run_tests() 