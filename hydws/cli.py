from pathlib import Path

import requests
import typer

from hydws.datamodel.base import drop_db, init_db
from hydws.datamodel.orm import (Borehole, BoreholeSection,  # noqa
                                 HydraulicSample)

app = typer.Typer(add_completion=False)
db = typer.Typer()
api = typer.Typer()

app.add_typer(db, name='db',
              help='Database Commands')
app.add_typer(api, name='api', help='Interact with API.')


@db.command('drop')
def drop_database():
    '''
    Drop all tables.
    '''
    drop_db()
    typer.echo('Tables dropped.')


@db.command('init')
def initialize_database():
    '''
    Create all tables.
    '''
    init_db()
    typer.echo('Tables created.')


@api.command('post')
def post_file(file: Path):
    url = 'http://localhost:8000/hydws/v1/boreholes'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    r = requests.post(url, data=open(file, 'rb'), headers=headers)
    typer.echo(r.text)
