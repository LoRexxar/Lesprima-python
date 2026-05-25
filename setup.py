try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

from esprima import version


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read().strip()
    except IOError:
        return ''


setup(
    name='esprima',
    version=version,
    author='German M. Bravo (Kronuz)',
    author_email='german.mb@gmail.com',
    packages=[
        'esprima',
    ],
    url='https://github.com/Kronuz/esprima-python',
    license='BSD License',
    keywords='esprima ecmascript javascript parser ast',
    description="ECMAScript parsing infrastructure for multipurpose analysis in Python",
    long_description=read('README'),
    python_requires='>=3.11',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
        "Topic :: Text Processing :: General",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'console_scripts': [
            'esprima = esprima.__main__:main',
        ]
    },
)
