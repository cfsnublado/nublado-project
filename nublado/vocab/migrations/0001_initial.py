# Generated by Django 2.1.4 on 2019-01-05 10:07

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VocabContext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='label_date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='label_date_updated')),
                ('content', models.TextField(verbose_name='label_content')),
            ],
            options={
                'verbose_name': 'label_vocab_context',
                'verbose_name_plural': 'label_vocab_context_plural',
            },
        ),
        migrations.CreateModel(
            name='VocabContextEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='label_date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='label_date_updated')),
                ('vocab_context', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocab.VocabContext')),
            ],
            options={
                'verbose_name': 'label_vocab_entry_context',
                'verbose_name_plural': 'label_vocab_entry_context_plural',
            },
        ),
        migrations.CreateModel(
            name='VocabDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='label_date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='label_date_updated')),
                ('definition', models.TextField(verbose_name='label_definition')),
                ('definition_type', models.IntegerField(choices=[(1, 'label_noun'), (2, 'label_adjective'), (3, 'label_verb'), (4, 'label_adverb'), (5, 'label_expression')], default=1, verbose_name='label_vocab_definition_type')),
            ],
            options={
                'verbose_name': 'label_vocab_definition',
                'verbose_name_plural': 'label_vocab_definition_plural',
            },
        ),
        migrations.CreateModel(
            name='VocabEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], default='en', max_length=2, verbose_name='label_language')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='label_date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='label_date_updated')),
                ('entry', models.CharField(max_length=255, verbose_name='label_entry')),
                ('pronunciation_spelling', models.CharField(blank=True, max_length=255, verbose_name='label_vocab_pronunciation_spelling')),
                ('pronunciation_ipa', models.CharField(blank=True, max_length=255, verbose_name='label_vocab_pronunciation_ipa')),
                ('description', models.TextField(blank=True, verbose_name='label_description')),
                ('slug', models.SlugField(max_length=255, verbose_name='label_slug')),
            ],
            options={
                'verbose_name': 'label_vocab_entry',
                'verbose_name_plural': 'label_vocab_entry_plural',
            },
        ),
        migrations.CreateModel(
            name='VocabEntryJsonData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json_data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('json_data_source', models.IntegerField(choices=[(1, 'label_json_data_oxford'), (2, 'label_json_data_miriam_webster'), (3, 'label_json_data_colins'), (4, 'label_json_data_other')], default=4, verbose_name='label_vocab_source_type')),
                ('vocab_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocab_vocabentryjsondata', to='vocab.VocabEntry')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VocabEntryTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='label_content')),
                ('vocab_context_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocab_entry_tags', to='vocab.VocabContextEntry')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VocabProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='label_date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='label_date_updated')),
                ('name', models.CharField(max_length=255, verbose_name='label_name')),
                ('description', models.TextField(blank=True, verbose_name='label_description')),
                ('slug', models.SlugField(max_length=255, verbose_name='label_slug')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocab_vocabproject', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'label_vocab_project',
                'verbose_name_plural': 'label_vocab_project_plural',
            },
        ),
        migrations.CreateModel(
            name='VocabSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='label_date_created')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='label_date_updated')),
                ('name', models.CharField(max_length=255, verbose_name='label_name')),
                ('description', models.TextField(blank=True, verbose_name='label_description')),
                ('source_type', models.IntegerField(choices=[(1, 'label_source_book'), (2, 'label_source_website'), (3, 'label_source_blog'), (4, 'label_source_created')], default=4, verbose_name='label_vocab_source_type')),
                ('slug', models.SlugField(max_length=255, verbose_name='label_slug')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocab_vocabsource', to=settings.AUTH_USER_MODEL)),
                ('vocab_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocab_sources', to='vocab.VocabProject')),
            ],
            options={
                'verbose_name': 'label_vocab_source',
                'verbose_name_plural': 'label_vocab_source_plural',
            },
        ),
        migrations.AlterUniqueTogether(
            name='vocabentry',
            unique_together={('entry', 'language')},
        ),
        migrations.AddField(
            model_name='vocabdefinition',
            name='vocab_entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocab_definitions', to='vocab.VocabEntry'),
        ),
        migrations.AddField(
            model_name='vocabcontextentry',
            name='vocab_entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vocab.VocabEntry'),
        ),
        migrations.AddField(
            model_name='vocabcontext',
            name='vocab_entries',
            field=models.ManyToManyField(related_name='vocab_context_entry', through='vocab.VocabContextEntry', to='vocab.VocabEntry'),
        ),
        migrations.AddField(
            model_name='vocabcontext',
            name='vocab_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vocab_contexts', to='vocab.VocabSource'),
        ),
        migrations.AlterUniqueTogether(
            name='vocabsource',
            unique_together={('vocab_project', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='vocabproject',
            unique_together={('owner', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='vocabcontextentry',
            unique_together={('vocab_entry', 'vocab_context')},
        ),
    ]
