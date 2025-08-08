import sqlite3
import os

def get_db_tables(db_path):
    """获取数据库中的所有表名"""
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def get_table_structure(db_path, table_name):
    """获取表的结构"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_table_columns(db_path, table_name):
    """获取表的列信息"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    conn.close()
    return [(col[1], col[2]) for col in columns]  # (列名, 数据类型)


def get_table_row_count(db_path, table_name):
    """获取表的行数"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def compare_table_data(db_path1, db_path2, table_name):
    """比较两个数据库中对应表的数据"""
    # 这个函数简化实现，只比较行数差异
    count1 = get_table_row_count(db_path1, table_name)
    count2 = get_table_row_count(db_path2, table_name)
    
    if count1 != count2:
        return f"行数不同: {db_path1} 有 {count1} 行, {db_path2} 有 {count2} 行"
    else:
        return f"行数相同: {count1} 行"


def compare_databases(db_path1, db_path2):
    """比较两个数据库"""
    print(f"\n=== 比较数据库: {db_path1} 和 {db_path2} ===")
    
    # 获取两个数据库中的表
    tables1 = get_db_tables(db_path1)
    tables2 = get_db_tables(db_path2)
    
    if not tables1 or not tables2:
        print("无法获取数据库表信息，比较失败。")
        return
    
    # 找出只在一个数据库中存在的表
    only_in_db1 = [table for table in tables1 if table not in tables2]
    only_in_db2 = [table for table in tables2 if table not in tables1]
    common_tables = [table for table in tables1 if table in tables2]
    
    # 打印结果
    if only_in_db1:
        print(f"仅在 {db_path1} 中存在的表:")
        for table in only_in_db1:
            print(f"- {table}")
    
    if only_in_db2:
        print(f"仅在 {db_path2} 中存在的表:")
        for table in only_in_db2:
            print(f"- {table}\n")
    
    if common_tables:
        print(f"两个数据库共有的表 ({len(common_tables)}):")
        for table in common_tables:
            print(f"\n--- 比较表: {table} ---")
            
            # 比较表结构
            struct1 = get_table_structure(db_path1, table)
            struct2 = get_table_structure(db_path2, table)
            
            if struct1 != struct2:
                print("表结构不同:")
                print(f"{db_path1} 结构: {struct1}")
                print(f"{db_path2} 结构: {struct2}")
            else:
                print("表结构相同")
                
            # 比较列信息
            cols1 = get_table_columns(db_path1, table)
            cols2 = get_table_columns(db_path2, table)
            
            if cols1 != cols2:
                print("列信息不同:")
                print(f"{db_path1} 列: {cols1}")
                print(f"{db_path2} 列: {cols2}")
            else:
                print("列信息相同")
                
            # 比较数据
            data_diff = compare_table_data(db_path1, db_path2, table)
            print(f"数据比较: {data_diff}")
    
    print(f"\n=== 比较完成 ===")


def main():
    """主函数"""
    db_path1 = "/root/my_pes/performance_evaluation.db.08071412"
    db_path2 = "/root/my_pes/performance_evaluation.db"
    
    compare_databases(db_path1, db_path2)

if __name__ == '__main__':
    main()