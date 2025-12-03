from invoke import task


@task
def test(c):
    """Run pytest unit tests"""
    print("Running pytest unit tests...")
    c.run("uv run pytest tests/ -v", pty=True)


@task
def format(c):
    """Format code with ruff"""
    print("Formatting code with ruff...")
    c.run("uv run ruff format ncaa/ tests/", pty=True)
    print("✓ Code formatting complete")


@task(format)
def lint(c):
    """Lint code with ruff (depends on format task)"""
    print("Linting code with ruff...")
    c.run("uv run ruff check ncaa/ tests/", pty=True)
    print("✓ Linting complete")


@task
def clean(c):
    """Clean up build artifacts and cache files"""
    print("Cleaning build artifacts...")
    c.run("rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__", warn=True)
    c.run("find . -type d -name __pycache__ -exec rm -rf {} +", warn=True)
    c.run("find . -type f -name '*.pyc' -delete", warn=True)
    print("✓ Cleanup complete")


@task(pre=[format, lint, test])
def build(c):
    """Run format, lint, and test tasks"""
    print("✓ Build complete - all checks passed!")
