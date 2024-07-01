from flask_wtf import FlaskForm
from flask import Blueprint, abort, render_template, url_for, redirect, flash, request
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Length
from flask_login import login_user, login_required, logout_user, current_user
import app
from functools import wraps
from datetime import datetime


tasks_bp = Blueprint('tasks', __name__, template_folder='templates')


class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    deadline = DateField('Deadline', validators=[DataRequired()])
    task_id = StringField('Task ID')  # Dodane pole ukryte
    submit = SubmitField('Add task')

class UpdateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    deadline = DateField('Deadline',validators=[DataRequired()])
    submit = SubmitField('Update task')

def role_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return func(*args, **kwargs)
        return decorated_view
    return decorator

@tasks_bp.route('/tasks', methods=['GET', 'POST'])
@role_required('user')
def tasks():
    tasks = app.Task.query.filter_by(user_id=current_user.id).all()
    form = TaskForm(prefix='form')
    if form.validate_on_submit() and form.submit.data:
        new_task = app.Task(title=form.title.data, description=form.description.data, deadline=form.deadline.data, user_id=current_user.id)
        app.db.session.add(new_task)
        app.db.session.commit()
        return redirect(url_for('tasks.tasks'))

    return render_template('tasks.html', form=form, tasks=tasks)

@tasks_bp.route('/tasks/update/<int:task_id>',methods=['GET','POST'])
def updateTask(task_id):
    task = app.Task.query.get(task_id)
    if not task.user_id == current_user.id:
        return redirect(url_for('tasks.tasks'))   
    else:
        form = UpdateForm()
        if form.validate_on_submit():
            task.title = form.title.data
            task.description = form.description.data
            task.deadline = form.deadline.data
            app.db.session.commit()
            return redirect('/tasks')
        return render_template('updateTask.html',form=form,task=task)

@tasks_bp.route('/admin/tasks',methods=['GET','POST'])
@role_required('Admin')
def tasksAdmin():
    tasks = app.Task.query.all()
    form = TaskForm()
    if form.validate_on_submit():
        flash(current_user.id)
        new_task = app.Task(title=form.title.data, description=form.description.data, deadline=form.deadline.data, user_id=current_user.id)
        app.db.session.add(new_task)
        app.db.session.commit()
        tasks = app.Task.query.all()
        return redirect('tasks')   
    return render_template('tasks.html',form = form,tasks=tasks)

