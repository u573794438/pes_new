from app import app
from extensions import db
from models import EvaluationScore
from datetime import datetime
import logging

def migrate_evaluation_scores():
    with app.app_context():
        try:
            # 查询旧表evaluation_score中的所有记录
            old_scores = db.session.execute('SELECT * FROM evaluation_score').fetchall()
            logging.info(f"找到 {len(old_scores)} 条旧评分记录")

            # 获取旧表的列名
            old_columns = [desc[0] for desc in db.session.execute('SELECT * FROM evaluation_score LIMIT 0').cursor.description]
            logging.info(f"旧表列名: {old_columns}")

            # 获取新表的列名（排除id，因为它是自增主键）
            new_columns = [column.name for column in EvaluationScore.__table__.columns if column.name != 'id']
            logging.info(f"新表列名: {new_columns}")

            # 迁移数据
            migrated_count = 0
            for old_score in old_scores:
                # 创建新评分字典
                new_score_data = {}

                # 处理字段映射
                for col in old_columns:
                    # 跳过需要忽略的字段
                    if col in ['created_at', 'updated_at']:
                        continue

                    # 处理字段名转换
                    if col == 'record_id':
                        new_col = 'evaluation_record_id'
                        if new_col in new_columns:
                            new_score_data[new_col] = getattr(old_score, col)
                    elif col in new_columns:
                        new_score_data[col] = getattr(old_score, col)

                # 确保comment字段存在，即使为空
                if 'comment' not in new_score_data:
                    new_score_data['comment'] = ''

                # 创建新评分记录
                new_score = EvaluationScore(**new_score_data)
                db.session.add(new_score)
                migrated_count += 1

            db.session.commit()
            logging.info(f"成功迁移 {migrated_count} 条记录到evaluation_scores表")
            return True, f"迁移成功，共迁移 {migrated_count} 条记录"

        except Exception as e:
            db.session.rollback()
            logging.error(f"迁移过程中出错: {str(e)}")
            return False, f"迁移失败: {str(e)}"

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    success, message = migrate_evaluation_scores()
    print(f"=== {'迁移成功' if success else '迁移失败'} ===")
    print(message)