from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="configlake",
    version="1.0.0",
    author="Govind Deshmukh",
    author_email="govind.ub47@gmail.com",
    description="Python client library for Config Lake - Centralized configuration and secrets management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Govind-Deshmukh/configlake-py",
    project_urls={
        "Bug Tracker": "https://github.com/Govind-Deshmukh/configlake-py/issues",
        "Documentation": "https://github.com/Govind-Deshmukh/configlake-py#readme",
        "Source Code": "https://github.com/Govind-Deshmukh/configlake-py",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Security :: Cryptography",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="config configuration secrets management environment variables",
    include_package_data=True,
    zip_safe=False,
)