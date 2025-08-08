from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from models import Employee, EvaluationTask, EvaluationRecord, EvaluationScore, EvaluationDimension
from extensions import db
from datetime import datetime
import pandas as pd
import io
import urllib.parse

# 生成考评结果表单
class GenerateEvaluationResultsForm(FlaskForm):
    task_id = SelectField('选择评估任务', validators=[DataRequired()])
    department_rating = SelectField('部门绩效评级', choices=[('甲', '甲'), ('乙', '乙'), ('丙', '丙'), ('丁', '丁')], validators=[DataRequired()])
    submit = SubmitField('生成结果')

# 导出考评结果表单
class ExportEvaluationResultsForm(FlaskForm):
    task_id = SelectField('选择评估任务', validators=[DataRequired()])
    department_rating = SelectField('部门绩效评级', choices=[('甲', '甲'), ('乙', '乙'), ('丙', '丙'), ('丁', '丁')], validators=[DataRequired()])
    submit = SubmitField('导出Excel')

# 创建蓝图
evaluation_results_bp = Blueprint('evaluation_results', __name__)

# 蓝图将在app.py中注册

@evaluation_results_bp.route('/admin/generate-evaluation-results', methods=['GET', 'POST'])
@login_required
def admin_generate_evaluation_results():
    # 检查用户权限
    if not current_user.is_admin and current_user.role == '员工':
        flash('无权限访问此页面', 'danger')
        return redirect(url_for('admin_dashboard'))

    # 获取所有评估任务
    tasks = EvaluationTask.query.order_by(EvaluationTask.year.desc(), EvaluationTask.quarter.desc()).all()

    # 创建表单实例
    form = GenerateEvaluationResultsForm()

    # 设置任务选择字段的选项
    form.task_id.choices = [(str(task.id), task.name) for task in tasks]

    results = None
    task_name = None
    selected_task_id = None
    selected_department_rating = '丙'

    if form.validate_on_submit():
        selected_task_id = form.task_id.data
        selected_department_rating = form.department_rating.data

        # 获取选定的任务
        task = EvaluationTask.query.get(selected_task_id)
        if not task:
            flash('无效的任务ID', 'danger')
            return redirect(url_for('evaluation_results.admin_generate_evaluation_results'))

        task_name = task.name

        # 1. 获取所有被评估者（角色为'员工'的员工）
        evaluatees = Employee.query.filter(
            Employee.role == '员工',
            Employee.employee_id != '10000',
            Employee.is_frozen == False
        ).all()

        # 2. 为每个被评估者计算各项分数和最终分数
        results = []
        for evaluatee in evaluatees:
            # 计算部门负责人分数（角色为'部门负责人'的评估者打分的平均值）- 转换为百分制
            dept_head_scores = db.session.query(EvaluationScore.score)\
                .join(EvaluationRecord)\
                .filter(
                    EvaluationRecord.task_id == selected_task_id,
                    EvaluationRecord.evaluatee_id == evaluatee.id,
                    EvaluationRecord.status == 'submitted',
                    Employee.id == EvaluationRecord.evaluator_id,
                    Employee.role == '部门负责人'
                ).all()
            dept_head_score = round(sum(score[0] for score in dept_head_scores) / len(dept_head_scores) * 20, 2) if dept_head_scores else 0

            # 计算部门经理分数（角色为'部门经理'的评估者打分的平均值）- 转换为百分制
            dept_manager_scores = db.session.query(EvaluationScore.score)\
                .join(EvaluationRecord)\
                .filter(
                    EvaluationRecord.task_id == selected_task_id,
                    EvaluationRecord.evaluatee_id == evaluatee.id,
                    EvaluationRecord.status == 'submitted',
                    Employee.id == EvaluationRecord.evaluator_id,
                    Employee.role == '部门经理'
                ).all()
            dept_manager_score = round(sum(score[0] for score in dept_manager_scores) / len(dept_manager_scores) * 20, 2) if dept_manager_scores else 0

            # 计算员工互评分数（角色为'员工'的评估者打分的平均值）- 转换为百分制
            peer_scores = db.session.query(EvaluationScore.score)\
                .join(EvaluationRecord)\
                .filter(
                    EvaluationRecord.task_id == selected_task_id,
                    EvaluationRecord.evaluatee_id == evaluatee.id,
                    EvaluationRecord.status == 'submitted',
                    Employee.id == EvaluationRecord.evaluator_id,
                    Employee.role == '员工'
                ).all()
            peer_score = round(sum(score[0] for score in peer_scores) / len(peer_scores) * 20, 2) if peer_scores else 0

            # 计算分管领导分数（角色为'分管领导'的评估者打分的平均值）- 转换为百分制
            leader_scores = db.session.query(EvaluationScore.score)\
                .join(EvaluationRecord)\
                .filter(
                    EvaluationRecord.task_id == selected_task_id,
                    EvaluationRecord.evaluatee_id == evaluatee.id,
                    EvaluationRecord.status == 'submitted',
                    Employee.id == EvaluationRecord.evaluator_id,
                    Employee.role == '分管领导'
                ).all()
            leader_score = round(sum(score[0] for score in leader_scores) / len(leader_scores) * 20, 2) if leader_scores else 0

            # 计算最终分数（加权合计）
            weighted_score = round(
                dept_head_score * 0.4 + 
                dept_manager_score * 0.15 + 
                peer_score * 0.15 + 
                leader_score * 0.3,
                2
            )

            # 乘以岗位系数并限制最大值为99分
            final_score = min(round(weighted_score * evaluatee.position_coefficient, 2), 99)

            results.append({
                'name': evaluatee.name,
                'position': evaluatee.position,
                'dept_head_score': dept_head_score,
                'dept_manager_score': dept_manager_score,
                'peer_score': peer_score,
                'leader_score': leader_score,
                'final_score': final_score
            })

        # 3. 按最终分数排序
        results.sort(key=lambda x: x['final_score'], reverse=True)

        # 4. 计算绩效等级
        total_employees = len(results)
        if total_employees > 0:
            # 根据部门绩效评级确定A、B档比例
            if selected_department_rating == '甲':
                a_ratio = 0.4
                b_ratio = 0.3
            elif selected_department_rating == '乙':
                a_ratio = 0.2
                b_ratio = 0.2
            elif selected_department_rating == '丙':
                a_ratio = 0.15
                b_ratio = 0.2
            else:  # 丁
                a_ratio = 0.1
                b_ratio = 0.2

            # 计算各等级人数
            a_count = round(total_employees * a_ratio)
            b_count = round(total_employees * b_ratio)
            c_count = total_employees - a_count - b_count

            # 分配绩效等级（结合排名比例和分数阈值）
            for i, result in enumerate(results):
                if i < a_count and result['final_score'] >= 90:
                    result['performance_level'] = 'A'
                elif i < a_count + b_count and result['final_score'] >= 80:
                    result['performance_level'] = 'B'
                elif result['final_score'] >= 70:
                    result['performance_level'] = 'C'
                else:
                    result['performance_level'] = 'D'

            # 添加排名
            for i, result in enumerate(results):
                result['rank'] = i + 1

    # 渲染模板
    return render_template('admin/generate_evaluation_results.html',
                           form=form,
                           tasks=tasks,
                           selected_task_id=selected_task_id,
                           selected_department_rating=selected_department_rating,
                           results=results,
                           task_name=task_name)

