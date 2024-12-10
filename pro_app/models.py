from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import uuid

class CustomUserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

# USERS 
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(
    max_length=20,
    choices=[
        ('user', 'User'),  # Add this if you want 'user' as a role
        ('marketing_director', 'Marketing Director'),
        ('marketing_manager', 'Marketing Manager'),
        ('marketing_assistant', 'Marketing Assistant'),
        ('graphics_designer', 'Graphics Designer'),
        ('content_writer', 'Content Writer'),
        ('account_manager', 'Account Manager'),
        ('accountant', 'Accountant'),
    ],
    default='user'
)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    agency_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    profile = models.FileField(upload_to='profiles/', null=True, blank=True)
    
    # Adding the relationship to Plans
    plans = models.ManyToManyField('Plans', related_name="assigned_account_managers", blank=True)

    USERNAME_FIELD = 'username'  # This allows logging in using the username
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.username:  # If username is not set
            base_username = self.email.split('@')[0]  # Generate base username from email
            new_username = base_username
            counter = 1
            # Ensure the username is unique
            while CustomUser.objects.filter(username=new_username).exists():
                new_username = f"{base_username}{counter}"
                counter += 1
            self.username = new_username
        super().save(*args, **kwargs)  # Call the real save() method

    def __str__(self):
        return self.username

# CLIENTS 
# class Clients(models.Model):
#     team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
#     account_manager = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='clients')
#     created_at = models.DateTimeField(default=timezone.now)  # Adding the default value
#     BUSINESS_OFFERINGS_CHOICES = [
#         ('services', 'Services'),
#         ('products', 'Products'),
#         ('services_products', 'Services Products'),
#         ('other', 'Other'),
#     ]
                         
#     business_name = models.CharField(max_length=255)
#     contact_person = models.CharField(max_length=255)
#     business_details = models.TextField(blank=True)
#     brand_key_points = models.TextField(blank=True)
#     business_address = models.CharField(max_length=255)
#     brand_guidelines_link = models.URLField(blank=True)
#     business_whatsapp_number = models.CharField(max_length=20, blank=True)
#     goals_objectives = models.TextField(blank=True)
#     business_email_address = models.EmailField()
#     target_region = models.CharField(max_length=255)
#     brand_guidelines_notes = models.TextField(blank=True)
    
#     # Selection field with choices for business offerings
#     business_offerings = models.CharField(
#         max_length=20, 
#         choices=BUSINESS_OFFERINGS_CHOICES, 
#         default='services'
#     )
    
#     # A field for additional notes, UGC drive, website, and social handles
#     ugc_drive_link = models.URLField(blank=True)
#     business_website = models.URLField(blank=True)
    
#     # Social handles with an array for 'other' social handles
#     social_handles_facebook = models.URLField(blank=True)
#     social_handles_instagram = models.URLField(blank=True)
#     social_handles_other = models.JSONField(blank=True, default=list)  # This will store an array of other social handles
    
#     additional_notes = models.TextField(blank=True)
 
#    # New fields for proposal upload and approval status
#     proposal_pdf = models.FileField(upload_to='proposals/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
#     PROPOSAL_APPROVAL_CHOICES = [
#         ('approved', 'Approved'),
#         ('declined', 'Declined'),
#         ('changes_required', 'Changes Required'),
#     ]
#     proposal_approval_status = models.CharField(max_length=20, choices=PROPOSAL_APPROVAL_CHOICES, null=True, blank=True)



#     def __str__(self):
#         return self.business_name

