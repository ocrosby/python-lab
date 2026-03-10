"""Invoke build tasks for the weather MCP server project."""

from __future__ import annotations

from invoke import Context, task  # type: ignore[import-untyped]


@task
def install(ctx: Context) -> None:
    """Install all dependencies (including dev) via uv."""
    ctx.run("uv sync --all-extras --all-groups", pty=True)


@task
def fmt(ctx: Context) -> None:
    """Auto-format source and tests with ruff."""
    ctx.run("uv run ruff format src tests tasks.py", pty=True)


@task
def lint(ctx: Context) -> None:
    """Lint source and tests with ruff (check only)."""
    ctx.run("uv run ruff check src tests tasks.py", pty=True)


@task
def lint_fix(ctx: Context) -> None:
    """Lint and auto-fix source and tests with ruff."""
    ctx.run("uv run ruff check --fix src tests tasks.py", pty=True)


@task
def test(ctx: Context, verbose: bool = False, cov: bool = False) -> None:
    """Run the pytest test suite.

    Args:
        verbose: Pass -v to pytest for verbose output.
        cov:     Enable coverage reporting (requires pytest-cov).
    """
    flags = ""
    if verbose:
        flags += " -v"
    if cov:
        flags += " --cov=src/weather --cov-report=term-missing"
    ctx.run(f"uv run pytest{flags}", pty=True)


@task(pre=[fmt, lint, test])
def build(ctx: Context) -> None:  # noqa: ARG001
    """Run the full build pipeline: format → lint → test."""


@task
def run(ctx: Context) -> None:
    """Start the MCP weather server (stdio transport)."""
    ctx.run("uv run weather", pty=True)


@task
def clean(ctx: Context) -> None:
    """Remove build artefacts and caches."""
    ctx.run(
        "rm -rf dist build .ruff_cache .pytest_cache __pycache__ "
        "src/weather/__pycache__ tests/__pycache__ "
        ".coverage htmlcov",
        pty=True,
    )
