from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ScreenTranslator",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.9',
    entry_points = {
        "console_scripts": [
            "ScreenTranslator = ScreenTranslator.__main__:main",
        ]
    }
)