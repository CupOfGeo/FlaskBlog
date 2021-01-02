import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir,'.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'magic'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATION = False

    MAIL_SERVER = 'localhost' #os.environ.get('MAIL_SERVER')
    MAIL_PORT = '8026' #int(os.environ.get('MAIL PORT') or 25)
    MAIL_USE_TLS = ''#os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = ''#os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = ''#os.environ.get('MAIL_PASSWORD')
    ADMINS = ['mazzeogeorge@gmail.com']

    POSTS_PER_PAGE = 20

    LANGUAGES = ['en','es']

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')

    ELASTICSEARCH_URL='http://localhost:9200'

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')




'''
export MAIL_SERVER=smtp.googlemail.com
export MAIL_PORT=587
export MAIL_USE_TLS=1
export MAIL_USERNAME=mazzeogeorge@gmail.com
export MAIL_PASSWORD=
'''
