from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_digitalprofile_social_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='digitalprofile',
            name='google_maps_url',
            field=models.URLField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name='Google Maps location URL',
            ),
        ),
    ]
