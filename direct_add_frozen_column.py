import sqlite3

# 连接到数据库
conn = sqlite3.connect('performance_evaluation.db')
cursor = conn.cursor()

# 检查字段是否已存在
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='employee'")
table_info = cursor.fetchone()

if 'is_frozen' not in table_info[0]:
    # 添加is_frozen字段
    cursor.execute("ALTER TABLE employee ADD COLUMN is_frozen BOOLEAN DEFAULT 0")
    conn.commit()
    print('成功添加is_frozen字段')
else:
    print('is_frozen字段已存在')

# 关闭连接
conn.close()