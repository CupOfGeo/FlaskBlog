from app import db, login
from flask import current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from app.search import *

#DATABASE STUFF

#association Table for the many to many connection
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

class User(UserMixin, db.Model):
    #User Column in DATABASE
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    #the many to many relationship
    followed = db.relationship('User', secondary=followers,
    primaryjoin=(followers.c.follower_id == id),
    secondaryjoin=(followers.c.followed_id == id),
    backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    #lazy inidcates execution mode, dynamic means will not run untill requested

    def _repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        #turns email to random picture
        return 'https:www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count()>0

    def followed_posts(self):
        #joins the posts and followers Table and the posts from the followers
        #filters to only the posts from the users i follow
        #sory by decending timestamp
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id) #adds own posts to timeline
        return followed.union(own).order_by(Post.timestamp.desc())

    #returns a jwt token as string
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    #tries to decode it if it cant returns raise exception
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


# a class method is a special method tht is associated with the class
# and not a particular instance. Post.search or User.before_commit
#Its not an instance of a class but recives a class to operate on (cls not self)
class SearchableMixin(object):
    #to replace the list of object IDs with actual objects
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))

        #returns the the elasticsearch query results
        #and the total number search results
        return cls.query.filter(
        cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total


    @classmethod
    def before_commit(cls, session):
        #using the sessions object's _changes variable
        session._changes = {
        'add': list(session.new),
        'update': list(session.dirty),
        'delete': list(session.deleted)
        }

    #after the commit has happend go through the adds updates and deletes on the
    #elasticsearch side
    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)

        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)

        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    #helper to add all the posts
    #initalized the index from all the posts in the db
    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

#setting up db even listeners to get before and after commit events
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class Post(SearchableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    #one to many connection
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #they are connected by this
    language = db.Column(db.String(5))
    __searchable__ = ['body']

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
