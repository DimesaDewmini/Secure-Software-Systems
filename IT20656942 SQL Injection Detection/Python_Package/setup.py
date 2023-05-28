from setuptools import setup, find_packages

setup(
    name='injectionfree',
    version='0.1',
    description='This will detect SQL injection attacks. and notify the user.',
    author='Dewmi',
    author_email='dewmi@gmail.com',
    packages=['injectionfree'],
    install_requires=[
        'tensorflow',
        # Add any other dependencies your project requires
    ],
)
