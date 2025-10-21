# Generated manually to eliminate user-group duplication
from django.db import migrations, models
import logging

log = logging.getLogger("migration")


def consolidate_group_memberships(apps, schema_editor):
    """
    Consolidates existing auth_user_groups data into GroupMembership table
    and marks Linea groups appropriately.
    """
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')
    GroupMembership = apps.get_model('core', 'GroupMembership')
    GroupMetadata = apps.get_model('core', 'GroupMetadata')
    
    stats = {
        'consolidated': 0,
        'already_exists': 0,
        'errors': 0
    }
    
    log.info("Starting consolidation of user-group memberships...")
    
    try:
        # Get all users with groups
        for user in User.objects.prefetch_related('groups').all():
            for group in user.groups.all():
                try:
                    # Check if GroupMembership already exists
                    existing = GroupMembership.objects.filter(
                        user=user, group=group
                    ).first()
                    
                    if existing:
                        # Update is_linea_managed flag if metadata exists
                        try:
                            metadata = GroupMetadata.objects.get(group=group)
                            if metadata.source == 'linea' and not existing.is_linea_managed:
                                existing.is_linea_managed = True
                                existing.save()
                                log.debug(f"Updated {user.username}-{group.name} to Linea managed")
                        except GroupMetadata.DoesNotExist:
                            pass
                        
                        stats['already_exists'] += 1
                        continue
                    
                    # Check if it's a Linea group based on metadata
                    is_linea = False
                    try:
                        metadata = GroupMetadata.objects.get(group=group)
                        is_linea = metadata.source == 'linea'  # Updated from 'saml' to 'linea'
                    except GroupMetadata.DoesNotExist:
                        pass
                    
                    # Create GroupMembership entry
                    GroupMembership.objects.create(
                        user=user,
                        group=group,
                        is_linea_managed=is_linea
                    )
                    
                    stats['consolidated'] += 1
                    
                    if stats['consolidated'] % 100 == 0:
                        log.info(f"Consolidated {stats['consolidated']} memberships so far...")
                        
                except Exception as e:
                    log.error(f"Error consolidating membership {user.username}-{group.name}: {e}")
                    stats['errors'] += 1
                    
    except Exception as e:
        log.error(f"Error during consolidation: {e}")
        raise
    
    log.info(f"Consolidation complete: {stats['consolidated']} consolidated, "
            f"{stats['already_exists']} already existed, {stats['errors']} errors")


def reverse_consolidation(apps, schema_editor):
    """
    Reverse operation: remove is_linea_managed field data
    (the field itself will be removed by the schema migration)
    """
    log.info("Reversing group membership consolidation...")
    # The field removal is handled by the schema migration


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_alter_groupmembership_last_seen_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        # Add the is_linea_managed field
        migrations.AddField(
            model_name='groupmembership',
            name='is_linea_managed',
            field=models.BooleanField(
                default=False, 
                help_text='True if this membership is managed by Linea IdP and should not be manually modified'
            ),
        ),
        
        # Run the data consolidation
        migrations.RunPython(
            consolidate_group_memberships,
            reverse_consolidation,
        ),
    ]