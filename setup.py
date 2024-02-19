import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="syncode",
    version="0.1",
    author="Shubham Ugare",
    author_email="shubhamugare@gmail.com",
    description="This package provides the tool for grammar augmented LLM generation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shubhamugare/syncode",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)