from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0004_rename_ai_score_surveyresponse_ai_points_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='surveyresponse',
            old_name='id',
            new_name='player_id',
        ),
        migrations.AddField(
            model_name='answerrecord',
            name='index',
            field=models.IntegerField(default=0),
        ),
        # Remove any existing unique_together constraints that might conflict
        migrations.AlterUniqueTogether(
            name='answerrecord',
            unique_together=set(),  # Temporarily remove to avoid conflicts
        ),
        migrations.AlterField(
            model_name='answerrecord',
            name='player_id',
            field=models.CharField(max_length=100, default='unknown', serialize=False),
        ),
        migrations.RemoveField(
            model_name='answerrecord',
            name='id',
        ),
        migrations.AlterField(
            model_name='answerrecord',
            name='player_id',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterUniqueTogether(
            name='answerrecord',
            unique_together={('player_id', 'index')},
        ),
    ]