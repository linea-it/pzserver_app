from django.contrib.auth.models import Group, User
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

    def is_admin(self):
        # Superusuários são sempre admins
        if self.user.is_superuser:
            return True
        
        # Verificar se pertence ao grupo Admin
        try:
            group = self.user.groups.get(name="Admin")
            if group:
                return True
        except Group.DoesNotExist:
            pass
        
        return False

    def __str__(self):
        return str(self.display_name)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Cria um profile para o usuario e adiciona um display_name.
    Só é executado quando um usuario é criado.
    display_name = username para usuarios sem email.
    display_name = email.split('@')[0] para usuarios que tem email.

    Args:
        instance (User): instancia do model User.
        created (bool): True se o evento for disparado pela criação de um novo usuario.
    """
    if created:
        display_name = instance.username

        if instance.email:
            display_name = instance.email.split("@")[0]

        Profile.objects.get_or_create(
            user=instance, defaults={"display_name": display_name}
        )
