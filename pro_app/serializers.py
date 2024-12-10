from rest_framework import serializers
from . import models

class AccountManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ['id', 'first_name', 'last_name']

class PlanSerializer(serializers.ModelSerializer):
    account_managers = serializers.SerializerMethodField()

    class Meta:
        model = models.Plans
        fields = '__all__'

    def validate_standard_attributes(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Standard attributes must be a dictionary.")
        return value

    def validate_advanced_attributes(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Advanced attributes must be a dictionary.")
        return value
    
    def get_account_managers(self, obj):
        # Return a list of dictionaries, each containing an account manager's ID and full name
        return [
            {"id": manager.id, "name": f"{manager.first_name} {manager.last_name}"}
            for manager in obj.account_managers.all()
        ]

class PlanAssignSerializer(serializers.ModelSerializer):
    account_managers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.CustomUser.objects.all()
    )

    class Meta:
        model = models.Plans
        fields = ['plan_name', 'account_managers']

class ClientsPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientsPlan
        fields = ['plan_type', 'attributes', 'platforms', 'add_ons', 'grand_total', 'created_at', 'updated_at']

# USERS 
class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    teams = serializers.SerializerMethodField()
    profile = serializers.ImageField(allow_null=True, required=False)  # New field for profile picture
    email = serializers.EmailField(required=False)  # Set email as optional for partial update
    username = serializers.CharField(required=False)  # Set username as optional

    class Meta:
        model = models.CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'agency_name', 
                  'role_display', 'is_active', 'date_joined', 'teams', 'profile']  # Added profile

    def get_teams(self, user):
        memberships = models.TeamMembership.objects.filter(user=user)
        teams = [membership.team for membership in memberships]
        return TeamSerializer(teams, many=True).data

    def validate(self, data):
        if data.get('role') == 'account_manager' and not data.get('agency_name'):
            raise serializers.ValidationError({
                'agency_name': 'This field is required for account managers.'
            })
        return data

class UserRoleSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    teams = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = models.CustomUser
        fields = ['id', 'username', 'full_name', 'role_display', 'teams']

    def get_full_name(self, user):
        # Combine first and last names
        return f"{user.first_name} {user.last_name}".strip()

    def get_teams(self, user):
        memberships = models.TeamMembership.objects.filter(user=user)
        teams = [membership.team.name for membership in memberships]  # Return only team names
        return teams

# CLIENTS 
# class ClientSerializer(serializers.ModelSerializer):
#     # Get a single plan for the client, if it exists
#     client_plan = serializers.SerializerMethodField()
#     team = serializers.SerializerMethodField()  # Custom field for team with ID and name

#     class Meta:
#         model = models.Clients
#         fields = '__all__'
#         extra_kwargs = {
#             'account_manager': {'required': False},
#         }

#     def get_client_plan(self, obj):
#         # Retrieve the latest or most relevant plan for the client
#         client_plan = obj.client_plans.first()
#         if client_plan:
#             return {
#                 "id": client_plan.id,
#                 "plan_type": client_plan.plan_type,
#                 "attributes": client_plan.attributes,
#                 "platforms": client_plan.platforms,
#                 "add_ons": client_plan.add_ons,
#                 "grand_total": client_plan.grand_total,
#                 "created_at": client_plan.created_at,
#                 "updated_at": client_plan.updated_at
#             }
#         return None

#     def get_team(self, obj):
#         # Include both team ID and name if a team is assigned
#         if obj.team:
#             return {
#                 "id": obj.team.id,
#                 "name": obj.team.name
#             }
#         return None
    
#     #CONDITION FOR DUPLICATE BUSINESS NAMES
#     def validate_business_name(self, value):
#         if models.Clients.objects.filter(business_name__iexact=value).exists():
#             raise serializers.ValidationError("A client with this business name already exists.")
#         return value

