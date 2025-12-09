from invoke import task


@task
def build(ctx):
    ctx.run("docker build -t project1:latest .")


@task
def up(ctx):
    ctx.run("docker compose up --build")


@task
def down(ctx):
    ctx.run("docker compose down")


@task
def dev(ctx):
    ctx.run("uv run uvicorn main:app --reload")


@task(pre=[build])
def test(ctx):
    ctx.run("uv run pytest tests/ -v")


@task
def clean(ctx):
    ctx.run("docker compose down -v")
    ctx.run("docker rmi project1:latest", warn=True)
