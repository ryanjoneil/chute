from setuptools import setup, find_packages

setup (
    name         = 'chute',
    version      = '0.0.1',
    description  = 'A micro-framework for Discrete Event Simulation',
    author       = "Ryan J. O'Neil",
    author_email = 'ryanjoneil@gmail.com',
    url          = 'http://code.google.com/p/chute/',
    download_url = 'http://code.google.com/p/chute/downloads/list',

    package_dir = {'': 'src'},
    packages    = find_packages('src', exclude=['tests', 'tests.*']),
    zip_safe    = True,
    test_suite  = 'tests',

    keywords    = 'discrete event simulation operations research',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering :: Mathematics'
    ]
)
