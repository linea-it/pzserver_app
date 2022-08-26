from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    class Meta:
        verbose_name_plural = "profile"

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    display_name = models.CharField(
        verbose_name="Display Name", max_length=124, default=None, null=True, blank=True
    )

    def __str__(self):
        return str(self.user.username)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):

    profile, create = Profile.objects.get_or_create(user=instance)
    if profile.display_name is None:
        if instance.email is not None:
            profile.display_name = instance.email.split("@")[0]
        else:
            profile.display_name = instance.username
        profile.save()

    # instance.profile.save()
