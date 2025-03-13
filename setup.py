from setuptools import setup, find_packages

setup(
    name="pdmInfra",
    version="0.2.1",
    packages=find_packages(include=["pdmInfra", "pdmInfra.*"]),
    url="https://github.com/pdmimpulse/pdmInfra.git",
    author="Yiyang Lu",
    author_email="y.lu@pdm-solutions.com",
    description="pdm impulse team infrastructure for AI application development",
    install_requires=[
        "requests",
    ],
)