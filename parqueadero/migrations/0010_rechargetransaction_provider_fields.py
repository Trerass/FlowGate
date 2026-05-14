from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parqueadero', '0009_wallet_rechargetransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='rechargetransaction',
            name='provider',
            field=models.CharField(choices=[('demo', 'Demo'), ('wompi', 'Wompi')], default='demo', max_length=20),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='payment_method',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='provider_transaction_id',
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AddField(
            model_name='rechargetransaction',
            name='credited',
            field=models.BooleanField(default=False),
        ),
    ]
