from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [

    # AUTHENTICATION ROUTES
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh JWT token
    path('auth/token/verify', TokenVerifyView.as_view(), name='token_verify'),  # Verify JWT token
    path('auth/login', views.LoginView.as_view(), name='login'),  # User login
    path('auth/logout', views.LogoutView.as_view(), name='logout'),  # User logout
    path('auth/set-password/<uidb64>/<token>', views.SetPasswordView.as_view(), name='set-password'),  # Set password with token
    path('password/forgot', views.ForgotPasswordView.as_view(), name='forgot-password'),  # Forgot password
    path('password/reset-confirm/<uidb64>/<token>', views.ResetPasswordConfirmView.as_view(), name='password-reset-confirm'),  # Reset password with token
    path('auth/profile', views.ProfileView.as_view(), name='profile'),  # Get user profile
    path('auth/profile/update', views.UpdateProfileView.as_view(), name='update_profile'),  # Update user profile

    # USER MANAGEMENT
    path('users', views.ListUsersView.as_view(), name='list-users'),  # List all users
    path('users/create', views.AdminCreateUserView.as_view(), name='create-user'),  # Admin creates a user
    path('users/<int:id>', views.UsersView.as_view(), name='user'),  # Retrieve, update, or delete a user by ID
    path('users/by-role', views.UserListByRoleView.as_view(), name='users-by-role'),  # List users filtered by role

    # # CLIENTS MANAGEMENT
    # path('clients', views.ClientListCreateView.as_view(), name='clients-list-create'),  # List or create clients
    # path('clients/<int:pk>', views.ClientDetailView.as_view(), name='client-detail'),  # Get, update, or delete a client by ID
    # path('clients/<int:id>/webdevdata', views.ClientWebDevDataListCreateView.as_view(), name='webdevdata-list-create'),  # List or create web development data for a client
    # path('clients/webdevdata/<int:pk>', views.ClientWebDevDataDetailView.as_view(), name='webdevdata-detail'),  # Get, update, or delete web development data by ID
    
    # List and create clients and webdev data
    path('clients', views.ClientWebDevDataListCreateView.as_view(), name='clients-list-create'),
    # Retrieve, update, or delete a specific client and its webdev data
    path('clients/<int:pk>', views.ClientWebDevDataDetailView.as_view(), name='client-detail'),
    
    
    #DYNAMIC POST ATTRIBUTES
    path('post-attributes', views.PostAttributeListCreateView.as_view(), name='post-attribute-create'),
    path('post-attributes/<str:attribute_type>', views.PostAttributeByTypeView.as_view(), name='post-attribute-by-type'),
    path('post-attributes/update/<int:pk>', views.PostAttributeUpdateView.as_view(), name='post-attribute-update'),

    # Routes for ClientCalendar
    path('clients/<int:id>/calendars', views.ClientCalendarListCreateView.as_view(), name='calendar-list-create'),
    path('clients/<int:client_id>/calendars/<int:pk>', views.ClientCalendarRetrieveUpdateDeleteView.as_view(), name='calendar-rud'),
    
    # Routes for ClientCalendarDate
    path('calendars/<int:calendar_id>/dates', views.ClientCalendarDateListCreateView.as_view(), name='calendar-date-list-create'),
    path('calendars/<int:calendar_id>/dates/<int:pk>', views.ClientCalendarDateRetrieveUpdateDeleteView.as_view(), name='calendar-date-rud'),
   
    path('clients/<int:pk>/assign-team', views.AssignClientToTeamView.as_view(), name='assign-client-to-team'),  # Assign a client to a team 
    path('clients/<int:client_id>/update-workflow', views.UpdateClientWorkflowView.as_view(), name='update-client-workflow'),  # Update client's workflow
    path('clients/<int:client_id>/proposal', views.UploadProposalView.as_view(), name='upload-proposal'),  # Handle proposal: GET (retrieve), PUT (upload), DELETE (remove)
    
    #CALENDER DATA FOR CLIENT
    path('clients/<int:client_id>/calendar-data/<str:month_name>', views.ClientCalendarByMonthView.as_view(), name='calendar-data-by-month'),
    # FOR CALENDAR DATE CRUD USE THIS EXISTING ROUTE 
    # path('clients/<int:client_id>/calendars/<int:pk>', views.ClientCalendarRetrieveUpdateDeleteView.as_view(), name='calendar-rud'),

    # CLIENTS PLAN 
    path('clients/<int:client_id>/plans', views.ClientPlanListCreateView.as_view(), name='client-plan-list-create'),
    path('clients/<int:client_id>/plans/<int:plan_id>', views.ClientPlanRetrieveUpdateDeleteView.as_view(), name='client-plan-rud'),

    #CLIENT INVOICE
    path('clients/<int:client_id>/invoices', views.ClientInvoicesListCreateView.as_view(), name='client-invoices-list-create'),
    path('clients/<int:client_id>/invoices/<int:pk>', views.ClientInvoicesRetrieveUpdateDeleteView.as_view(), name='client-invoices-rud'),

    # TEAM MANAGEMENT ROUTES
    path('teams', views.TeamListCreateView.as_view(), name='create-list-teams'),  # List or create teams
    path('teams/<int:pk>', views.TeamRetrieveUpdateDeleteView.as_view(), name='team-rud'),  # Retrieve, update, or delete a team by ID

    # MEETING MANAGEMENT
    path('meetings', views.MeetingListCreateView.as_view(), name='meeting-list-create'),  # List or create meetings
    path('meetings/<int:pk>', views.MeetingRetrieveUpdateDeleteView.as_view(), name='update-delete-meeting-meetingstatus'),  # Get, update, or delete a meeting by ID

    # TASK MANAGEMENT
    path('tasks/<int:task_id>/complete', views.CompleteTaskView.as_view(), name='complete-task'),  # Mark a task as complete
    path('tasks', views.TaskListView.as_view(), name='task-list'),  # List all tasks
    path('my/tasks', views.UserAssignedTaskListView.as_view(), name='user-assigned-tasks'),  # List tasks assigned to the current user

    # Routes for the PlanView
    path('plans', views.PlanView.as_view(), name='plan-list-create'),
    path('plans/<int:pk>', views.PlanView.as_view(), name='plan-rud'),
    
    path('plans/<int:pk>/assign', views.PlanAssignView.as_view(), name='assign-plan-to-managers'),
    path('search-unassigned-account-managers', views.UnassignedAccountManagerSearchView.as_view(), name='search-unassigned-account-managers'),
    
    
    # GET /api/search-assigned-account-managers/?plan_id=1
    
    path('assigned-account-managers-list', views.AssignedAccountManagerSearchView.as_view(), name='search-assigned-account-managers'),
    
    path('plans/<int:client_id>/account-manager-plans', views.AssignedPlansForAccountManagerView.as_view(), name='assigned-plans-for-account-manager'),
    
    path('remove-account-manager', views.RemoveAccountManagerFromPlanView.as_view(), name='removed-account-managers-from-plan'),
    
    path('clients/<int:client_id>/threads', views.ThreadMessageListCreateView.as_view(), name='thread-message-list-create'),
    
    path('notes/create', views.CreateNoteView.as_view(), name='create_note'),
    
    # url for proposal is created then work for check proposal approval task 
    # path('clients/<int:client_id>/calendar/<int:pk>/proposal', views.ProposalView.as_view(), name='proposal-detail'),
    
    
    path('strategies/', views.StrategyListCreateView.as_view(), name='strategy_list_create'),
    path('strategies/<int:pk>/', views.StrategyEditDeleteView.as_view(), name='strategy_edit_delete'),
    path('strategies/<int:pk>/assign/', views.StrategyAssignView.as_view(), name='strategy_assign'),

] 




