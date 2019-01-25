import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

version = '0.3.1b2'

requires = [
    'eduid-am >= 0.7.2b0',
    'eduid-userdb >= 0.4.0b12',
]

testing_extras = [
    'nose==1.3.7',
    'nosexcover==1.0.11',
    'coverage==4.5.1',
]


setup(
    name='eduid_signup_amp',
    version=version,
    description='eduID Sign Up Attribute Manager Plugin',
    long_description=README + '\n\n' + CHANGES,
    # TODO: add classifiers
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='',
    author='NORDUnet A/S',
    url='https://github.com/SUNET/eduid-signup-amp',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={
        'testing': testing_extras,
    },
    test_suite='eduid_signup_amp',
    entry_points="""\
    [eduid_am.attribute_fetcher]
    eduid_signup = eduid_signup_amp:attribute_fetcher

    [eduid_am.plugin_init]
    eduid_signup = eduid_signup_amp:plugin_init

    """,
)
