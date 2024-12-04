"""Define the database model/tables."""
from app import db
from flask_login import UserMixin

class Following(db.Model):
    """Model for users that a user follows."""

    __tablename__ = 'following'
    follower_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    following_id = db.Column(db.ForeignKey('user.id'), primary_key=True)


class User(db.Model, UserMixin):
    """Model for users."""

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    date_joined = db.Column(db.Date, nullable=False)
    bio = db.Column(db.String(50))
    # https://stackoverflow.com/questions/25177451/sqlalchemy-self-referential-many-to-many-relationship-with-extra-column
    follower = db.relationship('Following' ,backref='follower',
                               primaryjoin=id == Following.follower_id,
                               cascade="all, delete-orphan")
    following = db.relationship('Following',backref='following',
                                primaryjoin=id == Following.following_id,
                                cascade="all, delete-orphan")
    posts = db.relationship('Post', backref='user', lazy='dynamic',
                            cascade="all, delete-orphan")
    reading_list = db.relationship('ReadingList', backref='user',
                                   lazy='dynamic',
                                   cascade="all, delete-orphan")
    liked = db.relationship('Liked', backref='user', lazy='dynamic',
                            cascade="all, delete-orphan")


class Book(db.Model):
    """Model for books."""
    
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(100))


class ReadingList(db.Model):
    """Model for reading list."""

    __tablename__ = 'reading_list'
    user_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.ForeignKey('book.id'), primary_key=True)


class Post(db.Model):
    """Model for posts of books that the user has read."""

    __tablename__ = 'post'
    user_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    book_id = db.Column(db.ForeignKey('book.id'), primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Integer)
    review = db.Column(db.String(500))
    likes = db.Column(db.Integer, nullable=False)
    books = db.relationship('Book', backref='post')


class Liked(db.Model):
    """Model for posts that user had liked."""

    __tablename__ = 'liked'
    user_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    post_user_id = db.Column(db.ForeignKey('post.user_id'), primary_key=True)
    post_book_id = db.Column(db.ForeignKey('post.book_id'), primary_key=True)
