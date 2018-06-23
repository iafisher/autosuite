from setuptools import setup

with open('README', 'r') as f:
    long_description = f.read()

setup(
    name='testgen',
    version='0.1',
    description='Auto-generate unit tests from interactive shell sessions',
    license='MIT',
    long_description=long_description,
    author='Ian Fisher',
    author_email='iafisher@protonmail.com',
    packages=['testgen'],
    install_requires=[]
)
