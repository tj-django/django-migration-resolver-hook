import argparse
import inspect
import operator
import os
import pathlib
from typing import Optional, Generator
import re
from importlib import import_module

from bin.resolver import Resolver


class MigrationNode(object):
    def __init__(self):
        self._prev = None  # type: Optional[MigrationNode]
        self._current = None  # type: Optional[pathlib.Path]
        self._next = None  # type: Optional[MigrationNode]

    @property
    def next(self):
        # type: () -> MigrationNode
        return self._next

    @next.setter
    def next(self, next):
        if next and not isinstance(next, MigrationNode):
            raise ValueError('Expected {}: provided {}'.format(type(self).__name__, repr(next)))
        self._next = next

    @property
    def prev(self):
        # type: () -> MigrationNode
        return self._prev

    @prev.setter
    def prev(self, prev):
        if prev and not isinstance(prev, MigrationNode):
            raise ValueError('Expected {}: provided {}'.format(type(self).__name__, repr(prev)))
        self._prev = prev

    @property
    def current(self):
        return self._current

    @property
    def long_stem(self):
        if self.current:
            return self.current.stem

    @property
    def short_stem(self):
        if self.long_stem:
            return self.long_stem.split('_')[0]

    @current.setter
    def current(self, current):
        if not isinstance(current, pathlib.Path):
            raise ValueError('Expected {}: provided {}'.format(pathlib.Path.__name__, repr(current)))
        self._current = current

    @classmethod
    def as_migration_node(cls, current, prev=None, next=None):
        node = cls()
        node.prev = prev
        node.current = current
        node.next = next
        return node

    def __str__(self):
        title = ''
        if self.prev:
            title = (
                '{prev_pathname} → '.format(prev_pathname=self.prev.current.name)
            )
        if self.current:
            title += (
                '{current_pathname}'.format(current_pathname=self.current.name)
            )
        if self.next:
            title += (
                ' → {next_pathname}'.format(next_pathname=self.next.current.name)
            )
        return title

    def __repr__(self):
        return '<{}:{}>'.format(self.__class__, str(self))

    def walk(self):
        yield self

        next_ = self.next

        while next_ is not None:
            yield next_
            next_ = next_.next

    def conflicts(self):
        next_ = self
        seen = set()

        while next_:
            current_stem = next_.short_stem

            if current_stem not in seen:
                seen.add(current_stem)
            else:
                yield next_

            next_ = next_.next

    def node_exists(self, path):
        # type: (pathlib.Path) -> bool
        stem = path.stem.split('_')[0]
        found = False

        if self.current.stem.split('_')[0] == stem:
            return True

        next_ = self.next

        while next_:
            next_stem = next_.current.stem

            if next_stem.split('_')[0] == stem:
                found = True
                break
            else:
                next_ = next_.next

        return found

    @property
    def last(self):
        # type: () -> MigrationNode
        last = len(self) - 1
        return self[last]

    def __iter__(self):
        # type: () -> Generator[Optional[MigrationNode]]
        return self.walk()

    def __len__(self):
        return len(list(iter(self)))

    def __getitem__(self, index):
        # type: (int) -> MigrationNode
        items = list(iter(self))
        return items[index]


class AutoResolver(object):
    INITIAL_RE = re.compile('.*initial\s+=\s+True')

    def __init__(
        self,
        app_name,
        commit=False,
        verbose=False,
        exclude=None,
        strategy=None,
        mtime_gt=False,
    ):
        self.app_name = app_name
        self.commit = commit
        self.verbose = verbose
        self.strategy = strategy
        self.base_exclude = ['__init__']
        self.exclude = []
        self.excluded_paths = []

        self.app_module = import_module(app_name)
        self.migration_module = import_module('%s.%s' % (app_name, 'migrations'))

        self.mtime_gt = mtime_gt

        base_dir = os.path.dirname(os.path.dirname(inspect.getfile(self.app_module)))
        migration_dir = os.path.dirname(inspect.getfile(self.migration_module))

        self.base_path = pathlib.Path(os.path.join(base_dir))
        self.migration_path = pathlib.Path(os.path.join(migration_dir))

        if exclude:
            for path in exclude + self.base_exclude:
                excluded_path = list(
                    self.migration_path.glob('*{exclude}*'.format(exclude=path))
                )
                if len(excluded_path) > 1:
                    raise ValueError('Found more than one path for {}'.format(path))
                else:
                    excluded_path = excluded_path[0]
                    self.exclude.append(excluded_path.stem)
                    self.excluded_paths.append(excluded_path)

    def make_migration_node(self):
        migration_paths = sorted(
            self.migration_path.glob('*.py'),
            key=lambda p: (p.name.split('_')[0], -p.stat().st_mtime),
        )
        migration_node = MigrationNode()
        current_node = migration_node

        for index, path in enumerate(migration_paths):
            if path in self.excluded_paths:
                continue
            is_initial = self.INITIAL_RE.search(path.read_text())
            if is_initial:
                current_node.current = path
                current_node.prev = None
            else:
                node = MigrationNode.as_migration_node(
                    current=path,  # 002
                    prev=current_node,
                    next=None,
                )
                current_node.next = node
                # Change pointer to current node
                current_node = node

        return migration_node

    def fix(self):
        migration_node = self.make_migration_node()

        for node in migration_node.conflicts():
            comparator = operator.lt if not self.mtime_gt else operator.gt

            if self.strategy == 'reseed':
                # Sort by the last modified time
                # Fix the migrations
                prev = node.prev

                prev_stat = prev.current.stat()
                node_stat = node.current.stat()

                if comparator(prev_stat.st_mtime, node_stat.st_mtime):
                    node = prev

                resolver = Resolver(
                    app_name=self.app_name,
                    last=migration_node.last.long_stem,
                    conflict=node.long_stem,
                    commit=self.commit,
                    verbose=self.verbose,
                )
                # TODO: Update the migration_node to include changes after reseeding.
                # possibly update the node path/pointers to next and prev.
                migration_node = self.make_migration_node()
            else:
                # Sort by the last modified time
                # Fix the migrations
                prev = node.prev

                prev_stat = prev.current.stat()
                node_stat = node.current.stat()

                if comparator(prev_stat.st_mtime, node_stat.st_mtime):
                    last = prev
                else:
                    node, last = prev, node

                resolver = Resolver(
                    app_name=self.app_name,
                    last=last.long_stem,
                    conflict=node.long_stem,
                    commit=self.commit,
                    verbose=self.verbose,
                )
                migration_node = self.make_migration_node()
            resolver.fix()


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Auto Fix vcs errors with duplicate migration nodes.'
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
        '--strategy',
        type=str,
        choices=('reseed', 'inline'),
        default='reseed',
    )
    parser.add_argument(
        '--exclude',
        type=str,
        nargs='+',
        required=False,
        help='The glob/full name of the excluded migration file(s).'
    )
    parser.add_argument(
        '--mtime-gt',
        action='store_true',
        help='Use mtime greater than',
    )
    parser.add_argument(
        '--commit',
        action='store_true',
        help='Commit the changes made.'
    )

    return parser.parse_args()


def main(args=None):
    args = parse_args(args=args)
    resolver = AutoResolver(
        app_name=args.app_name,
        commit=args.commit,
        verbose=args.verbose,
        exclude=args.exclude,
        strategy=args.strategy,
        mtime_gt=args.mtime_gt,
    )
    resolver.fix()


if __name__ == '__main__':
    main()
