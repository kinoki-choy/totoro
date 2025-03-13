import os
import typer
from rich.console import Console

from totoro.utils import run
from totoro.spaces import get_backups
from totoro.validations import validate
from totoro.settings import load_settings


app = typer.Typer()
console = Console()
config = load_settings()

@app.callback()
def callback():
    """
    Restore databases, files and translations
    """

@app.command()
def db(
    db_name: str = typer.Argument(..., help='Database name'),
    filename: str = typer.Argument(None, help='Backup filename'),
    context: str = typer.Option('default', '--context', help='Docker context'),
    docker: bool = typer.Option(True, '--no-docker', help='Running on docker?'),
    initial_restore:  bool = typer.Option(False, '--initial-restore', help='Initial restore.'
    'Used in conjunction when `docker` is True')
):
    """
    Downloads the database backup, drops and recreates the database, then restores the backup
    """
    validate('db', db_name)
    validate('context', context)

    if not os.environ.get('PGPASSWORD'):
        raise typer.BadParameter(
            'Postgres password is missing.\nEnsure that PGPASSWORD is set as environment variable.'
        )

    if not filename:
        run(['totoro spaces list db'], stdout=False)
        input_option = console.input(
            f'[green][bold]Select an option (default is 1): [/bold][/green]'
        ) or 1
        filename = get_backups('db', 10)[int(input_option)-1]

    def _download():
        run([
            f'docker --context {context} compose exec web' if docker else '',
            f'totoro spaces download db {filename}'
        ])

    def _restore():
        restore_cmd = ' '.join([
            f'pv {config.get("db_downloads_dir")}/{filename} |',
            'pg_restore --clean --if-exists',
            '-h localhost -p 5432' if not docker else '',
            f'-U {config.get("db_user")} -d {db_name}',
        ]).strip()

        run([
            f'docker --context {context} compose exec db' if docker else '',
            f"bash -c '{restore_cmd}'" if docker else restore_cmd
        ])

    if docker and initial_restore:
        run([
            f'docker --context {context} compose run',
            '-e PGPASSWORD=$PGPASSWORD --name=postgres --remove-orphans -d db'
        ])

        run([
            f'docker --context {context} compose run',
            '--entrypoint sleep --name web_app --remove-orphans -d web infinity'
        ])

        _download()
        _restore()

        run([
            f'docker --context {context} container rm -f web_app postgres'
            ])
        return

    _download()
    _restore()