@evaluation_results_bp.route('/admin/export-evaluation-results', methods=['GET', 'POST'])
@login_required
def export_evaluation_results():
    # 检查用户权限
    if not current_user.is_admin and current_user.role == '员工':
        flash('无权限执行此操作', 'danger')
        return redirect(url_for('admin_dashboard'))

    # 获取所有评估任务
    tasks = EvaluationTask.query.order_by(EvaluationTask.year.desc(), EvaluationTask.quarter.desc()).all()

    # 创建表单实例
    form = ExportEvaluationResultsForm()

    # 设置任务选择字段的选项
    form.task_id.choices = [(str(task.id), task.name) for task in tasks]

    if form.validate_on_submit():
        selected_task_id = form.task_id.data
        selected_department_rating = form.department_rating.data

        if not selected_task_id:
            flash('请选择评估任务', 'danger')
            return redirect(url_for('evaluation_results.admin_generate_evaluation_results'))

    # 生成结果（与前面的逻辑相同）
    task = EvaluationTask.query.get(selected_task_id)
    evaluatees = Employee.query.filter(
        Employee.role == '员工',
        Employee.employee_id != '10000',
        Employee.is_frozen == False
    ).all()

    results = []
    for evaluatee in evaluatees:
        # 计算部门负责人分数 - 转换为百分制
            dept_head_scores = db.session.query(EvaluationScore.score)\
                .join(EvaluationRecord)\
                .filter(
                    EvaluationRecord.task_id == selected_task_id,
                    EvaluationRecord.evaluatee_id == evaluatee.id,
                    EvaluationRecord.status == 'submitted',
                    Employee.id == EvaluationRecord.evaluator_id,
                    Employee.role == '部门负责人'
                ).all()
            dept_head_score = round(sum(score[0] for score in dept_head_scores) / len(dept_head_scores) * 20, 2) if dept_head_scores else 0

            # 计算部门经理分数 - 转换为百分制
            dept_manager_scores = db.session.query(EvaluationScore.score)\
                .join(EvaluationRecord)\
                .filter(
                    EvaluationRecord.task_id == selected_task_id,
                    EvaluationRecord.evaluatee_id == evaluatee.id,
                    EvaluationRecord.status == 'submitted',
                    Employee.id == EvaluationRecord.evaluator_id,
                    Employee.role == '部门经理'
                ).all()
            dept_manager_score = round(sum(score[0] for score in dept_manager_scores) / len(dept_manager_scores) * 20, 2) if dept_manager_scores else 0

            # 计算员工互评分数 - 转换为百分制
            peer_scores = db.session.query(EvaluationScore.score)\
                .join(EvaluationRecord)\
                .filter(
                    EvaluationRecord.task_id == selected_task_id,
                    EvaluationRecord.evaluatee_id == evaluatee.id,
                    EvaluationRecord.status == 'submitted',
                    Employee.id == EvaluationRecord.evaluator_id,
                    Employee.role == '员工'
                ).all()
            peer_score = round(sum(score[0] for score in peer_scores) / len(peer_scores) * 20, 2) if peer_scores else 0

            # 计算分管领导分数 - 转换为百分制
            leader_scores = db.session.query(EvaluationScore.score)\
                .join(EvaluationRecord)\
                .filter(
                    EvaluationRecord.task_id == selected_task_id,
                    EvaluationRecord.evaluatee_id == evaluatee.id,
                    EvaluationRecord.status == 'submitted',
                    Employee.id == EvaluationRecord.evaluator_id,
                    Employee.role == '分管领导'
                ).all()
            leader_score = round(sum(score[0] for score in leader_scores) / len(leader_scores) * 20, 2) if leader_scores else 0

            # 计算最终分数
            final_score = round(
                dept_head_score * 0.4 + 
                dept_manager_score * 0.15 + 
                peer_score * 0.15 + 
                leader_score * 0.3,
                2
            )

            results.append({
                'name': evaluatee.name,
                'position': evaluatee.position,
                'dept_head_score': dept_head_score,
                'dept_manager_score': dept_manager_score,
                'peer_score': peer_score,
                'leader_score': leader_score,
                'final_score': final_score
            })

    # 排序和计算绩效等级
    results.sort(key=lambda x: x['final_score'], reverse=True)
    total_employees = len(results)

    if total_employees > 0:
        if selected_department_rating == '甲':
            a_ratio = 0.4
            b_ratio = 0.3
        elif selected_department_rating == '乙':
            a_ratio = 0.2
            b_ratio = 0.2
        elif selected_department_rating == '丙':
            a_ratio = 0.15
            b_ratio = 0.2
        else:  # 丁
            a_ratio = 0.1
            b_ratio = 0.2

        a_count = round(total_employees * a_ratio)
        b_count = round(total_employees * b_ratio)

        # 分配绩效等级（结合排名比例和分数阈值）
        for i, result in enumerate(results):
            if i < a_count and result['final_score'] >= 90:
                result['performance_level'] = 'A'
            elif i < a_count + b_count and result['final_score'] >= 80:
                result['performance_level'] = 'B'
            elif result['final_score'] >= 70:
                result['performance_level'] = 'C'
            else:
                result['performance_level'] = 'D'

        for i, result in enumerate(results):
            result['rank'] = i + 1

    # 创建DataFrame并导出为Excel
    df = pd.DataFrame(results)
    # 格式化分数为两位小数
    score_columns = ['dept_head_score', 'dept_manager_score', 'peer_score', 'leader_score', 'final_score']
    for col in score_columns:
        df[col] = df[col].round(2)
    # 选择并排序需要的列（删除分数排名列）
    df = df[['name', 'position', 'dept_head_score', 'dept_manager_score', 'peer_score', 'leader_score', 'final_score', 'performance_level']]
    df.columns = ['姓名', '岗位', '部门负责人分数', '部门经理分数', '员工互评分数', '分管领导分数', '最终分数', '绩效等级']

    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    # 获取工作表
    sheet_name = '绩效考评结果'
    # 写入数据，从第二行开始（留出标题行）
    df.to_excel(writer, index=False, sheet_name=sheet_name, startrow=1)

    # 获取workbook和worksheet对象
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # 添加标题（使用任务名称）
    title = task.name
    # 合并标题单元格（设置20号加粗字体）
    worksheet.merge_range(0, 0, 0, len(df.columns) - 1, title, workbook.add_format({'font_size': 20, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1}))

    # 设置表头和数据单元格格式（表头添加自动换行）
    header_format = workbook.add_format({'font_size': 12, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True, 'text_wrap': True})
    cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
    empty_cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

    # 应用表头格式
    for col_num, col_name in enumerate(df.columns):
        worksheet.write(1, col_num, col_name, header_format)

    # 设置数据区域的格式（只为非空单元格添加边框）
    # 获取数据范围
    num_rows = len(df)
    num_cols = len(df.columns)

    # 自动调整列宽并设置默认格式（无边框）
    for col_num, col_name in enumerate(df.columns):
        # 计算列标题的宽度（中文需要乘以系数）
        max_width = len(col_name) * 1.5 + 2
        # 检查该列所有数据的宽度
        for row in range(len(df)):
            cell_value = str(df.iloc[row, col_num])
            # 中文内容宽度系数调整
            cell_width = len(cell_value) * 1.5 if any('一-鿿' in char for char in cell_value) else len(cell_value)
            if cell_width > max_width:
                max_width = cell_width + 1
        # 对于岗位列，确保按内容最大宽度设置
        if col_name == '岗位':
            # 重新计算岗位列的最大宽度
            position_max_width = 0
            for row in range(len(df)):
                cell_value = str(df.iloc[row, col_num])
                cell_width = len(cell_value) * 1.5 if any('一-鿿' in char for char in cell_value) else len(cell_value)
                if cell_width > position_max_width:
                    position_max_width = cell_width + 1
            max_width = position_max_width
        # 设置列宽和默认格式（无边框）
        worksheet.set_column(col_num, col_num, max_width, empty_cell_format)

    # 为有数据的单元格添加边框
    for row_num in range(num_rows):
        for col_num in range(num_cols):
            cell_value = df.iloc[row_num, col_num]
            if pd.notna(cell_value):
                worksheet.write(row_num + 2, col_num, cell_value, cell_format)

    writer.close()

    output.seek(0)
    filename = f'绩效考评结果_{task.name}_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
    # 对文件名进行URL编码以处理中文
    encoded_filename = urllib.parse.quote(filename)

    # 创建响应
    response = Response(output.getvalue(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
    return response