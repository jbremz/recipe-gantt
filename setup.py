from setuptools import find_packages, setup

setup(
    name="recipe_gantt",
    version="0.1.0",
    description="AI-generated gantt charts for recipes",
    author="Jim Bremner",
    url="https://github.com/jbremz/recipe-gantt",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
