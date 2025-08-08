from app import app
from models import db, EvaluationRecord
from sqlalchemy import text

def migrate_evaluation_records():
    """
    迁移'evaluation_record'表中的数据至表'evaluation_records'中
    规则:
    - 按字段名迁移
    - 跳过'evaluator_id' >= 21的记录
    - 对于源表中不存在的字段'task_id'和'status'，目标表分别以'1'和'submitted'填充
    """
    print("=== 开始迁移evaluation_record数据到evaluation_records表 ===")

    with app.app_context():
        try:
            # 检查目标表是否存在
            inspector = db.inspect(db.engine)
            if 'evaluation_records' not in inspector.get_table_names():
                print("错误: 目标表'evaluation_records'不存在。")
                print("=== 迁移失败 ===")
                return

            # 检查源表是否存在
            if 'evaluation_record' not in inspector.get_table_names():
                print("错误: 源表'evaluation_record'不存在。")
                print("=== 迁移失败 ===")
                return

            # 获取源表的字段名
            source_columns = [col['name'] for col in inspector.get_columns('evaluation_record')]
            print(f"源表'evaluation_record'的字段: {source_columns}")

            # 获取目标表的字段名
            target_columns = [col['name'] for col in inspector.get_columns('evaluation_records')]
            print(f"目标表'evaluation_records'的字段: {target_columns}")

            # 查询源表中符合条件的数据 (evaluator_id < 21)
            query = text(f"SELECT * FROM evaluation_record WHERE evaluator_id < 21")
            result = db.session.execute(query)
            source_data = result.fetchall()

            print(f"找到符合条件的记录数: {len(source_data)}")

            # 迁移数据
            migrated_count = 0
            for record in source_data:
                # 创建目标表记录
                new_record = EvaluationRecord()

                # 按字段名迁移数据
                for i, column in enumerate(source_columns):
                    if column in target_columns and column != 'id':  # 跳过id字段，由数据库自动生成
                        setattr(new_record, column, record[i])

                # 填充缺失字段
                new_record.task_id = 1
                new_record.status = 'submitted'

                # 添加到数据库
                db.session.add(new_record)
                migrated_count += 1

            # 提交更改
            db.session.commit()
            print(f"成功迁移 {migrated_count} 条记录到'evaluation_records'表。")
            print("=== 迁移完成 ===")

        except Exception as e:
            db.session.rollback()
            print(f"迁移过程中出错: {str(e)}")
            print("=== 迁移失败 ===")


def main():
    """主函数"""
    migrate_evaluation_records()

if __name__ == '__main__':
    main()