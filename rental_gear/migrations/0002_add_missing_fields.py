from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('rental_gear', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gear',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='gear',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='gear',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
    ]
