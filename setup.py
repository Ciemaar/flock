from setuptools import setup

setup(
    name="closure_collector",
    version="0.0.2",
    packages=["flock"],
    url="http://ciemaar.com/flock",
    license="GPL v3",
    author="Andy Fundinger",
    author_email="Andy@ciemaar.com",
    description="A library for storing closures inside objects in an organized fashion.",
    install_requires=[
        "PyYAML>=6.0",
    ],
    extras_require={
        "test": ["pytest>=7.0", "hypothesis>=6.0"],
        "dev": ["ruff"],
    },
)
