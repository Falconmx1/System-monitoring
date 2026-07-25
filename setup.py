from setuptools import setup, find_packages

setup(
    name="system-monitoring",
    version="1.0.0",
    author="Falconmx1",
    description="Herramienta multiplataforma para monitoreo de sistemas",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Falconmx1/System-monitoring",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.9.0",
        "flask>=3.0.0",
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
        "click>=8.1.7",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "sysmon=run:main",
        ],
    },
)
