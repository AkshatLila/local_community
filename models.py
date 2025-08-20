from datetime import datetime
from bson import ObjectId


class User:
    def __init__(self, name, email, apartment, password, is_secretary=False, is_admin=False):
        self.name = name
        self.email = email
        self.apartment = apartment
        self.password = password
        self.is_secretary = is_secretary
        self.is_admin = is_admin
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'apartment': self.apartment,
            'password': self.password,
            'is_secretary': self.is_secretary,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }


class Notice:
    def __init__(self, title, content, priority):
        self.title = title
        self.content = content
        self.priority = priority  # urgent, high, medium, low
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'created_at': self.created_at
        }


class ServiceRequest:
    def __init__(self, title, description, category, priority, user_id, user_name, apartment):
        self.title = title
        self.description = description
        self.category = category  # plumbing, electrical, carpentry, cleaning, security, other
        self.priority = priority  # urgent, high, medium, low
        self.status = 'pending'  # pending, in_progress, resolved, cancelled
        self.user_id = user_id
        self.user_name = user_name
        self.apartment = apartment
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'apartment': self.apartment,
            'created_at': self.created_at
        }


class ChatMessage:
    def __init__(self, content, user_id, user_name):
        self.content = content
        self.user_id = user_id
        self.user_name = user_name
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'content': self.content,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'created_at': self.created_at
        }

# Database helper functions


def create_indexes(db):
    """Create database indexes for better performance"""
    # Users collection indexes
    db.users.create_index('email', unique=True)
    db.users.create_index('apartment')

    # Notices collection indexes
    db.notices.create_index('created_at')
    db.notices.create_index('priority')

    # Service requests collection indexes
    db.service_requests.create_index('user_id')
    db.service_requests.create_index('status')
    db.service_requests.create_index('created_at')
    db.service_requests.create_index('category')

    # Messages collection indexes
    db.messages.create_index('created_at')
    db.messages.create_index('user_id')


def get_priority_color(priority):
    """Get color class for priority levels"""
    colors = {
        'urgent': 'danger',
        'high': 'warning',
        'medium': 'info',
        'low': 'success'
    }
    return colors.get(priority, 'secondary')


def get_status_color(status):
    """Get color class for status levels"""
    colors = {
        'pending': 'warning',
        'in_progress': 'info',
        'resolved': 'success',
        'cancelled': 'danger'
    }
    return colors.get(status, 'secondary')


def format_datetime(dt):
    """Format datetime for display"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    return dt.strftime('%B %d, %Y at %I:%M %p')


def get_time_ago(dt):
    """Get relative time string"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))

    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"