# class ClientWebDevDataSerializer(serializers.ModelSerializer):
#     client = serializers.PrimaryKeyRelatedField(read_only=True)  # Make client read-only, as it will be set in the view
#     class Meta:
#         model = models.ClientWebDevData
#         fields = '__all__'

#     def validate(self, data):
#         # Conditional field validation
#         if data['website_type'] == 'ecommerce' and not data.get('num_of_products'):
#             raise serializers.ValidationError("Number of products is required for eCommerce websites.")
#         if data['domain'] == 'yes' and not data.get('domain_info'):
#             raise serializers.ValidationError("Domain information is required if domain is 'yes'.")
#         if data['hosting'] == 'yes' and not data.get('hosting_info'):
#             raise serializers.ValidationError("Hosting information is required if hosting is 'yes'.")
#         return data

#AFTER MERGE
class ClientSerializer(serializers.ModelSerializer):
    # Get a single plan for the client, if it exists
    client_plan = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()  # Custom field for team with ID and name

    class Meta:
        model = models.Clients
        fields = '__all__'
        extra_kwargs = {
            'account_manager': {'required': False},
        }

    def get_client_plan(self, obj):
        # Retrieve the latest or most relevant plan for the client
        client_plan = obj.client_plans.first()
        if client_plan:
            return {
                "id": client_plan.id,
                "plan_type": client_plan.plan_type,
                "attributes": client_plan.attributes,
                "platforms": client_plan.platforms,
                "add_ons": client_plan.add_ons,
                "grand_total": client_plan.grand_total,
                "created_at": client_plan.created_at,
                "updated_at": client_plan.updated_at
            }
        return None

    def get_team(self, obj):
        # Include both team ID and name if a team is assigned
        if obj.team:
            return {
                "id": obj.team.id,
                "name": obj.team.name
            }
        return None

    # Field-level validation
    def validate_business_name(self, value):
        if models.Clients.objects.filter(business_name__iexact=value).exists():
            raise serializers.ValidationError("A client with this business name already exists.")
        return value

    # Object-level validation
    def validate(self, data):
        # Conditional field validation for web development data fields
        if data.get('website_type') == 'ecommerce' and not data.get('num_of_products'):
            raise serializers.ValidationError("Number of products is required for eCommerce websites.")
        if data.get('domain') == 'yes' and not data.get('domain_info'):
            raise serializers.ValidationError("Domain information is required if domain is 'yes'.")
        if data.get('hosting') == 'yes' and not data.get('hosting_info'):
            raise serializers.ValidationError("Hosting information is required if hosting is 'yes'.")
        return data


class PostAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostAttribute
        fields = ['id', 'name', 'attribute_type', 'is_active']

    def validate_name(self, value):
        """
        Check for duplicate names.
        """
        # Ensure the name is unique, ignoring the instance itself during updates
        if models.PostAttribute.objects.filter(name__iexact=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("An attribute with this name already exists.")
        return value
    
# CALENDER 
class ClientCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientCalendar
        fields = [
            'client',  'created_at',  'month_name', 'strategy_completed',  'content_completed',
            'creatives_completed',  'mm_content_completed', 'acc_creative_completed','mm_creative_completed',
            'acc_content_completed'
        ]

class ClientCalendarDateSerializer(serializers.ModelSerializer):
    # proposal_pdf = serializers.FileField(required=False)
    calendar = serializers.PrimaryKeyRelatedField(queryset=models.ClientCalendar.objects.all())

    class Meta:
        model = models.ClientCalendarDate
        fields = '__all__'

class FilteredClientCalendarDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientCalendarDate
        fields = [
            'id',
            'calendar','created_at','date','post_count','type','category',
            'cta','strategy','resource','tagline','caption','hashtags','creatives',
            'e_hooks','client_approval','comments'
        ]

class ClientInvoicesSerializer(serializers.ModelSerializer):
    # client = serializers.PrimaryKeyRelatedField(queryset=models.Clients.objects.all())
    class Meta:
        model = models.ClientInvoices
        fields = '__all__'
        extra_kwargs = {
            'client': {'required': False}  # Make client field not required from the request body
        }

class ClientProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Clients
        fields = ['proposal_pdf', 'proposal_approval_status']

# TEAM 
class TeamSerializer(serializers.ModelSerializer):
    # Add fields for member and client counts
    members_count = serializers.SerializerMethodField()
    clients_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Team
        fields = ['id', 'name', 'description', 'created_by', 'members_count', 'clients_count']

    # Serializer method to get the number of members in the team
    def get_members_count(self, obj):
        return obj.memberships.count()

    # Serializer method to get the number of clients associated with the team
    def get_clients_count(self, obj):
        return models.Clients.objects.filter(team=obj).count()

class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = models.TeamMembership
        fields = ['id', 'team', 'user', 'user_id']

class AssignClientToTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Clients
        fields = ['id', 'business_name', 'team']

# MEETINGS 
class MeetingSerializer(serializers.ModelSerializer):
    # Read-only fields for existing data
    scheduled_by_id = serializers.IntegerField(source='scheduled_by.id', read_only=True)
    client_name = serializers.CharField(source='client.business_name', read_only=True)  
    client = serializers.PrimaryKeyRelatedField(queryset=models.Clients.objects.all())

    # Custom field to return an array with required data
    details = serializers.SerializerMethodField()

    class Meta:
        model = models.Meeting
        fields = [
            'id', 'date', 'time', 'meeting_name', 'meeting_link', 'timezone', 'client', 'client_name', 'team', 
            'is_completed', 'scheduled_by_id', 'details'
        ]

    def get_details(self, obj):
        return [
            obj.team.name if obj.team else None,
            obj.scheduled_by.role if obj.scheduled_by else None,
            obj.marketing_manager.role if obj.marketing_manager else None
        ]

class SpecificMeetingSerializer(serializers.ModelSerializer):
    # Read-only fields for existing data
    client_name = serializers.CharField(source='client.business_name', read_only=True)
    
    # Custom field to return an array with required data
    details = serializers.SerializerMethodField()

    class Meta:
        model = models.Meeting
        fields = [
            'id', 'date', 'time', 'meeting_name', 'meeting_link', 'timezone', 'client', 'client_name',
            'is_completed', 'scheduled_by_id', 'details'
        ]

    def get_details(self, obj):
        details_list = [
            obj.scheduled_by.role if obj.scheduled_by else None,
            obj.team.name if obj.team else "No team assigned with this client",
            obj.marketing_manager.role if obj.marketing_manager else None
        ]
        # Remove any None values from the list
        return [detail for detail in details_list if detail is not None]

# TASKS 
class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    client_name = serializers.CharField(source='client.business_name', read_only=True)

    class Meta:
        model = models.Task
        fields = ['id', 'task_type', 'client', 'client_name', 'assigned_to', 'assigned_to_name', 'is_completed', 'created_at']
        read_only_fields = ['created_at']

class MyTaskSerializer(serializers.ModelSerializer):
    client_business_name = serializers.CharField(source='client.business_name', read_only=True)

    class Meta:
        model = models.Task
        fields = ['id', 'created_at', 'task_type', 'client_business_name'] 

# CLIENT PLAN 
class ClientPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClientsPlan
        fields = '__all__'
        extra_kwargs = {
            "client": {'read_only': True},
        }

class ClientMessageThreadSerializer(serializers.ModelSerializer):
    sender_info = serializers.SerializerMethodField()

    class Meta:
        model = models.ClientMessageThread
        fields = ['id', 'client', 'sender', 'message', 'created_at', 'sender_info']

    def get_sender_info(self, obj):
        return obj.sender_info()  # Calls sender_info method to get details

class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notes
        fields = ['id', 'message', 'team', 'sender', 'created_at', 'updated_at']
        read_only_fields = ['sender', 'created_at', 'updated_at']


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Strategy
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
