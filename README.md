# django-migration-resolver-hook
Migration resolver for django, ensures that the migration nodes always stays in sync regardless of remote changes.


### Installation

```bash
$ pip install django-migration-resolver-hook==0.0.1
```

##### Poetry

```bash
poetry add -D django-migration-resolver-hook
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

##### Scenario

###### Remote
```text
|--- migrations
       |---- ...
       |---- 0007_auto_20200112_2328.py # Shared between remote and local repo
       |---- 0008_auto_20200113_4328.py # Only exists on remote
       |---- 0009_auto_20200114_4532.py
       |---- 0010_auto_20200115_1632.py

```

###### Local repo

```text
|--- migrations
       |---- ...
       |---- 0007_auto_20200112_2328.py  # Shared between remote and local repo
       |---- 0008_auto_20200114_5438.py  # Only exists locally which raises duplicate migration nodes errors.
```

###### Since this is now out of sync with the remote branch to sync changes reseeding the migration run:

```bash
$ migration_resolver --app-name my_app --last 0010_auto_20200115_1632 --conflict 0008_auto_20200114_5438 --commit --verbose
```

###### Output

```text
Fixing migrations...
Updating the conflicting migration file 0008_auto_20200114_5438.py
Succefully updated: 0008_auto_20200114_5438.py.
Renaming the migration file from 0008_auto_20200114_5438.py to 0011_auto_20200114_5438.py
Successfully renamed the migration file.
[my-test-branch c18fca41e] Resolved migration conflicts for 0008_auto_20200114_5438.py → 0011_auto_20200114_5438.py
1 file changed, 1 insertion(+), 1 deletion(-)
rename my_app/migrations/{0008_auto_20200114_5438.py => 0011_auto_20200114_5438.py} (99%)

```

For more options


```bash
$ migration_resolver --help
```

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


TODO:
- Auto detect and resolve errors with migration nodes.
- Add support for database unapply migration for case of applied migrations.
- Add support to rollback any changes if there are failures in the chain of operations.
- VCS support right now only git is supported (extend to mercurial).

