from django.db import models


class Release(models.Model):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    indexing_column = models.CharField(max_length=255)
    has_mag_hats = models.BooleanField(default=False)
    has_flux_hats = models.BooleanField(default=True)
    dereddening = models.JSONField(null=True, blank=True)
    fluxes = models.JSONField(null=True, blank=True)
    
    # Access control based on Django groups (SAML + local)
    access_groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='accessible_releases',
        help_text="Groups that have access to this release. If empty, all authenticated users have access."
    )
    is_public = models.BooleanField(
        default=False,
        help_text="If true, the release is accessible to all authenticated users, regardless of groups"
    )

    def __str__(self):
        return f"{self.display_name}"
    
    def user_has_access(self, user):
        """
        Checks if the user has access to this release based on SAML groups.
        
        Args:
            user: User model instance
            
        Returns:
            bool: True if the user has access, False otherwise
        """
        # If the release is public, everyone has access
        if self.is_public:
            return True
            
        # If no groups are defined, all authenticated users have access
        if not self.access_groups.exists():
            return True
            
        # Check if the user belongs to any of the groups with access
        user_group_ids = set(user.groups.values_list('id', flat=True))
        release_group_ids = set(self.access_groups.values_list('id', flat=True))
        
        return bool(user_group_ids & release_group_ids)
