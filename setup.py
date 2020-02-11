import io
import os

from setuptools import setup, find_namespace_packages

deploy_requires = [
    'bump2version==0.5.11',
    'readme_renderer[md]',
    'changes==0.7.0',
    'git-changelog==0.1.0',
    'twine==1.3.1',
]


BASE_DIR = os.path.dirname(__file__)
README_PATH = os.path.join(BASE_DIR, 'README.md')
LONG_DESCRIPTION_TYPE = 'text/markdown'

if os.path.isfile(README_PATH):
    with io.open(README_PATH, encoding='utf-8') as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = ''

VERSION = (0, 1, 6)

version = '.'.join(map(str, VERSION))

setup(
    name='django-migration-resolver-hook',
    version=version,
    install_requires=['django>=1.11'],
    python_requires='>=3.6',
    description='Resolve migration conflicts.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_TYPE,
    author='Tonye Jack',
    author_email='jtonye@ymail.com',
    maintainer='Tonye Jack',
    maintainer_email='jtonye@ymail.com',
    url='https://github.com/jackton1/django-migration-resolver-hook.git',
    license='MIT',
    keywords=[
        'django',
        'django migration',
        'django migration resolver',
        'django migration node conflict resolver',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
    ],

    packages=find_namespace_packages(),
    entry_points = {
        'console_scripts': [
              'migration_resolver = bin.resolver:main',
              'auto_migration_resolver = bin.auto_resolver:main',
          ]
    },
    extras_require={
        'deploy': deploy_requires,
        'development': ['pip-tools==4.4.1'],
    },
)
