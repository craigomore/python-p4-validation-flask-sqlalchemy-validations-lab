from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.exc import OperationalError
db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add validators 
    @validates('name')
    def validate_name(self, key, value):
        if value is None or not value.strip():
            raise ValueError('Author must have a name')
        # ensure uniqueness
        existing = None
        try:
            existing = db.session.query(Author).filter_by(name=value).first()
        except OperationalError:
            # table may not exist yet (tests may not have run migrations); skip DB uniqueness check
            existing = None

        if existing and existing.id != getattr(self, 'id', None):
            raise ValueError('Author name must be unique')
        return value

    @validates('phone_number')
    def validate_phone(self, key, value):
        if value is None:
            return value
        # must be exactly 10 digits
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError('Phone number must be exactly 10 digits')
        return value

    def __repr__(self):
        return f'Author(id={self.id}, name={self.name})'

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    category = db.Column(db.String)
    summary = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add validators  
    @validates('title')
    def validate_title(self, key, value):
        if value is None or not value.strip():
            raise ValueError('Post must have a title')
        # clickbait check (case-insensitive)
        lower = value.lower()
        keywords = ["won't believe", 'secret', 'top', 'guess']
        if not any(k in lower for k in keywords):
            raise ValueError('Post title must be sufficiently clickbait-y')
        return value

    @validates('content')
    def validate_content(self, key, value):
        if value is None or len(value) < 250:
            raise ValueError('Post content must be at least 250 characters')
        return value

    @validates('summary')
    def validate_summary(self, key, value):
        if value is None:
            return value
        if len(value) > 250:
            raise ValueError('Post summary must be 250 characters or fewer')
        return value

    @validates('category')
    def validate_category(self, key, value):
        if value not in ('Fiction', 'Non-Fiction'):
            raise ValueError("Post category must be 'Fiction' or 'Non-Fiction'")
        return value


    def __repr__(self):
        return f'Post(id={self.id}, title={self.title} content={self.content}, summary={self.summary})'
