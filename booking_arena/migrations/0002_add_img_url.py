from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('booking_arena', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='arena',
            name='img_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
