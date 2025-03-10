from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="langchain_agent_project",
    version="0.1.0",
    author="Jabar42",
    description="A multi-model AI agent platform using LangChain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jabar42/langchain_agent_project",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "psycopg2-binary",
        "redis",
        "langchain",
        "openai",
        "anthropic",
        "cohere",
        "google-cloud-aiplatform",
    ],
    entry_points={
        "console_scripts": [
            "langchain-agent=src.cli:main",
        ],
    },
) 