# AFTER MERGE 
class Clients(models.Model):
    # Foreign Keys
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='clients')
    account_manager = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='clients')

    # Business Info
    business_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    business_details = models.TextField(blank=True)
    brand_key_points = models.TextField(blank=True)
    business_address = models.CharField(max_length=255)
    brand_guidelines_link = models.URLField(blank=True)
    business_whatsapp_number = models.CharField(max_length=20, blank=True)
    goals_objectives = models.TextField(blank=True)
    business_email_address = models.EmailField()
    target_region = models.CharField(max_length=255)
    brand_guidelines_notes = models.TextField(blank=True)
    
    BUSINESS_OFFERINGS_CHOICES = [
        ('services', 'Services'),
        ('products', 'Products'),
        ('services_products', 'Services Products'),
        ('other', 'Other'),
    ]
    business_offerings = models.CharField(
        max_length=20, 
        choices=BUSINESS_OFFERINGS_CHOICES, 
        default='services'
    )
    
    # Social Media and Web Info
    ugc_drive_link = models.URLField(blank=True)
    business_website = models.URLField(blank=True)
    
    social_handles_facebook = models.URLField(blank=True)
    social_handles_instagram = models.URLField(blank=True)
    social_handles_other = models.JSONField(blank=True, default=list)  # Stores other social handles
    
    additional_notes = models.TextField(blank=True)

    # Proposal Information
    proposal_pdf = models.FileField(upload_to='proposals/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    
    PROPOSAL_APPROVAL_CHOICES = [
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('changes_required', 'Changes Required'),
    ]
    proposal_approval_status = models.CharField(max_length=20, choices=PROPOSAL_APPROVAL_CHOICES, null=True, blank=True)

    # Web Development Data
    WEBSITE_TYPE_CHOICES = [
        ('ecommerce', 'Ecommerce'),
        ('services', 'Offer Services'),
    ]

    MEMBERSHIP_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    YES_NO_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    # Client WebDevData Fields
    website_type = models.CharField(max_length=20, choices=WEBSITE_TYPE_CHOICES, default='none')
    num_of_products = models.IntegerField(null=True, blank=True)  # Only for ecommerce
    membership = models.CharField(max_length=3, choices=MEMBERSHIP_CHOICES, default='none')
    website_structure = models.TextField(blank=True, null=True)
    design_preference = models.TextField(blank=True, null=True)
    domain = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='none')
    domain_info = models.CharField(max_length=255, blank=True, null=True)  # Only if domain is yes
    hosting = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='none')
    hosting_info = models.CharField(max_length=255, blank=True, null=True)  # Only if hosting is yes
    graphic_assets = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='none')
    is_regular_update = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='none')
    is_self_update = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='none')
    additional_webdev_notes = models.TextField(blank=True, null=True)

    # Timestamp
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.business_name

    
class Plans(models.Model):
    plan_name = models.CharField(max_length=255)

    # Plan Pricing fields (merged from PlanPricing)
    pricing_attributes = models.JSONField(default=dict, blank=True, help_text="Key-value pairs for attributes like reel:100, post:200, etc.")
    pricing_platforms = models.JSONField(default=dict, blank=True, help_text="Key-value pairs for platforms like facebook:200, instagram:150, etc.")

    # Standard Plan fields
    standard_attributes = models.JSONField(default=dict, blank=True, help_text="Key-value pairs for attributes like reel:100, post:200, etc.")
    standard_plan_inclusion = models.TextField(blank=True, null=True, help_text="Details of what's included in the standard plan")
    standard_netprice = models.IntegerField(help_text="Net price for the standard plan")

    # Advanced Plan fields
    advanced_attributes = models.JSONField(default=dict, blank=True, help_text="Key-value pairs for attributes like reel:100, post:200, etc.")
    advanced_plan_inclusion = models.TextField(blank=True, null=True, help_text="Details of what's included in the advanced plan")
    advanced_netprice = models.IntegerField(help_text="Net price for the advanced plan")

    # Additional fields
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Relationship with account managers (many-to-many)
    account_managers = models.ManyToManyField('CustomUser', related_name="assigned_plans", blank=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.plan_name

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"
        
                                 
#CLIENT PLAN
class ClientsPlan(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, related_name='client_plans')
    
    # Plan type field (e.g., Standard, Advanced)
    plan_type = models.CharField(max_length=255, blank=True, null=True)
    
    # Attributes of the plan (e.g., number of posts, reels, etc.)
    attributes = models.JSONField(default=dict, blank=True, help_text="Attributes of the plan")
    
    # Platforms on which the plan will be implemented (e.g., Facebook, Instagram)
    platforms = models.JSONField(default=dict, blank=True, help_text="Platforms like Facebook, Instagram")
    
    # Add-ons or extra features associated with the plan
    add_ons = models.JSONField(default=dict, blank=True, help_text="Additional add-ons for the plan")
    
    # Grand total price for the plan
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Timestamps for when the plan was created and last updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.client.business_name} - {self.plan_type} Plan"
   
   
# WEB DEV
# class ClientWebDevData(models.Model):
#     WEBSITE_TYPE_CHOICES = [
#         ('ecommerce', 'Ecommerce'),
#         ('services', 'Offer Services'),
#     ]

#     MEMBERSHIP_CHOICES = [
#         ('yes', 'Yes'),
#         ('no', 'No'),
#     ]

#     YES_NO_CHOICES = [
#         ('yes', 'Yes'),
#         ('no', 'No'),
#     ]

