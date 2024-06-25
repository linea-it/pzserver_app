import logging

from django.contrib.auth.models import Group
from djangosaml2.backends import Saml2Backend


class ModifiedSaml2Backend(Saml2Backend):

    def _update_user(self, user, attributes: dict, attribute_mapping: dict, force_save: bool = False):

        log = logging.getLogger("saml")

        log.debug("USER: ", user)
        log.debug("ATTRIBUTES: ", attributes)

        display_name = attributes.get('cn', [""])[0]

        if display_name:
            names = display_name.split()
            user.first_name = names[0]
            user.last_name = names[-1]
            user.profile.display_name = display_name
            user.save()

        return super()._update_user(user, attributes, attribute_mapping, force_save)

    def save_user(self, user, *args, **kwargs):
        log = logging.getLogger("saml")
        user.save()

        try:
            if not user.groups.filter(name="Saml2").exists():
                group, _ = Group.objects.get_or_create(name="Saml2")
                group.user_set.add(user)
                group.save()
                log.debug("Added user to Saml2 group")
        except Exception as _er:
            log.error("Failed on add user to group Saml2. Error: %s" % _er)

        return super().save_user(user, *args, **kwargs)
