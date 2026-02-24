from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detectionhistory',
            name='packet_size',
        ),
        migrations.RemoveField(
            model_name='detectionhistory',
            name='inter_arrival',
        ),
        migrations.RemoveField(
            model_name='detectionhistory',
            name='packet_rate',
        ),
        migrations.RemoveField(
            model_name='detectionhistory',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='detectionhistory',
            name='failed_logins',
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='altitude',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='speed',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='direction',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='signal_strength',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='distance_from_base',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='flight_time',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='battery_level',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='temperature',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='vibration',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='detectionhistory',
            name='gps_accuracy',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
    ]
