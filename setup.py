"""Setup script for Capibara."""

from setuptools import setup, find_packages

setup(
    name="capibara",
    version="0.1.0",
    description="From idea to executable code, in one step",
    author="Capibara Team",
    author_email="team@capibara.dev",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.0",
        "httpx>=0.25.0",
        "click>=8.1.0",
        "rich>=13.7.0",
        "cryptography>=41.0.0",
        "jinja2>=3.1.0",
        "python-multipart>=0.0.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.7.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "capibara=capibara.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
