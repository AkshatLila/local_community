from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import os
from bson import ObjectId

app = Flask(__name__)
app.secret_key = os.environ.get(
    'SECRET_KEY') or 'your-secret-key-change-in-production'

# MongoDB Configuration
app.config['MONGO_URI'] = os.environ.get(
    'MONGO_URI') or 'mongodb://localhost:27017/hyperlocal_community'
mongo = PyMongo(app)

# Default Secretary Credentials
SECRETARY_EMAIL = "secretary@community.com"
SECRETARY_PASSWORD = "secretary123"

# Default Resident Credentials
RESIDENT_EMAIL = "resident@community.com"
RESIDENT_PASSWORD = "resident123"

# Helper Functions


def get_current_user():
    if 'user_id' in session:
        return mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return None


# Context processor to make current_user available in all templates
@app.context_processor
def inject_current_user():
    return {
        'current_user': get_current_user(),
        'format_datetime': format_datetime,
        'format_time_only': format_time_only
    }


@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to <br> tags for HTML display"""
    if text:
        return text.replace('\n', '<br>')
    return text


def is_secretary():
    user = get_current_user()
    return user and user.get('is_secretary', False)


def format_datetime(dt):
    """Convert UTC datetime to local time and format it"""
    if dt is None:
        return 'Recently'

    # Convert UTC to local time (assuming local timezone)
    # For a production app, you might want to use pytz or zoneinfo for proper timezone handling
    local_dt = dt.replace(tzinfo=timezone.utc).astimezone()
    return local_dt.strftime('%B %d, %Y at %I:%M %p')


def format_time_only(dt):
    """Convert UTC datetime to local time and format time only"""
    if dt is None:
        return 'Recently'

    # Convert UTC to local time
    local_dt = dt.replace(tzinfo=timezone.utc).astimezone()
    return local_dt.strftime('%I:%M %p')


@app.route('/')
def index():
    """Home page - redirects to appropriate area based on user type"""
    if 'user_id' in session:
        user = get_current_user()
        if user:
            if user.get('is_secretary'):
                return redirect(url_for('secretary_dashboard'))
            else:
                return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if it's the secretary login
        if email == SECRETARY_EMAIL and password == SECRETARY_PASSWORD:
            # Check if secretary user exists in database, if not create it
            secretary_user = mongo.db.users.find_one(
                {'email': SECRETARY_EMAIL})
            if not secretary_user:
                secretary_data = {
                    'name': 'Society Secretary',
                    'email': SECRETARY_EMAIL,
                    'apartment': 'Office',
                    'password': generate_password_hash(SECRETARY_PASSWORD),
                    'is_secretary': True,
                    'is_admin': False,
                    'created_at': datetime.utcnow()
                }
                mongo.db.users.insert_one(secretary_data)
                secretary_user = mongo.db.users.find_one(
                    {'email': SECRETARY_EMAIL})

            session['user_id'] = str(secretary_user['_id'])
            flash('Successfully logged in as Secretary!', 'success')
            return redirect(url_for('secretary_dashboard'))

        # Check if it's the default resident login
        if email == RESIDENT_EMAIL and password == RESIDENT_PASSWORD:
            # Check if default resident user exists in database, if not create it
            resident_user = mongo.db.users.find_one(
                {'email': RESIDENT_EMAIL})
            if not resident_user:
                resident_data = {
                    'name': 'Default Resident',
                    'email': RESIDENT_EMAIL,
                    'apartment': 'A-101',
                    'password': generate_password_hash(RESIDENT_PASSWORD),
                    'is_secretary': False,
                    'is_admin': False,
                    'created_at': datetime.utcnow()
                }
                mongo.db.users.insert_one(resident_data)
                resident_user = mongo.db.users.find_one(
                    {'email': RESIDENT_EMAIL})

            session['user_id'] = str(resident_user['_id'])
            flash('Successfully logged in as Resident!', 'success')
            return redirect(url_for('dashboard'))

        # Regular user login
        user = mongo.db.users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration - only for residents"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        apartment = request.form.get('apartment')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered.', 'error')
            return render_template('register.html')

        # Create user (only residents can register)
        user_data = {
            'name': name,
            'email': email,
            'apartment': apartment,
            'password': generate_password_hash(password),
            'is_secretary': False,
            'is_admin': False,
            'created_at': datetime.utcnow()
        }

        mongo.db.users.insert_one(user_data)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user_id', None)
    flash('Successfully logged out!', 'success')
    return redirect(url_for('index'))

# User Dashboard Routes


@app.route('/dashboard')
def dashboard():
    """User dashboard - redirects secretary to secretary dashboard"""
    user = get_current_user()
    if not user:
        flash('Please login to access dashboard.', 'error')
        return redirect(url_for('login'))

    # If user is secretary, redirect to secretary dashboard
    if user.get('is_secretary'):
        return redirect(url_for('secretary_dashboard'))

    # Get user's recent activity for regular residents
    notices = list(mongo.db.notices.find().sort('created_at', -1).limit(5))
    requests = list(mongo.db.service_requests.find(
        {'user_id': user['_id']}).sort('created_at', -1).limit(3))
    messages = list(mongo.db.messages.find().sort('created_at', -1).limit(5))

    return render_template('dashboard.html',
                           user=user,
                           notices=notices,
                           requests=requests,
                           messages=messages,
                           now=datetime.utcnow())


@app.route('/notices')
def notices():
    """View all notices - different views for secretary and residents"""
    user = get_current_user()
    if not user:
        flash('Please login to view notices.', 'error')
        return redirect(url_for('login'))

    notices = list(mongo.db.notices.find().sort('created_at', -1))

    # If user is secretary, redirect to secretary notices page
    if user.get('is_secretary'):
        return redirect(url_for('secretary_notices'))

    return render_template('notices.html', notices=notices)


@app.route('/service_requests', methods=['GET', 'POST'])
def service_requests():
    """Service requests management - different views for secretary and residents"""
    user = get_current_user()
    if not user:
        flash('Please login to access service requests.', 'error')
        return redirect(url_for('login'))

    # If user is secretary, redirect to secretary requests page
    if user.get('is_secretary'):
        return redirect(url_for('secretary_requests'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        priority = request.form.get('priority')

        request_data = {
            'title': title,
            'description': description,
            'category': category,
            'priority': priority,
            'status': 'pending',
            'user_id': user['_id'],
            'user_name': user['name'],
            'apartment': user['apartment'],
            'created_at': datetime.utcnow()
        }

        mongo.db.service_requests.insert_one(request_data)
        flash('Service request submitted successfully!', 'success')
        return redirect(url_for('service_requests'))

    requests = list(mongo.db.service_requests.find(
        {'user_id': user['_id']}).sort('created_at', -1))
    return render_template('service_requests.html', requests=requests)


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Community chat"""
    user = get_current_user()
    if not user:
        flash('Please login to access chat.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.form.get('message')
        if message.strip():
            message_data = {
                'content': message,
                'user_id': user['_id'],
                'user_name': user['name'],
                'is_secretary': user.get('is_secretary', False),
                'created_at': datetime.utcnow()
            }
            mongo.db.messages.insert_one(message_data)

    messages = list(mongo.db.messages.find().sort('created_at', -1).limit(50))
    messages.reverse()  # Show oldest first
    return render_template('chat.html', messages=messages)

# Profile Settings


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """Resident profile settings page: update name, apartment, email, and password"""
    user = get_current_user()
    if not user:
        flash('Please login to access your profile.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        apartment = (request.form.get('apartment') or '').strip()
        email = (request.form.get('email') or '').strip().lower()

        current_password = (request.form.get('current_password') or '')
        new_password = (request.form.get('new_password') or '')
        confirm_password = (request.form.get('confirm_password') or '')

        updates = {}

        # Basic profile fields
        if name and name != user.get('name'):
            updates['name'] = name
        if apartment and apartment != user.get('apartment'):
            updates['apartment'] = apartment
        if email and email != user.get('email'):
            # Ensure email uniqueness
            existing_user = mongo.db.users.find_one(
                {'email': email, '_id': {'$ne': user['_id']}})
            if existing_user:
                flash('This email is already in use by another account.', 'error')
                return redirect(url_for('profile'))
            updates['email'] = email

        # Password change (all-or-nothing)
        if current_password or new_password or confirm_password:
            if not current_password or not new_password or not confirm_password:
                flash(
                    'Please fill all password fields to change your password.', 'error')
                return redirect(url_for('profile'))
            if not check_password_hash(user['password'], current_password):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('profile'))
            if new_password != confirm_password:
                flash('New password and confirmation do not match.', 'error')
                return redirect(url_for('profile'))
            updates['password'] = generate_password_hash(new_password)

        if updates:
            mongo.db.users.update_one({'_id': user['_id']}, {'$set': updates})
            flash('Profile updated successfully!', 'success')
        else:
            flash('No changes to update.', 'info')

        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

# Secretary Routes


@app.route('/secretary')
def secretary_dashboard():
    """Secretary dashboard"""
    if not is_secretary():
        flash('Access denied. Secretary privileges required.', 'error')
        return redirect(url_for('login'))

    # Get statistics
    total_users = mongo.db.users.count_documents({'is_secretary': False})
    total_notices = mongo.db.notices.count_documents({})
    pending_requests = mongo.db.service_requests.count_documents(
        {'status': 'pending'})
    total_messages = mongo.db.messages.count_documents({})

    # Get recent activity
    recent_requests = list(
        mongo.db.service_requests.find().sort('created_at', -1).limit(5))
    recent_notices = list(
        mongo.db.notices.find().sort('created_at', -1).limit(3))

    return render_template('secretary_panel.html',
                           total_users=total_users,
                           total_notices=total_notices,
                           pending_requests=pending_requests,
                           total_messages=total_messages,
                           recent_requests=recent_requests,
                           recent_notices=recent_notices)


@app.route('/secretary/post_notice', methods=['GET', 'POST'])
def secretary_post_notice():
    """Secretary post notice form"""
    if not is_secretary():
        flash('Access denied. Secretary privileges required.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        priority = request.form.get('priority')

        notice_data = {
            'title': title,
            'content': content,
            'priority': priority,
            'created_at': datetime.utcnow()
        }

        mongo.db.notices.insert_one(notice_data)
        flash('Notice posted successfully!', 'success')
        return redirect(url_for('secretary_notices'))

    return render_template('secretary_post_notice.html')


@app.route('/secretary/notices', methods=['GET'])
def secretary_notices():
    """Secretary view all notices"""
    if not is_secretary():
        flash('Access denied. Secretary privileges required.', 'error')
        return redirect(url_for('login'))

    notices = list(mongo.db.notices.find().sort('created_at', -1))
    return render_template('secretary_notices.html', notices=notices)


@app.route('/secretary/requests')
def secretary_requests():
    """Secretary service requests management"""
    if not is_secretary():
        flash('Access denied. Secretary privileges required.', 'error')
        return redirect(url_for('login'))

    requests = list(mongo.db.service_requests.find().sort('created_at', -1))
    return render_template('secretary_requests.html', requests=requests)


@app.route('/secretary/update_request_status', methods=['POST'])
def update_request_status():
    """Update service request status"""
    if not is_secretary():
        return jsonify({'error': 'Access denied'}), 403

    request_id = request.form.get('request_id')
    status = request.form.get('status')

    mongo.db.service_requests.update_one(
        {'_id': ObjectId(request_id)},
        {'$set': {'status': status}}
    )

    return jsonify({'success': True})


@app.route('/secretary/users')
def secretary_users():
    """Secretary users management"""
    if not is_secretary():
        flash('Access denied. Secretary privileges required.', 'error')
        return redirect(url_for('login'))

    users = list(mongo.db.users.find(
        {'is_secretary': False}).sort('created_at', -1))
    return render_template('secretary_users.html', users=users)


@app.route('/secretary/delete_notice/<notice_id>')
def delete_notice(notice_id):
    """Delete a notice"""
    if not is_secretary():
        flash('Access denied. Secretary privileges required.', 'error')
        return redirect(url_for('login'))

    mongo.db.notices.delete_one({'_id': ObjectId(notice_id)})
    flash('Notice deleted successfully!', 'success')
    return redirect(url_for('secretary_notices'))


@app.route('/delete_message/<message_id>')
def delete_message(message_id):
    """Delete a chat message - allows users to delete their own messages or secretary to delete any"""
    user = get_current_user()
    if not user:
        flash('Please login to delete messages.', 'error')
        return redirect(url_for('login'))

    # Get the message to check ownership
    message = mongo.db.messages.find_one({'_id': ObjectId(message_id)})
    if not message:
        flash('Message not found.', 'error')
        return redirect(url_for('chat'))

    # Allow deletion if user is secretary or if user owns the message
    if user.get('is_secretary') or str(message['user_id']) == str(user['_id']):
        mongo.db.messages.delete_one({'_id': ObjectId(message_id)})
        flash('Message deleted successfully!', 'success')
    else:
        flash('Access denied. You can only delete your own messages.', 'error')

    return redirect(url_for('chat'))

# Error handlers


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
