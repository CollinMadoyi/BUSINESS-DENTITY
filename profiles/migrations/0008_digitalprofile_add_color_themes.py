from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0007_digitalprofile_color_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='digitalprofile',
            name='color_theme',
            field=models.CharField(
                choices=[
                    ('OCEAN', 'Ocean'),
                    ('SUNSET', 'Sunset'),
                    ('FOREST', 'Forest'),
                    ('ROYAL', 'Royal'),
                    ('LAVENDER', 'Lavender'),
                    ('ROSE', 'Rose'),
                    ('SLATE', 'Slate'),
                    ('SAND', 'Sand'),
                ],
                default='FOREST',
                max_length=10,
            ),
        ),
    ]
