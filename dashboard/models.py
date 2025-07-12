from django.db import models

class AnswerRecord(models.Model):
    player_id = models.CharField(max_length=100, primary_key=True)  # Unity Player ID
    index = models.IntegerField()  # Sequential index
    question_id = models.IntegerField()
    question_type = models.CharField(max_length=20, choices=[('knowledge', 'Knowledge'), ('preference', 'Preference')])
    selected_option_id = models.CharField(max_length=10)  # e.g., "A", "B", "C"
    course = models.CharField(max_length=50, choices=[('AI', 'AI'), ('Computing', 'Computing'), ('Cybersecurity', 'Cybersecurity')])
    points_earned = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player_id', 'index')  # Unique per player and sequence

    def __str__(self):
        return f"{self.player_id} - Q{self.question_id} (Index {self.index})"

class SurveyResponse(models.Model):
    player_id = models.CharField(max_length=100, primary_key=True)  # Unity Player ID
    ai_points = models.IntegerField(default=0)
    computing_points = models.IntegerField(default=0)
    cybersecurity_points = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    recommendation = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response {self.player_id}"

    def save(self, *args, **kwargs):
        self.total_score = self.ai_points + self.computing_points + self.cybersecurity_points
        self.recommendation = max(
            [('AI', self.ai_points), ('Computing', self.computing_points), ('Cybersecurity', self.cybersecurity_points)],
            key=lambda x: x[1]
        )[0]
        super().save(*args, **kwargs)

from django.db import models

class AnswerRecord(models.Model):
    player_id = models.CharField(max_length=100, primary_key=True)  # Unity Player ID
    index = models.IntegerField()  # Sequential index
    question_id = models.IntegerField()
    question_type = models.CharField(max_length=20, choices=[('knowledge', 'Knowledge'), ('preference', 'Preference')])
    selected_option_id = models.CharField(max_length=10)  # e.g., "A", "B", "C"
    course = models.CharField(max_length=50, choices=[('AI', 'AI'), ('Computing', 'Computing'), ('Cybersecurity', 'Cybersecurity')])
    points_earned = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player_id', 'index')  # Unique per player and sequence

    def __str__(self):
        return f"{self.player_id} - Q{self.question_id} (Index {self.index})"

class SurveyResponse(models.Model):
    player_id = models.CharField(max_length=100, primary_key=True)  # Unity Player ID
    ai_points = models.IntegerField(default=0)
    computing_points = models.IntegerField(default=0)
    cybersecurity_points = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    recommendation = models.CharField(max_length=50, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response {self.player_id}"

    def save(self, *args, **kwargs):
        self.total_score = self.ai_points + self.computing_points + self.cybersecurity_points
        self.recommendation = max(
            [('AI', self.ai_points), ('Computing', self.computing_points), ('Cybersecurity', self.cybersecurity_points)],
            key=lambda x: x[1]
        )[0]
        super().save(*args, **kwargs)
