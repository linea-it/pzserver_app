from django.db import models


class Release(models.Model):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    indexing_column = models.CharField(max_length=255)


    def __str__(self):
        return f"{self.display_name}"
