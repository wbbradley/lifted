"""Setup."""
import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="lifted",
    version="0.2.3",
    author="William Bradley",
    author_email="williambbradley@gmail.com",
    description="A minimal parser combinator library.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/wbbradley/python-parsing",
    package_data={"lifted": ["lifted/py.typed"]},
    packages=['lifted'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
