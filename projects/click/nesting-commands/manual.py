import click


@click.group()
def cli() -> None:
    pass


@click.command()
def initdb() -> None:
    click.echo("Initialized the database")


@click.command()
def dropdb():
    click.echo("Dropped the database")


cli.add_command(initdb)
cli.add_command(dropdb)

if __name__ == "__main__":
    cli()
