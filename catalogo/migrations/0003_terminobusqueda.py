from django.db import migrations, models
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_rename_precio_base_producto_precio_and_more'),
    ]

    operations = [
        TrigramExtension(),
        migrations.CreateModel(
            name='TerminoBusqueda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('termino', models.CharField(max_length=200, unique=True)),
                ('contador', models.PositiveIntegerField(default=1)),
                ('ultima_busqueda', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Termino de busqueda',
                'verbose_name_plural': 'Terminos de busqueda',
                'ordering': ['-contador'],
            },
        ),
    ]
