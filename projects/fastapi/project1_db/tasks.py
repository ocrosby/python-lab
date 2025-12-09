from invoke import task


@task(aliases=['b'])
def build(ctx):
    ctx.run("docker build -t project1:latest .")


@task(aliases=['u'])
def up(ctx):
    ctx.run("docker compose up --build")


@task(aliases=['d'])
def down(ctx):
    ctx.run("docker compose down")


@task(aliases=['v'])
def dev(ctx):
    ctx.run("uv run uvicorn main:app --reload")


@task(pre=[build], aliases=['t'])
def test(ctx):
    ctx.run("uv run pytest tests/ -v")


@task(aliases=['c'])
def clean(ctx):
    ctx.run("docker compose down -v")
    ctx.run("docker rmi project1:latest", warn=True)
