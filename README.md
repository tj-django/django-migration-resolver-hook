[![PyPI version](https://badge.fury.io/py/django-migration-resolver-hook.svg)](https://badge.fury.io/py/django-migration-resolver-hook)

# [django-migration-resolver-hook](https://pypi.org/project/django-migration-resolver-hook/)

Django Migration resolver ensures that migration files always stays ordered regardless of remote changes.


Problem:

With generated migration files using Django's `manage.py makemigrations` command you could run
into issues where the generated migration files would potentially be out of sync with 
remote's master/default branch most CI servers are able to catch this error by running a test based on
your local branch merge back into the base branch there by spotting duplicate migration nodes.


Solution:
   
This package aims to solve this problem by using a Doubly Linked List while traversing the app's 
migration file(s) to store and detect duplicate node(s) and potential conflicts.

When duplicate nodes are detected [`stat.st_mtime`](https://docs.python.org/2/library/stat.html#stat.ST_MTIME) is used to sort files based on the last modified time.

:warning: This is not always accurate and might require a manual check to validate changes.

> NOTE: This doesn't require Django's installed apps concept when using 
*CLI commands* since this is totally file based and should be executed within
 the root/app folders.



## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
    
    i. [Use Case](#use-case)
        
    ii. [Using Auto migration resolver](#using-auto-migration-resolver)
        
    iii. [Using Static migration resolver](#using-static-migration-resolver)



## Installation

```bash
$ pip install django-migration-resolver-hook
```

##### Poetry

```bash
poetry add -D django-migration-resolver-hook
```


## Usage

#### Use Case

##### Remote
```text
|--- migrations
       |---- ...
       |---- 0007_auto_20200112_2328.py # Shared between remote and local repo
       |---- 0008_auto_20200113_4328.py # Only exists on remote
       |---- 0009_auto_20200114_4532.py
       |---- 0010_auto_20200115_1632.py

```

##### Local repo

```text
|--- migrations
       |---- ...
       |---- 0007_auto_20200112_2328.py  # Shared between remote and local repo
       |---- 0008_auto_20200114_5438.py  # Only exists locally which raises duplicate migration nodes errors.
```

> Since this is now out of sync with the remote branch to sync changes:
-----------------------------

### Using Auto migration resolver

---------------------------------
#### CLI command: `auto_migration_resolver`

Auto detect and fix migration files by providing the following:
- `--app-name`: The app_name of the Django application.
- `--strategy`: The strategy used to resolve migration errors (options: "reseed"/"inline"). (Defaults to: "reseed")
- `--exclude`: The list of migration files that should be ignored.
- `--commit`: Perform a `git commit` for the changes after moving file old -> new.
- `--verbose`: Verbose command execution.

##### Usage:

```bash
$ auto_migration_resolver --app-name my_app --commit --verbose
```

###### Output

```text
...
```

-------------------------------
### Using Static migration resolver

-------------------------------
#### CLI command: `migration_resolver`

Fix migrations by providing the following: 
- `--app-name`: The app_name of the Django application.
- `--last`: Last migration file of the remote that should be the seed of the conflicted migrations with or without the suffix.
- `--conflict`: The migration file which needs to be reseeded from the last migration file.
- `--commit`: Perform a `git commit` for the changes after moving file old -> new.
- `--verbose`: Verbose command execution.

##### Usage:

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
usage: migration_resolver [-h] [--auto-detect] [--verbose] --app-name APP_NAME --last LAST --conflict CONFLICT [--commit]

Resolve duplicate migration nodes.

optional arguments:
  -h, --help           show this help message and exit
  --auto-detect        Auto-detect and fix migration errors. (Not supported)
  --verbose            Verbose output
  --app-name APP_NAME  App Name
  --last LAST          The glob/full name of the final migration file.
  --conflict CONFLICT  The glob/full name of the final migration file with the conflict.
  --commit             Commit the changes made.
```


Using vsc (git/mercurial) when the remote has a migration files that conflict with previous
migrations you have locally.


TODO:
- [x] Auto detect and resolve errors with migration nodes.
- [ ] Speed up execution using async/await for handling reading nodes.
- [ ] Add support for database unapply migration for case of applied migrations.
- [ ] Add support to rollback any changes if there are failures in the chain of operation.
- [ ] VCS support right now only git is supported (extend to mercurial).
- [ ] Document Auto migration strategies.

