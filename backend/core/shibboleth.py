import logging

from django.contrib.auth.models import Group
from shibboleth.middleware import ShibbolethRemoteUserMiddleware


class ShibbolethMiddleware(ShibbolethRemoteUserMiddleware):
    def make_profile(self, user, shib_meta):
        """
        This is here as a stub to allow subclassing of ShibbolethRemoteUserMiddleware
        to include a make_profile method that will create a Django user profile
        from the Shib provided attributes.  By default it does nothing.
        """
        log = logging.getLogger("shibboleth")
        log.debug("Shib Meta:")
        log.debug(shib_meta)

        log.debug("User:")
        log.debug(user)

        # Guardar o email do usuario
        if shib_meta.get("email", None):
            user.email = shib_meta.get("email")
            log.debug("Updated user email")

        if shib_meta.get("first_name", None):
            fullname = shib_meta.get("first_name")
            user.first_name = fullname.split()[0]
            user.last_name = fullname.split()[-1]

        if user.profile.display_name != shib_meta.get("display_name", None):
            user.profile.display_name = shib_meta.get("display_name", user.username)
            log.debug("Added user profile display name")
            user.profile.save()

        # Adiciona um display name para o usuario
        if user.profile.display_name is None:
            user.profile.display_name = user.username
            user.profile.save()

        user.save()

        # Adicionar o usuario ao grupo Shibboleth
        try:
            if not user.groups.filter(name="Shibboleth").exists():
                group, created = Group.objects.get_or_create(name="Shibboleth")
                group.user_set.add(user)
                log.debug("Added user to Shibboleth group")
        except Exception as e:
            log.error("Failed on add user to group shibboleth. Error: %s" % e)

        return

    def setup_session(self, request):
        """
        If you want to add custom code to setup user sessions, you
        can extend this.
        """
        log = logging.getLogger("shibboleth")
        log.debug("---------- Setup Session ----------")

        return
