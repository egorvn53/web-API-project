from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'collection.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

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

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template_string(open('index.html').read())

@app.route('/api/items', methods=['GET'])
def get_items():
    search = request.args.get('search', '').lower()
    item_type = request.args.get('type', '')
    query = Item.query
    if search:
        query = query.filter(Item.title.ilike(f'%{search}%') | Item.author.ilike(f'%{search}%'))
    if item_type:
        query = query.filter(Item.item_type == item_type)
    items = query.all()
    return jsonify([item.to_dict() for item in items]), 200

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(item.to_dict()), 200

@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    item = Item(
        title=data.get('title'),
        item_type=data.get('item_type', 'other'),
        author=data.get('author'),
        genre=data.get('genre'),
        status=data.get('status', 'not_started'),
        rating=data.get('rating', 0),
        notes=data.get('notes')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get(item_id)
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
        item.rating = data['rating']
    if 'notes' in data:
        item.notes = data['notes']
    db.session.commit()
    return jsonify(item.to_dict()), 200

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted successfully'}), 204

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = Item.query.count()
    by_type = {}
    by_status = {}
    for item in Item.query.all():
        by_type[item.item_type] = by_type.get(item.item_type, 0) + 1
        by_status[item.status] = by_status.get(item.status, 0) + 1
    avg_rating = db.session.query(db.func.avg(Item.rating)).scalar() or 0
    return jsonify({
        'total_items': total,
        'by_type': by_type,
        'by_status': by_status,
        'average_rating': round(avg_rating, 2)
    }), 200

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000