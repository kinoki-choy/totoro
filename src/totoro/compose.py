import typer

from totoro.utils import run
from totoro.validations import validate


app = typer.Typer()

@app.callback()
def callback():
    """
    Container orchestration
    """

@app.command()
def up(
    profile: str = typer.Argument(..., help='Services profile'),
    context: str = typer.Option('default', '--context', help='Docker context'),
    daemon: bool = typer.Option(True, '--no-daemon', help='Daemon')
):
    """
    Docker compose up

    TODO:
    - Additional environment variables via inline assignment
    """
    validate('context', context)
    validate('profile', profile)
    run([
        f'NGINX_TAG={context} docker --context {context} compose',
        f'--profile {profile} up',
        '-d' if daemon else '',
    ])

@app.command()
def down(
    profile: str = typer.Argument(..., help='Services profile'),
    context: str = typer.Option('default', '--context', help='Docker context')
):
    """
    Docker compose down
    """
    validate('context', context)
    validate('profile', profile)
    run([
        f'docker --context {context} compose',
        f'--profile {profile}',
        'down',
    ])

@app.command()
def exec(
    service: str = typer.Argument(...,help='Service for executing'),
    command: str = typer.Argument(..., help='Command to execute'),
    context: str = typer.Option('default', '--context', help='Docker context')
):
    """
    Docker compose execute
    """
    validate('service', service)
    validate('context', context)

    run([
        f'docker --context {context} compose exec',
        f'{service} {command}',
    ])