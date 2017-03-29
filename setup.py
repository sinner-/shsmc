""" shsmd
"""

from setuptools import setup, find_packages

setup(
    name='shsmc',
    version='1.0',
    url='https://github.com/sinner-/shsmc',
    author='Sina Sadeghi',
    install_requires=['requests>=2.13.0',
                      'Click>=6.7',
                      'PyNaCl>=1.0.1'],
    description='Python client for Self Hosted Secure Messaging Daemon',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'shsmc = shsmc.cmd.cli:main',
        ]},
)
