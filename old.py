import os
import pathlib

from django.conf import settings
from django.db import migrations
from django.db.migrations.executor import MigrationExecutor


BASE_DIR = os.path.join(settings.BASE_DIR, 'app_name', 'migrations')

def forwards_func(apps, schema_editor):
    connection = schema_editor.connection
    path = pathlib.Path(os.path.join(BASE_DIR, '222.py'))
    if path.exists():
        # Reverse to the original migration
        executor = MigrationExecutor(connection)
        executor.migrate([('app_name', '222')])

        # Rename the file
        post_migration_path = pathlib.Path(os.path.join(BASE_DIR, '222.py'))
        output = post_migration_path.read_text().replace('222', '222')
        post_migration_path.write_text(output)

        path.rename(os.path.join(BASE_DIR, '222.py'))

        # Reapply the migration
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate([('content_library', '222')])


class Migration(migrations.Migration):

    dependencies = [
        ('app_name', '222'),
    ]

    operations = [
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]
