from flask_wtf import FlaskForm
from flask import Blueprint, abort, render_template, url_for, redirect, flash, request
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Length
from flask_login import login_user, login_required, logout_user, current_user
import app
from functools import wraps
from datetime import datetime


events_bp = Blueprint('events', __name__, template_folder='templates')


class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    date = DateField('Data', validators=[DataRequired()])
    submit = SubmitField('Add event')

class UpdateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    date = DateField('Data',validators=[DataRequired()])
    submit = SubmitField('Update event')

def role_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return func(*args, **kwargs)
        return decorated_view
    return decorator


@events_bp.route('/events/update/<int:event_id>',methods=['GET','POST'])
@login_required
@role_required('admin')
def updateEvent(event_id):
    event = app.Event.query.get(event_id) 
    form = UpdateForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.date = form.date.data
        app.db.session.commit()
        return redirect(url_for('AdminPanel'))
    return render_template('UpdateEvent.html',form=form,event=event)
    

@events_bp.route('/delete_event/<event_id>')
def delete_event(event_id):
    event_to_delete = app.Event.query.get(event_id)
    app.db.session.delete(event_to_delete)
    app.db.session.commit()
    return redirect(url_for('AdminPanel'))

@events_bp.route('/admin/events',methods=['GET','POST'])
@role_required('admin')
def eventsAdmin():
    events = app.Event.query.all()
    form = EventForm()
    if form.validate_on_submit():
        new_event = app.Event(title=form.title.data, description=form.description.data, date=form.date.data)
        app.db.session.add(new_event)
        app.db.session.commit()
        return redirect(url_for('AdminPanel'))   
    return render_template('UploadEvent.html',form = form,events=events)


@events_bp.route('/singUp/<event_id>', methods=['GET', 'POST'])
@login_required
def singUp(event_id):
    user=app.User.query.get(current_user.id)
    event=app.Event.query.get(event_id)
    event.members.append(user)
    app.db.session.commit()
    return redirect(url_for('calendar'))
