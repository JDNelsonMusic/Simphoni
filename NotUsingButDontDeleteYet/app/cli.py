# app/cli.py

import click
from flask import current_app
from flask.cli import with_appcontext

@click.command('list-routes')
@with_appcontext
def list_routes():
    """List all routes and their endpoints."""
    import urllib
    output = []
    for rule in current_app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule.rule))
        output.append(line)
    for line in sorted(output):
        click.echo(line)
