from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///10000hours.db'
db = SQLAlchemy(app)

# Models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    entries = db.relationship('TimeEntry', backref='category', lazy=True)

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    clock_in = db.Column(db.DateTime)
    clock_out = db.Column(db.DateTime)
    manual_hours = db.Column(db.Float)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

# Create tables
with app.app_context():
    db.create_all()
    # Add some default categories if none exist
    if not Category.query.first():
        default_categories = ['Work', 'Meeting', 'Break', 'Project']
        for cat_name in default_categories:
            db.session.add(Category(name=cat_name))
        db.session.commit()

@app.route('/')
def index():
    categories = Category.query.all()
    entries = TimeEntry.query.order_by(TimeEntry.date.desc()).all()
    return render_template('index.html', categories=categories, entries=entries)

@app.route('/start_timer', methods=['POST'])
def start_timer():
    category_id = request.form.get('category_id')
    description = request.form.get('description')

    entry = TimeEntry(
        category_id=category_id,
        description=description,
        clock_in=datetime.now()
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'entry_id': entry.id})

@app.route('/stop_timer/<int:entry_id>', methods=['POST'])
def stop_timer(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    entry.clock_out = datetime.now()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/manual_entry', methods=['POST'])
def manual_entry():
    category_id = request.form.get('category_id')
    description = request.form.get('description')
    hours = float(request.form.get('hours'))
    date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')

    entry = TimeEntry(
        category_id=category_id,
        description=description,
        manual_hours=hours,
        date=date
    )
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)