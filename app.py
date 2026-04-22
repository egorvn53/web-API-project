from flask import Flask, request, jsonify, render_template_string, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-collection-manager-2026'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'collection.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ============ MODELS ============
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    items = db.relationship('Item', backref='user', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    item_type = db.Column(db.String(50), nullable=False, default='other')
    author = db.Column(db.String(200), nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='not_started')
    rating = db.Column(db.Float, nullable=True, default=0)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'item_type': self.item_type,
            'author': self.author,
            'genre': self.genre,
            'status': self.status,
            'rating': self.rating,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


# ============ FORMS ============
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_confirm = PasswordField('Подтвердить пароль', validators=[DataRequired(), EqualTo('password',
                                                                                               message='Пароли должны совпадать')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя уже занято')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже используется')


class ItemForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    item_type = SelectField('Тип',
                            choices=[('book', 'Книга'), ('game', 'Видеоигра'), ('movie', 'Фильм'), ('other', 'Другое')])
    author = StringField('Автор/Разработчик')
    genre = StringField('Жанр')
    status = SelectField('Статус', choices=[('not_started', 'Не начинал'), ('in_progress', 'В процессе'),
                                            ('completed', 'Завершено')])
    rating = StringField('Оценка (0-10)')
    notes = TextAreaField('Заметки')
    submit = SubmitField('Сохранить')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# ============ AUTH ROUTES ============
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    message = ''
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        else:
            message = "Неправильный email или пароль"

    return render_template('login.html', form=form, message=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    message = ''
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ============ MAIN ROUTES ============
@app.route('/')
def index():
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read(), current_user=current_user)


# ============ API ROUTES ============
@app.route('/api/items', methods=['GET'])
def get_items():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    search = request.args.get('search', '').lower()
    item_type = request.args.get('type', '')
    query = Item.query.filter_by(user_id=current_user.id)

    if search:
        query = query.filter(Item.title.ilike(f'%{search}%') | Item.author.ilike(f'%{search}%'))

    if item_type:
        query = query.filter(Item.item_type == item_type)

    items = query.all()
    return jsonify([item.to_dict() for item in items]), 200


@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(item.to_dict()), 200


@app.route('/api/items', methods=['POST'])
def create_item():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    item = Item(
        title=data.get('title'),
        item_type=data.get('item_type', 'other'),
        author=data.get('author'),
        genre=data.get('genre'),
        status=data.get('status', 'not_started'),
        rating=float(data.get('rating', 0)),
        notes=data.get('notes'),
        user_id=current_user.id
    )

    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    data = request.get_json()
    if 'title' in data:
        item.title = data['title']
    if 'item_type' in data:
        item.item_type = data['item_type']
    if 'author' in data:
        item.author = data['author']
    if 'genre' in data:
        item.genre = data['genre']
    if 'status' in data:
        item.status = data['status']
    if 'rating' in data:
        item.rating = float(data['rating'])
    if 'notes' in data:
        item.notes = data['notes']

    db.session.commit()
    return jsonify(item.to_dict()), 200


@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted successfully'}), 204


@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    total = Item.query.filter_by(user_id=current_user.id).count()
    by_type = {}
    by_status = {}

    for item in Item.query.filter_by(user_id=current_user.id).all():
        by_type[item.item_type] = by_type.get(item.item_type, 0) + 1
        by_status[item.status] = by_status.get(item.status, 0) + 1

    avg_rating = db.session.query(db.func.avg(Item.rating)).filter(Item.user_id == current_user.id).scalar() or 0

    return jsonify({
        'total_items': total,
        'by_type': by_type,
        'by_status': by_status,
        'average_rating': round(float(avg_rating), 2)
    }), 200


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)