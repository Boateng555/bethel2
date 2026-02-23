# Fixed for SQLite: avoid RemoveField table remake by dropping tables directly

from django.db import migrations


def drop_jitsi_tables(apps, schema_editor):
    """Drop Jitsi tables in correct order (participant first due to FK to meeting)."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS core_jitsiparticipant;")
        cursor.execute("DROP TABLE IF EXISTS core_jitsimeeting_moderators;")
        cursor.execute("DROP TABLE IF EXISTS core_jitsimeeting;")
        cursor.execute("DROP TABLE IF EXISTS core_jitsisettings;")


def noop_reverse(apps, schema_editor):
    """Cannot recreate deleted Jitsi models from this migration."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_add_jitsi_models'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='jitsiparticipant',
                    name='meeting',
                ),
                migrations.AlterUniqueTogether(
                    name='jitsiparticipant',
                    unique_together=None,
                ),
                migrations.RemoveField(
                    model_name='jitsiparticipant',
                    name='user',
                ),
                migrations.RemoveField(
                    model_name='jitsisettings',
                    name='church',
                ),
                migrations.DeleteModel(
                    name='JitsiMeeting',
                ),
                migrations.DeleteModel(
                    name='JitsiParticipant',
                ),
                migrations.DeleteModel(
                    name='JitsiSettings',
                ),
            ],
            database_operations=[
                migrations.RunPython(drop_jitsi_tables, noop_reverse),
            ],
        ),
    ]
