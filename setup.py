from setuptools import setup, find_namespace_packages

setup(
    name='django-migration-resolver-hook',
    version='0.0.1',
    install_requires=['django>=1.11'],
    packages=find_namespace_packages(),
    entry_points = {
        'console_scripts': [
              'migration_resolver = bin.resolver:main'
          ]
    }
)
