import click


@click.group()
def cli() -> None:
    pass


@cli.command()
def initdb() -> None:
    click.echo("Initialized the database")


@cli.command()
def dropdb():
    click.echo("Dropped the database")


if __name__ == "__main__":
    cli()
