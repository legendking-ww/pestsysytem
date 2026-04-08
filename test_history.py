#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试历史记录清除功能
"""

import sys
sys.path.append('.')

from backend.database import Database

# 测试数据库操作
def test_database_operations():
    print("开始测试数据库操作...")
    
    # 初始化数据库
    db = Database()
    
    # 测试1: 注册一个测试用户
    print("\n测试1: 注册测试用户")
    success, user_id = db.register_user("test_user", "test123")
    if success:
        print(f"注册成功，用户ID: {user_id}")
    else:
        print(f"注册失败: {user_id}")
    
    # 测试2: 保存测试检测记录
    print("\n测试2: 保存测试检测记录")
    test_results = [
        {"class_name": "蚜虫", "confidence": 0.95},
        {"class_name": "螨虫", "confidence": 0.88}
    ]
    record_id = db.save_detection(user_id, "test_image.jpg", "images/test_image.jpg", test_results, 2)
    print(f"保存记录成功，记录ID: {record_id}")
    
    # 测试3: 获取历史记录
    print("\n测试3: 获取历史记录")
    history = db.get_user_history(user_id)
    print(f"获取到 {len(history)} 条历史记录")
    for record in history:
        print(f"  - ID: {record['id']}, 图片: {record['image_name']}, 时间: {record['time']}, 总数: {record['total']}")
    
    # 测试4: 删除单个记录
    print("\n测试4: 删除单个记录")
    if history:
        delete_success = db.delete_history_record(history[0]['id'], user_id)
        if delete_success:
            print("删除记录成功")
        else:
            print("删除记录失败")
    
    # 测试5: 再次获取历史记录
    print("\n测试5: 再次获取历史记录")
    history_after_delete = db.get_user_history(user_id)
    print(f"获取到 {len(history_after_delete)} 条历史记录")
    
    # 测试6: 保存多条记录
    print("\n测试6: 保存多条测试记录")
    for i in range(3):
        test_results = [{"class_name": f"昆虫{i+1}", "confidence": 0.8 + i*0.05}]
        db.save_detection(user_id, f"test_image_{i+1}.jpg", f"images/test_image_{i+1}.jpg", test_results, 1)
    print("保存多条记录成功")
    
    # 测试7: 清空所有历史记录
    print("\n测试7: 清空所有历史记录")
    deleted_count = db.clear_user_history(user_id)
    print(f"清空成功，删除了 {deleted_count} 条记录")
    
    # 测试8: 验证历史记录已清空
    print("\n测试8: 验证历史记录已清空")
    history_empty = db.get_user_history(user_id)
    print(f"获取到 {len(history_empty)} 条历史记录")
    if len(history_empty) == 0:
        print("历史记录已成功清空")
    else:
        print("历史记录未清空")
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    test_database_operations()
