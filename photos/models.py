from django.db import models

class Photo(models.Model):
    title = models.TextField()
    image = models.FileField(upload_to="images/")
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
