from django.db import models


class Release(models.Model):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.display_name}"
