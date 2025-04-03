from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Detect environment (local vs. Heroku)
IS_PRODUCTION = os.getenv("FLASK_ENV") == "production"

# Use the correct subpath for deployment
SUBPATH = "/10000hours" if IS_PRODUCTION else ""

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///10000hours.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    categories = db.relationship('Category', backref='user', lazy=True)
    entries = db.relationship('TimeEntry', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entries = db.relationship('TimeEntry', backref='category', lazy=True)

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    clock_in = db.Column(db.DateTime)
    clock_out = db.Column(db.DateTime)
    manual_hours = db.Column(db.Float)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    # db.drop_all() 
    db.create_all()

# Add prefix to all URLs if in production
def url_for_with_subpath(*args, **kwargs):
    if IS_PRODUCTION:
        return SUBPATH + url_for(*args, **kwargs)
    return url_for(*args, **kwargs)

# Make the custom url_for available in templates
app.jinja_env.globals['url_for_with_subpath'] = url_for_with_subpath

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for_with_subpath('dashboard'))
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.desc()).all()
    
    # Calculate total hours
    total_hours = 0
    for entry in entries:
        if entry.manual_hours:
            total_hours += entry.manual_hours
        elif entry.clock_in and entry.clock_out:
            duration = entry.clock_out - entry.clock_in
            total_hours += duration.total_seconds() / 3600
    
    return render_template('dashboard.html', 
                          categories=categories, 
                          entries=entries,
                          total_hours=total_hours)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for_with_subpath('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.')
            return redirect(url_for_with_subpath('register'))
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for_with_subpath('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for_with_subpath('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for_with_subpath('register'))
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Add default categories for the new user
        default_categories = ['Work', 'Meeting', 'Break', 'Project']
        for cat_name in default_categories:
            db.session.add(Category(name=cat_name, user_id=new_user.id))
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for_with_subpath('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for_with_subpath('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for_with_subpath('login'))
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for_with_subpath('dashboard')
            
        return redirect(next_page)
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for_with_subpath('home'))

@app.route('/start_timer', methods=['POST'])
@login_required
def start_timer():
    category_id = request.form.get('category_id')
    description = request.form.get('description')

    # Verify category belongs to user
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    entry = TimeEntry(
        category_id=category_id,
        description=description,
        clock_in=datetime.now(),
        user_id=current_user.id
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({'entry_id': entry.id})

@app.route('/stop_timer/<int:entry_id>', methods=['POST'])
@login_required
def stop_timer(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    
    # Verify entry belongs to user
    if entry.user_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for_with_subpath('dashboard'))
    
    entry.clock_out = datetime.now()
    db.session.commit()
    return redirect(url_for_with_subpath('dashboard'))

@app.route('/manual_entry', methods=['POST'])
@login_required
def manual_entry():
    category_id = request.form.get('category_id')
    description = request.form.get('description')
    hours = float(request.form.get('hours'))
    date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')

    # Verify category belongs to user
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for_with_subpath('dashboard'))

    entry = TimeEntry(
        category_id=category_id,
        description=description,
        manual_hours=hours,
        date=date,
        user_id=current_user.id
    )
    db.session.add(entry)
    db.session.commit()
    return redirect(url_for_with_subpath('dashboard'))

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            category = Category(name=name, user_id=current_user.id)
            db.session.add(category)
            db.session.commit()
    
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories.html', categories=categories)

@app.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Verify category belongs to user
    if category.user_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for_with_subpath('manage_categories'))
    
    # Check if category has entries
    if TimeEntry.query.filter_by(category_id=category_id).first():
        flash('Cannot delete category with existing entries')
        return redirect(url_for_with_subpath('manage_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted')
    return redirect(url_for_with_subpath('manage_categories'))

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    
    # Verify entry belongs to user
    if entry.user_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for_with_subpath('dashboard'))
    
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted')
    return redirect(url_for_with_subpath('dashboard'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validation
    if username and username != current_user.username:
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for_with_subpath('profile'))
        current_user.username = username
    
    if email and email != current_user.email:
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for_with_subpath('profile'))
        current_user.email = email
    
    # Password change
    if current_password and new_password:
        if not current_user.check_password(current_password):
            flash('Current password is incorrect')
            return redirect(url_for_with_subpath('profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match')
            return redirect(url_for_with_subpath('profile'))
        
        current_user.set_password(new_password)
    
    db.session.commit()
    flash('Profile updated successfully')
    return redirect(url_for_with_subpath('profile'))

@app.route('/stats')
@login_required
def stats():
    # Get all entries for the current user
    entries = TimeEntry.query.filter_by(user_id=current_user.id).all()
    
    # Calculate statistics
    total_hours = 0
    category_hours = {}
    daily_hours = {}
    
    for entry in entries:
        # Calculate hours for this entry
        hours = 0
        if entry.manual_hours:
            hours = entry.manual_hours
        elif entry.clock_in and entry.clock_out:
            duration = entry.clock_out - entry.clock_in
            hours = duration.total_seconds() / 3600
        
        total_hours += hours
        
        # Add to category stats
        category_name = entry.category.name
        if category_name in category_hours:
            category_hours[category_name] += hours
        else:
            category_hours[category_name] = hours
        
        # Add to daily stats
        date_str = entry.date.strftime('%Y-%m-%d')
        if date_str in daily_hours:
            daily_hours[date_str] += hours
        else:
            daily_hours[date_str] = hours
    
    return render_template('stats.html', 
                          total_hours=total_hours,
                          category_hours=category_hours,
                          daily_hours=daily_hours)

@app.route('/check_active_timer')
@login_required
def check_active_timer():
    # Find any active timer for the current user
    active_entry = TimeEntry.query.filter_by(
        user_id=current_user.id,
        clock_in=not None,
        clock_out=None
    ).first()
    
    if active_entry:
        return jsonify({
            'active_timer': True,
            'entry_id': active_entry.id,
            'category_id': active_entry.category_id,
            'description': active_entry.description
        })
    else:
        return jsonify({'active_timer': False})

@app.context_processor
def inject_today():
    """Add today's date to all templates"""
    return {'today': datetime.now().strftime('%Y-%m-%d')}

# Add context processor for the subpath
@app.context_processor
def inject_subpath():
    """Add subpath to all templates"""
    return {'subpath': SUBPATH}

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))

    # Bind to 0.0.0.0 to listen on all interfaces
    app.run(host="0.0.0.0", port=port, debug=not IS_PRODUCTION)