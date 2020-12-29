from app import app, db
from app.models import User, Post

#@app.shell_context_processors #giving me errors all of a sudden :(
def make_shell_context():
        return{'db': db, 'User': User, 'Post': Post}
