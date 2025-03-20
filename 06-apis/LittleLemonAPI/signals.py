from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def assign_group_to_new_user(sender, instance, created, **kwargs):
    if created:
        if not instance.groups.exists():
            group_name = "Customer"
            group, created = Group.objects.get_or_create(name=group_name)
            instance.groups.add(group)
