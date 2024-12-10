from django.db.models.signals import post_save
from django.dispatch import receiver
from pro_app.models import Clients, CustomUser, Task

@receiver(post_save, sender=Clients)
def assign_task_to_marketing_director(sender, instance, created, **kwargs):
    if created:
        # Get the marketing director
        marketing_director = CustomUser.objects.filter(role='marketing_director').first()
        
        if marketing_director:
            # Assign a task to the marketing director
            Task.objects.create(
                task_type='assign_client_to_team',
                assigned_to=marketing_director,
                client=instance
            )
