

import sqlite3
import os
import json
from datetime import datetime

class Database:
    def __init__(self, db_path='database/pest_detection.db'):
        """初始化数据库连接"""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                image_name TEXT NOT NULL,
                image_path TEXT,
                detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                results TEXT NOT NULL,
                total_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("数据库初始化完成")
    
    def register_user(self, username, password, email=''):
        """用户注册"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password, email)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return True, user_id
        except sqlite3.IntegrityError:
            return False, "用户名已存在"
        except Exception as e:
            return False, str(e)
    
    def login_user(self, username, password):
        """用户登录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, {"id": user[0], "username": user[1]}
        else:
            return False, "用户名或密码错误"
    
    def save_detection(self, user_id, image_name, image_path, results, total_count):
        """保存检测记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO detection_history 
               (user_id, image_name, image_path, results, total_count) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, image_name, image_path, json.dumps(results, ensure_ascii=False), total_count)
        )
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_user_history(self, user_id, limit=50):
        """获取用户的历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, image_name, detection_time, total_count, results 
               FROM detection_history 
               WHERE user_id=? 
               ORDER BY detection_time DESC 
               LIMIT ?""",
            (user_id, limit)
        )
        records = cursor.fetchall()
        conn.close()
        
        history = []
        for r in records:
            history.append({
                'id': r[0],
                'image_name': r[1],
                'time': r[2],
                'total': r[3],
                'results': json.loads(r[4])
            })
        return history
    
    def clear_user_history(self, user_id):
        """清空用户的所有历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM detection_history WHERE user_id=?",
            (user_id,)
        )
        conn.commit()
        deleted_count = cursor.rowcount
        conn.close()
        return deleted_count
    
    def delete_history_record(self, record_id, user_id):
        """删除指定的历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM detection_history WHERE id=? AND user_id=?",
            (record_id, user_id)
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
