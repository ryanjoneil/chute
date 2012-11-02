from distutils.core import setup

setup (
    name         = 'chute',
    version      = '0.0.1',
    description  = 'A simple tool for Discrete Event Simulation in Python.',
    author       = "Ryan J. O'Neil",
    author_email = 'ryanjoneil@gmail.com',
    url          = 'http://bitbucket.org/ryanjoneil/chute',
    download_url = 'http://bitbucket.org/ryanjoneil/chute/downloads',

    package_dir = {'': 'src'},
    packages    = ['chute'],
    scripts     = ['scripts/chute'],
    
    keywords    = 'discrete event simulation des operations research',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering :: Mathematics'
    ]
)
