from setuptools import find_packages, setup

setup(
    name="tap-yotpo",
    version="0.1.0",
    description="Singer.io tap for Yotpo (email stream example)",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "singer-python>=5.12.1",
        "requests>=2.20.0"
    ],
    entry_points="""
    [console_scripts]
    tap-yotpo=tap_yotpo.tap:main
    """
)
