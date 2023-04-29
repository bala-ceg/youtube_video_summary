from django.db import models


class video_sum_predicted(models.Model):
    summary = models.TextField()
    video_id = models.CharField(max_length=50)
