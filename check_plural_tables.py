from app import app, db
import re
from collections import defaultdict

def get_plural_table_pairs():
    """检查数据库中命名存在单复数关系的表"""
    print("=== 数据库单复数表名检查 ===")
    
    # 获取所有表名
    with app.app_context():
        # 获取所有表名
        inspector = db.inspect(db.engine)
        all_tables = inspector.get_table_names()
        
        print(f"数据库中共有 {len(all_tables)} 张表:")
        print(", ".join(all_tables))
        
        # 分析单复数关系
        plural_patterns = [
            (r'(.*)ies$', r'\1y'),  # 例如：dimensions -> dimension
            (r'(.*)es$', r'\1'),    # 例如：scores -> score
            (r'(.*)s$', r'\1'),     # 例如：employees -> employee
        ]
        
        table_pairs = []
        processed = set()
        
        # 检查每个表名
        for table in all_tables:
            if table in processed:
                continue
            
            singular_candidates = []
            
            # 尝试各种复数形式转换
            for pattern, replacement in plural_patterns:
                if re.match(pattern, table):
                    singular = re.sub(pattern, replacement, table)
                    singular_candidates.append(singular)
            
            # 检查是否有对应的单数表
            for singular in singular_candidates:
                if singular in all_tables and singular != table:
                    table_pairs.append((singular, table))
                    processed.add(singular)
                    processed.add(table)
                    break
        
        # 打印结果
        print("\n发现以下单复数表名对:")
        if not table_pairs:
            print("没有发现单复数关系的表。")
        else:
            for singular, plural in table_pairs:
                print(f"- {singular} (单数) 和 {plural} (复数)")
        
        return table_pairs

if __name__ == '__main__':
    get_plural_table_pairs()