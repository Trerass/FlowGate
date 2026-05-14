from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parqueadero', '0008_metodopago'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance_cop', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wallet', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RechargeTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=64)),
                ('amount_cop', models.PositiveIntegerField()),
                ('amount_in_cents', models.PositiveIntegerField()),
                ('currency', models.CharField(default='COP', max_length=3)),
                ('reference', models.CharField(max_length=80, unique=True)),
                ('wompi_transaction_id', models.CharField(blank=True, db_index=True, max_length=100)),
                ('status', models.CharField(choices=[('PENDING', 'Pendiente'), ('APPROVED', 'Aprobada'), ('DECLINED', 'Rechazada'), ('ERROR', 'Error'), ('VOIDED', 'Anulada')], db_index=True, default='PENDING', max_length=20)),
                ('is_credited', models.BooleanField(default=False)),
                ('raw_response', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recharge_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
