from flask_wtf import FlaskForm
from flask import Blueprint, abort, render_template, url_for, redirect,flash
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, length
from werkzeug.utils import secure_filename
from flask_login import login_required

import app
from functools import wraps
from tasks import role_required
import os


posts_bp = Blueprint('posts', __name__, template_folder='templates')

class PostForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired()])
    description = StringField('Opis', validators=[DataRequired(), length(max=500)])
    image = FileField('Zdjęcie', validators=[FileRequired()])
    submit = SubmitField('Dodaj post')


class UpdateForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired()])
    description = StringField('Opis', validators=[DataRequired()])
    image = FileField('Zdjęcie', validators=[])
    submit = SubmitField('Zaktualizuj post')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.ALLOWED_EXTENSIONS

@posts_bp.route('/posts', methods=['GET', 'POST'])
@role_required('admin')
def posts():
    posts = app.Post.query.all()
    form = PostForm()
    error= ""
    if form.validate_on_submit():    
        image = form.image.data
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.app.config['UPLOAD_FOLDER'], filename))
        else:
            error = "Nieprawidłowe rozszerzenie pliku"
            return render_template('UploadPost.html', form=form, error=error)
        # Stwórz nowy post
        new_post = app.Post(title=form.title.data, content=form.description.data, image_name=image.filename)
        app.db.session.add(new_post)
        app.db.session.commit()
        
        return redirect(url_for('AdminPanel'))
    return render_template('AllPostsAdminView.html', form=form,posts=posts)

@posts_bp.route('/UpdatePost', methods=['GET', 'POST'])
@role_required('admin')
def UpdatePost():
    form = UpdateForm()
    if form.validate_on_submit():
        img = app.Img(img=form.image.data.read(), name=form.image.data.filename, mimetype=form.image.data.mimetype)
        app.db.session.add(img)
        app.db.session.commit()
        post = app.Post.query.get(form.post_id.data)
        post.title = form.title.data
        post.content = form.description.data
        post.image_id = img.id
        app.db.session.commit()
        return redirect(url_for('AdminPanel'))
    return render_template('UpdatePost.html', form=form)


@posts_bp.route('/delete_post/<post_id>')
@login_required
@role_required('admin')
def delete_post(post_id):
    Post_to_delete = app.Post.query.get(post_id)
    app.db.session.delete(Post_to_delete)
    app.db.session.commit()
    return redirect(url_for('AdminPanel'))

@posts_bp.route('/archiwum', methods=['GET', 'POST'])
def Archiwum():
    posts = app.Post.query.filter(app.Post.id <= app.Post.query.count())
    return render_template('archiwum.html', posts=posts)