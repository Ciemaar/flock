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
    requires=[
        "PyYAML",
        "wheel",
    ],
    tests_require=["pytest", "hypothesis"],
)
