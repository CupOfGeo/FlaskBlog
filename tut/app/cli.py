from app import app
import os
import click

#I dont use these comand just wanted to see how you make them
@app.cli.group()
def translate():
    pass

@translate.command()
def update():
    if os.system('pybabel extract -F babel.cfg -k _l -o message.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i message.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')

@translate.command()
def compile():
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')


@translate.comand()
@click.argument('lang') #arguments
def init(lang):
    #more stuff i wont use if intrested in more langaue stuff relooks at chapter 13
    pass
