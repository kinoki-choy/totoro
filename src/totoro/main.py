import typer

from totoro.utils import run
from totoro.settings import load_settings
from totoro import image, compose, server, spaces, restore


app = typer.Typer()
config = load_settings()

app.add_typer(image.app, name='image')
app.add_typer(server.app, name='server')
app.add_typer(spaces.app, name='spaces')
app.add_typer(compose.app, name='compose')
app.add_typer(restore.app, name='restore')

@app.callback()
def callback():
    """
    Totoro, your dependable DevOps buddy
    """

@app.command()
def init():
    """
    Set up Docker contexts
    """
    for context, host in config.get('hosts').items():
        run([
            f'docker context create {context} --docker=host=ssh://{host}'
        ])