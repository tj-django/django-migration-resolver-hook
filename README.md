# django-migration-resolver-hook
Migration resolver for django, ensuring that the migration nodes always stays in sync regardless of merge changes.


### Installation

```bash
$ pip install django-migration-resolver-hook==0.0.1
```

##### Poetry

```bash
poetry add -D 
```


##### Using extras 
```python
setup(
    ...
    extras_require={
        'development': [
            ...
            'django-migration-resolver-hook==0.0.1',
            ...
        ]
    },
)
```


### Usage

```
Usage: migration_resolver [-h] [--auto-detect AUTO_DETECT] --app-name APP_NAME
                          --last LAST --conflict CONFLICT

Fix vcs errors with duplicate migration nodes.

optional arguments:
  -h, --help            show this help message and exit
  --auto-detect AUTO_DETECT
                        Auto-detect and fix migration errors. (Not supported)
  --app-name APP_NAME   App Name
  --last LAST           The glob/full name of the final migration file.
  --conflict CONFLICT   The glob/full name of the final migration file with
                        the conflict.

```


Using vsc (git/mercurial) when the remote has a migration files that conflict with previous
migrations you have locally.


Version 0:
Manually specify the last migration module to seed the conflicting migration.

```
$ migration_resolver --app-name content_library --last 0540_auto_20200115_1632 --conflict  
0538_auto_20200115_2208
```

