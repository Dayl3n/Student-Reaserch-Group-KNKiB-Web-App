from flask import Flask
from flask_login import LoginManager, UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knkib.db'
app.config['SECRET_KEY'] = 'MDbgI2k2YULy9C8SnJslH67IG5XE4iyY'
app.config['Mail_SERVER'] = 'smtp.gmail.com'
app.config['Mail_PORT'] = 465
app.config['Mail_USERNAME'] = 'tak@gmail.com'
app.config['Mail_PASSWORD'] = 'password'
app.config['Mail_USE_TLS'] = False
app.config['Mail_USE_SSL'] = True
mail = Mail(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db=SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    tasks = db.relationship('Task', backref='user')
    events = db.relationship('EventsMembers', secondary='events_members', backref='user')

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
    members = db.relationship('EventsMembers', backref='event')

    def __repr__(self):
        return f'<Event {self.title}>'

class EventsMembers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<EventsMembers {self.id}>'

@app.route('/')
def test():
    return 'Hello World'

@login_manager.user_loader
def load_user(user_id):   
    return db.User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   
        app.run(debug=True)