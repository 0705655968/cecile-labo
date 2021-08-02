#!/usr/bin/env python
import os
import sys
import environ


def run():
    env = environ.Env()
    env.read_env('.env')
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", env('SETTINGS_MODULE'))
    try:
        from django.core.management import execute_from_command_line
#        from django.db.backends.mysql.schema import DatabaseSchemaEditor
#        DatabaseSchemaEditor.sql_create_table += " ROW_FORMAT=DYNAMIC"
    except ImportError as exc:
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        raise
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    run()
