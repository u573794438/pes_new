from app import app
from extensions import db
from models import EvaluationTask
from datetime import datetime
import logging

def migrate_evaluation_tasks():
    with app.app_context():
        try:
            # 查询旧表evaluation_task中的所有记录
            old_tasks = db.session.execute('SELECT * FROM evaluation_task').fetchall()
            logging.info(f"找到 {len(old_tasks)} 条旧任务记录")

            # 获取旧表的列名
            old_columns = [desc[0] for desc in db.session.execute('SELECT * FROM evaluation_task LIMIT 0').cursor.description]
            logging.info(f"旧表列名: {old_columns}")

            # 获取新表的列名（排除id，因为它是自增主键）
            new_columns = [column.name for column in EvaluationTask.__table__.columns if column.name != 'id']
            logging.info(f"新表列名: {new_columns}")

            # 计算交集，按字段名迁移
            common_columns = list(set(old_columns) & set(new_columns))
            logging.info(f"共同列名: {common_columns}")

            # 迁移数据
            migrated_count = 0
            for old_task in old_tasks:
                # 创建新任务字典
                new_task_data = {col: getattr(old_task, col) for col in common_columns}

                # 处理特殊字段（如果有）
                # 如果旧表没有created_at和updated_at字段，设置默认值
                if 'created_at' not in old_columns:
                    new_task_data['created_at'] = datetime.utcnow()
                if 'updated_at' not in old_columns:
                    new_task_data['updated_at'] = datetime.utcnow()
                # 如果旧表没有status字段，设置默认值
                if 'status' not in old_columns:
                    new_task_data['status'] = 'published'

                # 创建新任务记录
                new_task = EvaluationTask(**new_task_data)
                db.session.add(new_task)
                migrated_count += 1

            db.session.commit()
            logging.info(f"成功迁移 {migrated_count} 条记录到evaluation_tasks表")
            return True, f"迁移成功，共迁移 {migrated_count} 条记录"

        except Exception as e:
            db.session.rollback()
            logging.error(f"迁移过程中出错: {str(e)}")
            return False, f"迁移失败: {str(e)}"

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    success, message = migrate_evaluation_tasks()
    print(f"=== {'迁移成功' if success else '迁移失败'} ===")
    print(message)