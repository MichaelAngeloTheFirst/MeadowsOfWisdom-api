# Generated by Django 4.2.4 on 2023-09-23 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("mow_api", "0003_alter_funfact_updated_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="funfactcomment",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="replies",
                to="mow_api.funfactcomment",
            ),
        ),
    ]