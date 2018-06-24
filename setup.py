from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='autosuite',
    version='0.1',
    description='Auto-generate unit tests from interactive shell sessions',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ian Fisher',
    author_email='iafisher@protonmail.com',
    packages=find_packages(),
    classifiers=(
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Testing'
    ),
    project_urls={
        'Source': 'https://github.com/iafisher/autosuite',
    }
)