#     client = models.ForeignKey(Clients, on_delete=models.CASCADE, related_name='webdevdata')
#     website_type = models.CharField(max_length=20, choices=WEBSITE_TYPE_CHOICES)
#     num_of_products = models.IntegerField(null=True, blank=True)  # Only for ecommerce
#     membership = models.CharField(max_length=3, choices=MEMBERSHIP_CHOICES)
#     website_structure = models.TextField(blank=True, null=True)
#     design_preference = models.TextField(blank=True, null=True)
#     domain = models.CharField(max_length=3, choices=YES_NO_CHOICES)
#     domain_info = models.CharField(max_length=255, blank=True, null=True)  # Only if domain is yes
#     hosting = models.CharField(max_length=3, choices=YES_NO_CHOICES)
#     hosting_info = models.CharField(max_length=255, blank=True, null=True)  # Only if hosting is yes
#     graphic_assets = models.CharField(max_length=3, choices=YES_NO_CHOICES)
#     is_regular_update = models.CharField(max_length=3, choices=YES_NO_CHOICES)
#     is_self_update = models.CharField(max_length=3, choices=YES_NO_CHOICES)
#     additional_notes = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f'{self.client.business_name} Web Development Data'


class PostAttribute(models.Model):
    ATTRIBUTE_TYPE_CHOICES = [
        ('post_type', 'Post Type'),
        ('post_cta', 'Post CTA'),
        ('post_category', 'Post Category'),
    ]

    name = models.CharField(max_length=255)
    attribute_type = models.CharField(max_length=50, choices=ATTRIBUTE_TYPE_CHOICES)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.attribute_type})"

# CALENDER 
class ClientCalendar(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, related_name='calendars')
    created_at = models.DateTimeField(default=timezone.now)
    month_name = models.TextField()
    # New fields to track completion status
    strategy_completed = models.BooleanField(default=False)
    content_completed = models.BooleanField(default=False)
    creatives_completed = models.BooleanField(default=False)
    mm_content_completed = models.BooleanField(default=False)
    acc_creative_completed = models.BooleanField(default=False)
    mm_creative_completed = models.BooleanField(default=False)
    acc_content_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client} - {self.month_name} {self.year}"

    class Meta:
        verbose_name = 'Client Calendar'
        verbose_name_plural = 'Client Calendars'

class ClientCalendarDate(models.Model):
    calendar = models.ForeignKey(ClientCalendar, on_delete=models.CASCADE, related_name='dates')
    created_at = models.DateTimeField(default=timezone.now)
    date = models.TextField()
    post_count = models.IntegerField(default=0)

    # Changed back to CharField to store a single value
    type = models.CharField(max_length=20, blank=True, null=True)  # Single post type
    category = models.CharField(max_length=100, blank=True, null=True)  # Single category
    cta = models.CharField(max_length=255, blank=True, null=True, verbose_name='Call to Action')  # Single CTA
    
    resource = models.TextField(blank=True, null=True, help_text="Strategy description for this post date")
    tagline = models.CharField(max_length=255, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    hashtags = models.TextField(blank=True, null=True, help_text="Use commas to separate hashtags")
    e_hooks = models.TextField(blank=True, null=True, verbose_name='Engagement Hooks')
    creatives_text = models.TextField(blank=True, null=True, help_text="Describe the creatives text")
    creatives = models.FileField(upload_to='creatives/', null=True, blank=True, help_text="Upload the creatives file or provide a URL")


    # Internal status stored as a JSON field
    internal_status = models.JSONField(default=dict, blank=True)
    # Client approval stored as a JSON field
    client_approval = models.JSONField(default=dict, blank=True)

    comments = models.TextField(blank=True, null=True)
    collaboration = models.TextField(blank=True, null=True)

    # Validation for internal_status and client_approval fields
    def clean(self):
        allowed_values = ['content_approval', 'creatives_approval']

        # Validate internal_status
        if not isinstance(self.internal_status, dict):
            raise ValidationError("internal_status must be a JSON object.")
        if len(self.internal_status.keys()) > 2:
            raise ValidationError("internal_status can only contain two fields: 'content_approval' and 'creatives_approval'.")
        for key in self.internal_status.keys():
            if key not in allowed_values:
                raise ValidationError(f"Invalid value '{key}' in internal_status. Only 'content_approval' and 'creatives_approval' are allowed.")

        # Validate client_approval
        if not isinstance(self.client_approval, dict):
            raise ValidationError("client_approval must be a JSON object.")
        if len(self.client_approval.keys()) > 2:
            raise ValidationError("client_approval can only contain two fields: 'content_approval' and 'creatives_approval'.")
        for key in self.client_approval.keys():
            if key not in allowed_values:
                raise ValidationError(f"Invalid value '{key}' in client_approval. Only 'content_approval' and 'creatives_approval' are allowed.")

    def __str__(self):
        return f"{self.calendar} - {self.date}"

    class Meta:
        verbose_name = 'Client Calendar Date'
        verbose_name_plural = 'Client Calendar Dates'


#CLIENT INVOICES
class ClientInvoices(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, related_name='clients_invoices')
    billing_from = models.TextField(null=True, blank=True)
    billing_to = models.TextField(null=True, blank=True)
    invoice = models.FileField(upload_to='invoices/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    INVOICE_STATUS_CHOICES=[
        ('paid', 'PAID'),
        ('unpaid', 'UNPAID'),
    ]
    submission_status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, null=True, blank=True)

