from app import app, db
from models import User

with app.app_context():
    # 创建管理员用户
    admin = User(username='admin', is_admin=True)
    admin.set_password('admin123')  # 设置管理员密码
    db.session.add(admin)
    
    try:
        db.session.commit()
        print('管理员用户创建成功！用户名: admin, 密码: admin123')
    except Exception as e:
        db.session.rollback()
        print(f'创建失败: {str(e)}')