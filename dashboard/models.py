from django.db import models

class SurveyResponse(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)
    score = models.IntegerField(default=0)
    skipped = models.BooleanField(default=False)
    selected_options_from_one_to_five = models.TextField(blank=True, null=True)
    selected_options_rest_questions = models.TextField(blank=True, null=True)
    correctly_answered = models.TextField(blank=True, null=True)
    recommendation = models.CharField(max_length=50, blank=True, null=True)
    computing_score = models.IntegerField(default=0)
    cybersecurity_score = models.IntegerField(default=0)
    ai_score = models.IntegerField(default=0)

    def __str__(self):
        return self.id