# TEAM 
class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='created_teams')

    def __str__(self):
        return self.name

# TEAM MEMBERS 
class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='team_memberships')
    
    def __str__(self):
        return f"{self.user.username} in {self.team.name} as {self.user.get_role_display()}"

    class Meta:
        unique_together = ('team', 'user')  # Ensures that a user can only be in a team once

# MEETINGS 
class Meeting(models.Model):
    MEETING_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    date = models.DateField(default=timezone.now)
    time = models.TimeField()
    meeting_name = models.CharField(max_length=255)
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    
    # New field: Store time zone information
    timezone = models.CharField(max_length=50, blank=True, null=True)

    client = models.ForeignKey(Clients, on_delete=models.CASCADE, related_name='meetings', null=True, blank=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='meetings', blank=True, null=True)
    marketing_manager = models.ForeignKey('CustomUser', on_delete=models.CASCADE, limit_choices_to={'role': 'Marketing Manager'}, blank=True, null=True)
    scheduled_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='scheduled_meetings')
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.meeting_name} on {self.date} at {self.time}"

    class Meta:
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'

#TASK
class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ('assign_team', 'Assign Team to Client'),
        ('create_proposal', 'Create Proposal'),
        ('approve_proposal', 'Approve Proposal'),
        ('schedule_brief_meeting', 'Schedule Brief Meeting'),
        ('create_strategy', 'Create Strategy'),
        ('content_writing', 'Content Writing'),
        ('approve_content_by_marketing_manager', 'Approve Content by Marketing Manager'),
        ('approve_content_by_account_manager', 'Approve Content by Account Manager'),
        ('creatives_design', 'Creatives Designing'),
        ('approve_creatives_by_marketing_manager', 'Approve Creatives by Marketing Manager'),
        ('approve_creatives_by_account_manager', 'Approve Creatives by Account Manager'),
        ('schedule_onboarding_meeting', 'Schedule Onboarding Meeting'),
        ('onboarding_meeting', 'Onboarding Meeting'),
        ('smo_scheduling', 'SMO & Scheduling'),
        ('invoice_submission', 'Invoice Submission'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('monthly_report', 'Monthly Reporting'),
    ]

    client = models.ForeignKey('Clients', on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks')
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_type} for {self.client.business_name} - Assigned to: {self.assigned_to.username}"

class ClientWorkflowState(models.Model):
    client = models.OneToOneField('Clients', on_delete=models.CASCADE)
    current_step = models.CharField(max_length=50, choices=Task.TASK_TYPE_CHOICES)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Workflow for {self.client.business_name} - Current Step: {self.current_step}"

class ClientStatus(models.Model):
    client = models.OneToOneField('Clients', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='In Progress')

    def __str__(self):
        return f"Status for {self.client.business_name}: {self.status}"
   
class ClientMessageThread(models.Model):
    client = models.ForeignKey('Clients', on_delete=models.CASCADE, related_name='message_threads')
    sender = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Client Message Thread'
        verbose_name_plural = 'Client Message Threads'
        ordering = ['-created_at']

    def sender_info(self):
        # Retrieve the required details from the sender
        if self.sender:
            return {
                "id": self.sender.id,
                "name": f"{self.sender.first_name} {self.sender.last_name}",
                "role": self.sender.get_role_display(),
                "profile_image": self.sender.profile.url if self.sender.profile else None,  # Adjusted for profile image
            }
        return None

    def __str__(self):
        return f"Message by {self.sender} in thread for client {self.client.business_name}"

#notes
class Notes(models.Model):
    """A model to represent notes/messages related to a team."""
    message = models.TextField()
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='notes', help_text="The team this note is related to.")
    sender = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notes', help_text="The user who created the note.")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, help_text="The timestamp when the note was last updated.")

    def __str__(self):
        return f"Note by {self.sender} for Team {self.team} - Created on {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['-created_at']
    
class Strategy(models.Model):
    client = models.ForeignKey('Clients', on_delete=models.CASCADE, related_name='strategies')
    created_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()  # Stores HTML
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Strategy: {self.title} for {self.client.business_name}"
    
    