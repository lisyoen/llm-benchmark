from setuptools import setup, find_packages
import os

# README 읽기
def read_long_description():
    with open("README.md", encoding="utf-8") as f:
        return f.read()

# requirements.txt 읽기
def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return [
        "httpx>=0.27.0",
        "pyyaml>=6.0.1",
        "pandas>=2.2.0",
    ]

setup(
    name="llm-benchmark",
    version="1.0.0",
    author="S-Core",
    author_email="",
    description="Run Bench - LLM 추론 서버 성능 벤치마크 도구",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(include=["scripts", "scripts.*"]),
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Benchmark",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        "console_scripts": [
            "llm-bench=scripts.run_bench_interactive:main",
            "llm-bench-cli=scripts.run_bench:main",
        ],
    },
    package_data={
        "": ["configs/*.yaml"],
    },
    project_urls={
        "Bug Reports": "",
        "Source": "",
    },
)
