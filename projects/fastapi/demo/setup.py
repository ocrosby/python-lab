"""
This script is used to package the project into a distributable format.
"""

from setuptools import setup, find_packages

setup(
    name="example_project",
    version="0.1.0",
    description="This is an example project.",
    author="Omar Crosby",
    author_email="omar.crosby@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "uvicorn",
        "pytest",
        "pytest-bdd",
    ],
    extras_require={
        "dev": [
            "black",
            "isort",
            "flake8",
        ],
    },
    python_requires=">=3.7",
)
