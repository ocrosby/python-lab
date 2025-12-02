import click


@click.command()
def hello() -> None:
    click.echo("Hello World!")


if __name__ == "__main__":
    hello()
