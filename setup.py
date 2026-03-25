from setuptools import setup, find_packages

setup(
    name="ubounty",
    version="0.1.0",
    description="Enable maintainers to clear their backlog with one command.",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "ubounty=ubounty.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)