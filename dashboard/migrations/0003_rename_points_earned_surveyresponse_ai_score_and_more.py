# Generated by Django 5.2.3 on 2025-07-11 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_surveyresponse_recommended_department_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='surveyresponse',
            old_name='points_earned',
            new_name='ai_score',
        ),
        migrations.RenameField(
            model_name='surveyresponse',
            old_name='recommended_department',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='surveyresponse',
            old_name='course',
            new_name='recommendation',
        ),
        migrations.AlterUniqueTogether(
            name='surveyresponse',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='computing_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='correctly_answered',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='cybersecurity_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='selected_options_from_one_to_five',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='selected_options_rest_questions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='skipped',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='surveyresponse',
            name='id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
        migrations.RemoveField(
            model_name='surveyresponse',
            name='index',
        ),
        migrations.RemoveField(
            model_name='surveyresponse',
            name='player',
        ),
        migrations.RemoveField(
            model_name='surveyresponse',
            name='question_id',
        ),
        migrations.RemoveField(
            model_name='surveyresponse',
            name='question_type',
        ),
        migrations.RemoveField(
            model_name='surveyresponse',
            name='selected_option_id',
        ),
        migrations.DeleteModel(
            name='Player',
        ),
    ]
