from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager,login_required, UserMixin, login_user,logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import auth, tasks,posts, events
from tasks import role_required


app = Flask(__name__, template_folder='templates')
app.register_blueprint(auth.auth_bp)
app.register_blueprint(tasks.tasks_bp)
app.register_blueprint(posts.posts_bp)
app.register_blueprint(events.events_bp)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knkib.db'
app.config['UPLOAD_FOLDER'] = 'static/images/'
app.config['SECRET_KEY'] = 'MDbgI2k2YULy9C8SnJslH67IG5XE4iyY'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db=SQLAlchemy(app)

EventMebers = db.Table('events_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    tasks = db.relationship('Task', backref='user')
    events = db.relationship('Event', secondary=EventMebers, backref='user')

    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    deadline = db.Column(db.DateTime())   
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Task {self.title}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime())
    members = db.relationship('User', secondary='events_members', backref='event')

    def __repr__(self):
        return f'<Event {self.title}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    image_name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'

@app.route('/')
def start():
    posts = Post.query.order_by(Post.id.desc()).limit(4).all()
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return render_template('index.html',posts=posts, admin=True)
        else:
            return render_template('index.html',posts=posts, admin=False)
    return render_template('index.html',posts=posts)

@app.route('/calendar')
def calendar():
    all_events = Event.query.all()
    return render_template('Calendar.html', all_events=all_events)

@app.route('/about')
def aboutus():
    return render_template('about.html')

@login_manager.user_loader
def load_user(user_id):   
    return User.query.get(int(user_id))

@app.route('/AdminPanel', methods=['GET', 'POST'])
def AdminPanel():
    return render_template('AdminPanel.html', admin=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))

@app.route('/update_user/<int:user_id>')
@login_required
@role_required('admin')
def update_user(user_id):
    user_to_update = User.query.get(user_id)
    if user_to_update:
        user_to_update.role = 'admin'
        db.session.commit()
        return f'Zaktualizowano użytkownika o ID {user_id}'
    else:
        return f'Użytkownik o ID {user_id} nie istnieje.'
    

@app.route('/task', methods=['GET', 'POST'])
@login_required
def tasks():
    if(current_user.role == 'admin'):
        return redirect(url_for('tasks.tasksAdmin'))
    else:
        return redirect(url_for('tasks.tasks'))
    



# @app.route('/dropTable')
# def dropTable():
#     Img.__table__.drop(db.engine)
#     Post.__table__.drop(db.engine)
#     return 'Usunięto tabele'    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   
        app.run(debug=True)