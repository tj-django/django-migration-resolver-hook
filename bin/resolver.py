import argparse
import inspect
import os
import pathlib
import re
import shlex
import subprocess
import sys
from importlib import import_module
from itertools import count


def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)

    try:
        outs, errs = process.communicate(timeout=30)
        if outs:
            print(outs.decode('utf8').strip(), file=sys.stdout)
        if errs:
            print(errs, file=sys.stdout)
    except subprocess.TimeoutExpired:
        process.kill()
        outs, errs = process.communicate()
        if outs:
            print(outs.decode('utf8').strip(), file=sys.stdout)
        if errs:
            print(errs, file=sys.stdout)
    rc = process.poll()
    return rc


class Resolver(object):
    def __init__(self, app_name, last, conflict, commit=False, verbose=False):
        self.app_name = app_name
        self.app_module = import_module(app_name)
        self.migration_module = import_module('%s.%s' % (app_name, 'migrations'))
        self.last = last  # 0539_auto_20200117_2109.py
        self.conflict = conflict  # 0537_auto_20200115_1632.py
        self.commit = commit
        self.verbose = verbose

        base_dir = os.path.dirname(os.path.dirname(inspect.getfile(self.app_module)))
        migration_dir = os.path.dirname(inspect.getfile(self.migration_module))

        self.base_path = pathlib.Path(os.path.join(base_dir))
        self.migration_path = pathlib.Path(os.path.join(migration_dir))
        self.replace_regex = re.compile(
            "\('{app_name}',\s'(?P<conflict_migration>.*)'\),"
            .format(app_name=self.app_name),
            re.I | re.M,
        )

        seed = self.last.split('_')[0]

        if str(seed).isdigit():
            next_ = next(count(int(seed) + 1))
            if not str(next_).startswith('0'):
                next_ = '0{next_}'.format(next_=next_)

        else:
            raise NotImplementedError

        self.last_path = list(
            self.migration_path.glob('*{last}*'.format(last=self.last))
        )[0]
        self.conflict_path = list(
            self.migration_path.glob(
                '*{conflict}*'.format(conflict=self.conflict))
        )[0]

        self.replacement = (
            "('{app_name}', '{prev_migration}'),"
            .format(
                app_name=self.app_name,
                prev_migration=self.last_path.name.strip(self.last_path.suffix),
            )
        )

        # Calculate the new name
        conflict_parts = self.conflict_path.name.split('_')

        conflict_parts[0] = next_

        new_conflict_name = '_'.join(conflict_parts)

        self.conflict_new_path = self.conflict_path.with_name(new_conflict_name)

    def fix(self):
        if self.conflict_path.is_file():
            conflict_file = os.path.basename(str(self.conflict_path))
            new_resolved_file = os.path.basename(str(self.conflict_new_path))
            pwd = os.getcwd()
            os.chdir(self.base_path)
            print('Fixing migrations...')

            if self.verbose:
                print(
                    'Updating the conflicting migration file {}'.format(conflict_file),
                )
            # Rename the file
            output = re.sub(
                self.replace_regex,
                self.replacement,
                self.conflict_path.read_text(),
            )
            # Write to the conflict file.
            self.conflict_path.write_text(output)

            if self.verbose:
                print('Successfully updated: {}.'.format(conflict_file))
                print(
                    'Renaming the migration file from {} to {}'
                    .format(conflict_file, new_resolved_file)
                )

            # Calculate the new name
            self.conflict_path.rename(self.conflict_new_path)

            if self.verbose:
                print('Successfully renamed the migration file.')

            if self.commit:
                msg = (
                    'Resolved migration conflicts for {} → {}'.format(
                        os.path.basename(str(self.conflict_path)),
                        os.path.basename(str(self.conflict_new_path)),
                    )
                )
                migration_abs_path = str(self.migration_path).replace(
                    '{}/'.format(str(self.base_path)), '')
                cf_abs = os.path.join(migration_abs_path, new_resolved_file)
                ncf_abs = os.path.join(migration_abs_path, conflict_file)

                run_command('git add {}'.format(cf_abs))
                run_command('git add {}'.format(ncf_abs))
                run_command('git commit -m "{}"'.format(msg))
            os.chdir(pwd)


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Fix vcs errors with duplicate migration nodes.'
    )
    parser.add_argument(
        '--verbose',
        help='Verbose output',
        action='store_true'
    )
    parser.add_argument(
        '--app-name',
        type=str,
        help='App Name',
        required=True,
    )
    parser.add_argument(
        '--last',
        type=str,
        required=True,
        help='The glob/full name of the final migration file.'
    )

    parser.add_argument(
        '--conflict',
        type=str,
        required=True,
        help='The glob/full name of the final migration file with the conflict.'
    )

    parser.add_argument(
        '--commit',
        action='store_true',
        help='Commit the changes made.'
    )

    return parser.parse_args()


def main(args=None):
    args = parse_args(args=args)
    resolver = Resolver(
        app_name=args.app_name,
        last=args.last,
        conflict=args.conflict,
        commit=args.commit,
        verbose=args.verbose,
    )
    resolver.fix()


if __name__ == '__main__':
    main()
