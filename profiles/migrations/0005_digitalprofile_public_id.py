import uuid

from django.db import migrations, models


def populate_public_ids(apps, schema_editor):
    DigitalProfile = apps.get_model('profiles', 'DigitalProfile')
    profiles = DigitalProfile.objects.using(schema_editor.connection.alias)
    pending_updates = []
    for profile in profiles.filter(public_id__isnull=True).iterator(chunk_size=1000):
        profile.public_id = uuid.uuid4()
        pending_updates.append(profile)
        if len(pending_updates) == 1000:
            profiles.bulk_update(pending_updates, ['public_id'], batch_size=1000)
            pending_updates.clear()
    if pending_updates:
        profiles.bulk_update(pending_updates, ['public_id'], batch_size=1000)


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_digitalprofile_google_maps_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='digitalprofile',
            name='public_id',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(populate_public_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='digitalprofile',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
