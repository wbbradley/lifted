"""Setup."""
import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="lifted",
    version="0.1.0",
    author="William Bradley",
    author_email="williambbradley@gmail.com",
    description="A minimal parser combinator library.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/wbbradley/python-parsing",
    packages=setuptools.find_packages(exclude=["test_*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
