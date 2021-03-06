import os
import sys

from setuptools import setup
from setuptools.command.install import install

from version import get_version

version = get_version()
with open('README.md') as f:
    long_description = f.read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != version:
            info = f"Git tag: {tag} does not match the version of this app: {version}"
            sys.exit(info)

setup(
    install_requires=["deepdiff"],
    version = version,
    author="Marco Caselli, Will Lohrmann",
    packages=["dast"],
    name = "dast",
    long_description=long_description,
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
