import sqlite3
import os
import shutil
import time

# 备份数据库
db_path = 'performance_evaluation.db'
bak_path = f'{db_path}.bak.{int(time.time())}'
shutil.copy2(db_path, bak_path)
print(f'数据库已备份到 {bak_path}')

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 删除旧表
tables_to_drop = ['evaluation_score', 'employee', 'evaluation_record', 'evaluation_task', 'evaluation_dimension']
for table in tables_to_drop:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f'已删除旧表: {table}')
    except Exception as e:
        print(f'删除表 {table} 时出错: {e}')

# 检查并删除其他可能的旧表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    table_name = table[0]
    # 检查是否存在单数形式的表名(如果复数表名存在)
    if table_name.endswith('s'):
        singular_name = table_name[:-1]
        if any(singular_name == t[0] for t in tables):
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {singular_name}")
                print(f'已删除冗余表: {singular_name}')
            except Exception as e:
                print(f'删除表 {singular_name} 时出错: {e}')

# 提交更改并关闭连接
conn.commit()
conn.close()

print('数据库清理完成。现在可以应用迁移了。')