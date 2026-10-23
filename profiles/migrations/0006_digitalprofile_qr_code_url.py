from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_digitalprofile_public_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='digitalprofile',
            name='qr_code_url',
            field=models.URLField(blank=True, editable=False, max_length=500),
        ),
    ]
