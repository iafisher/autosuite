from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='testgen',
    version='0.1',
    description='Auto-generate unit tests from interactive shell sessions',
    license='MIT',
    long_description=long_description,
    author='Ian Fisher',
    author_email='iafisher@protonmail.com',
    packages=find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Topic :: Software Development :: Testing'
    ),
)
