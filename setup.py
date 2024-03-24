import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the content of the requirements.txt file	
with open('requirements.txt', 'r', encoding='utf-8') as f:	
    requirements = f.read().splitlines()

setuptools.setup(
    name="syncode",
    version="0.1",
    author="Shubham Ugare",
    author_email="shubhamugare@gmail.com",
    description="This package provides the tool for grammar augmented LLM generation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shubhamugare/syncode",
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",	
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)