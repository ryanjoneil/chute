from setuptools import setup

setup (
    name         = 'chute',
    version      = '0.2.dev',
    description  = 'A simple tool for Discrete Event Simulation in Python.',
    author       = "Ryan J. O'Neil",
    author_email = 'ryanjoneil@gmail.com',
    url          = 'https://github.com/ryanjoneil/chute',

    package_dir = {'': 'src'},
    packages    = ['chute'],
    scripts     = ['scripts/chute'],

    keywords    = 'discrete event simulation des operations research',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering :: Mathematics'
    ],

    install_requires = ['docopt']
)
