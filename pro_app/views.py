from .imports import (  
    APIView, Response, Request, status, generics, AllowAny, settings, TokenObtainPairView, RefreshToken, TokenRefreshView,
    send_mail, get_connection, default_token_generator, datetime, timedelta, JsonResponse,
    urlsafe_base64_decode, urlsafe_base64_encode, force_bytes, reverse, get_object_or_404, 
    smtplib, MIMEText, MIMEMultipart, authenticate, IsAuthenticated, get_user_model, RefreshToken, MultiPartParser, FormParser
    ,create_task, update_client_workflow, mark_task_as_completed, get_next_step_and_user,update_client_status,pytz_timezone, make_aware, utc,Q
,PermissionDenied
)
from . import models
from . import serializers 

# AUTH 
class CustomTokenObtainPairView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Set token expiration
            access_token.set_exp(
                lifetime=timedelta(minutes=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds // 60))

            # Create the response
            response = Response({
                'message': 'Login successful',
            }, status=status.HTTP_200_OK)

            # Set the access token in the cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],  # Cookie name from settings
                value=str(access_token),  # Token value
                expires=access_token.payload['exp'],  # Expiration time
                httponly=True,  # Prevent client-side JavaScript access
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],  # Should be True in production with HTTPS
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],  # To prevent CSRF attacks
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']  # Path scope for the cookie
            )

            return response
        else:
            return Response({"detail": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token not found."}, status=401)

        request.data['refresh'] = refresh_token
        return super().post(request, *args, **kwargs)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow this view to be accessible to everyone
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            response = JsonResponse({
                'message': 'Login successful',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'role_display': user.get_role_display(),
                },
                'access_token': access_token,
                'refresh_token': refresh_token
            })
            return response
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class AdminCreateUserView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = data.get('role')

        agency_name = data.get('agency_name')

        # Check if the role is 'account_manager' and validate the agency_name
        if role == 'account_manager' and not agency_name:
            return Response({"message": "Agency name is required for account managers."}, status=status.HTTP_400_BAD_REQUEST)

        if models.CustomUser.objects.filter(email=email).exists():
            return Response({"message": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        # Create a user without a password
        user = models.CustomUser.objects.create(email=email, first_name=first_name, last_name=last_name, role=role,agency_name=agency_name, is_active=False)
        user.save()
        # Generate token for setting password
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        # Build the password reset URL
        set_password_url = f"{settings.FRONTEND_DOMAIN}/set-password/{uid}/{token}"
        # Manually construct the email
        subject = "Set your password"
        body = f"Hi {first_name}, please set your password using the following link: {set_password_url}"
        message = MIMEMultipart()
        message['From'] = 'abbas.dksolutions@gmail.com'
        message['To'] = email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        try:
            # Connect to the SMTP server using smtplib
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('abbas.dksolutions@gmail.com', 'tsidcvtigttqbxll')
            server.sendmail('abbas.dksolutions@gmail.com', email, message.as_string())
            server.quit()
            return Response({"message": "User created and email sent to set password"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SetPasswordView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access this view without authentication

    def post(self, request, uidb64, token, *args, **kwargs):
        password = request.data.get('password')

        try:
            # Decode the user id from the uidb64
            user_id = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(models.CustomUser, pk=user_id)
        except (TypeError, ValueError, OverflowError, models.CustomUser.DoesNotExist):
            return Response({"error": "Invalid UID or user does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the token
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid token or token has expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(password)
        user.is_active = True  # Activate user after password is set
        user.save()

        return Response({"message": "Password has been set successfully"}, status=status.HTTP_200_OK)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email exists in the system
        try:
            user = models.CustomUser.objects.get(email=email)
            username = user.username
            print(f"Fetched Username: {username}")  # Debugging: Check if username is being fetched
        except models.CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate a token and uidb64 to send in the email
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build the password reset URL
        reset_url =  f"{settings.FRONTEND_DOMAIN}/password/reset-confirm/{uid}/{token}"

        # Send the email
        subject = "Reset your password"
        body = f"Hi {username}, please reset your password using the following link: {reset_url}"
        message = MIMEMultipart()
        message['From'] = 'abbas.dksolutions@gmail.com'
        message['To'] = email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        try:
            # Connect to the SMTP server using smtplib
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('abbas.dksolutions@gmail.com', 'tsidcvtigttqbxll')
            server.sendmail('abbas.dksolutions@gmail.com', email, message.as_string())
            server.quit()
            return Response({"message": "User created and email sent to reset password"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)

class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token, *args, **kwargs):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the user id from the uidb64
            user_id = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(models.CustomUser, pk=user_id)
        except (TypeError, ValueError, OverflowError, models.CustomUser.DoesNotExist):
            return Response({"error": "Invalid UID or user does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the token
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid token or token has expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)

# USERS 
class ListUsersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]  # Change to `AllowAny` if needed
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserSerializer
    
class UsersView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]  # Set appropriate permissions
    serializer_class = serializers.UserSerializer
    queryset = models.CustomUser.objects.all()
    lookup_field = 'id'

class UserListByRoleView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.UserRoleSerializer

    def get_queryset(self):
        # Get the 'role' parameter from the request's query params
        role = self.request.query_params.get('role')
        if role:
            return models.CustomUser.objects.filter(role=role, is_active=True)
        else:
            return models.CustomUser.objects.none()  # Return an empty queryset if no role is provided

# PROFILE 
class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user
    
class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        """Override patch to allow partial update with partial=True."""
        return self.partial_update(request, partial=True, *args, **kwargs)


# CLIENTS 
# class ClientListCreateView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = models.Clients.objects.all()
#     serializer_class = serializers.ClientSerializer

#     def perform_create(self, serializer):
#         # Automatically set the account_manager to the currently authenticated user
#         if self.request.user.role == 'account_manager':
#             serializer.save(account_manager=self.request.user)
#         else:
#             raise PermissionDenied("Only Account Manager can create a client.")

# class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAuthenticated]  # Update based on your needs
#     queryset = models.Clients.objects.all()
#     serializer_class = serializers.ClientSerializer
    
#     def update(self, request, *args, **kwargs):
#         # Get the client instance
#         client = self.get_object()

#         # Use partial=True to allow partial updates (only updating the provided fields)
#         serializer = self.get_serializer(client, data=request.data, partial=True)

#         # Validate the serializer
#         if serializer.is_valid():
#             # Save the updated client data without overwriting other fields
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # List all or Create WebDevData for a specific Client
# class ClientWebDevDataListCreateView(generics.ListCreateAPIView):
#     permission_classes = [AllowAny]
#     queryset = models.ClientWebDevData.objects.all()
#     serializer_class = serializers.ClientWebDevDataSerializer

#     def perform_create(self, serializer):
#         client_id = self.kwargs.get('id')  # Get client ID from the URL
#         client = get_object_or_404(models.Clients, id=client_id)  # Get the client
#         serializer.save(client=client)  # Associate webdevdata with the client

#     def get_queryset(self):
#         # Return all web development data for the specific client
#         client_id = self.kwargs.get('id')
#         return models.ClientWebDevData.objects.filter(client_id=client_id)

#     def post(self, request, *args, **kwargs):
#         client_id = self.kwargs.get('id')
#         client = get_object_or_404(models.Clients, id=client_id)

#         # Serialize the incoming data
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             # Save the webdevdata with the associated client
#             serializer.save(client=client)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
# # Retrieve, Update, or Delete specific WebDevData for a client
# class ClientWebDevDataDetailView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [AllowAny]
#     queryset = models.ClientWebDevData.objects.all()
#     serializer_class = serializers.ClientWebDevDataSerializer

#     def get(self, request, pk, *args, **kwargs):
#         webdev_data = get_object_or_404(models.ClientWebDevData, pk=pk)
#         serializer = self.get_serializer(webdev_data)
#         return Response(serializer.data)

#     def put(self, request, pk, *args, **kwargs):
#         webdev_data = get_object_or_404(models.ClientWebDevData, pk=pk)
#         serializer = self.get_serializer(webdev_data, data=request.data, partial=False)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, *args, **kwargs):
#         webdev_data = get_object_or_404(models.ClientWebDevData, pk=pk)
#         webdev_data.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# MERGE CLIENT AND CLIENT'S WEB DEV DATA
class ClientWebDevDataListCreateView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_classes = {
        'client': serializers.ClientSerializer,
        'webdev_data': serializers.ClientSerializer
    }

    def get(self, request, *args, **kwargs):
        # Handle listing clients and webdev data
        client_id = self.kwargs.get('id', None)

        # If ID is provided, return webdev data for that client
        if client_id:
            webdev_data = models.ClientWebDevData.objects.filter(client_id=client_id)
            serializer = self.serializer_classes['webdev_data'](webdev_data, many=True)
            return Response(serializer.data)

        # Otherwise, return a list of all clients
        clients = models.Clients.objects.all()
        serializer = self.serializer_classes['client'](clients, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Handle creating clients and webdev data
        client_id = self.kwargs.get('id', None)

        if client_id:
            # Create webdev data for specific client
            client = get_object_or_404(models.Clients, id=client_id)
            serializer = self.serializer_classes['webdev_data'](data=request.data)
            if serializer.is_valid():
                serializer.save(client=client)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new client (if no client ID is provided)
        serializer = self.serializer_classes['client'](data=request.data)
        if serializer.is_valid():
            # Automatically set the account_manager to the currently authenticated user
            if self.request.user.role == 'account_manager':
                serializer.save(account_manager=self.request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                raise PermissionDenied("Only Account Manager can create a client.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientWebDevDataDetailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_classes = {
        'client': serializers.ClientSerializer,
        'webdev_data': serializers.ClientSerializer
    }

    def get(self, request, pk, *args, **kwargs):
        # Retrieve specific client or webdev data
        if kwargs.get('id') is None:
            # Retrieve a single client
            client = get_object_or_404(models.Clients, pk=pk)
            serializer = self.serializer_classes['client'](client)
            return Response(serializer.data)

        else:
            # Retrieve specific webdev data for a client
            webdev_data = get_object_or_404(models.ClientWebDevData, pk=pk)
            serializer = self.serializer_classes['webdev_data'](webdev_data)
            return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        # Update client or webdev data
        if kwargs.get('id') is None:
            # Update client
            client = get_object_or_404(models.Clients, pk=pk)
            serializer = self.serializer_classes['client'](client, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            # Update webdev data
            webdev_data = get_object_or_404(models.ClientWebDevData, pk=pk)
            serializer = self.serializer_classes['webdev_data'](webdev_data, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        # Delete client or webdev data
        if kwargs.get('id') is None:
            # Delete client
            client = get_object_or_404(models.Clients, pk=pk)
            client.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            # Delete webdev data
            webdev_data = get_object_or_404(models.ClientWebDevData, pk=pk)
            webdev_data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


#DYNAMIC POST TYPE
class PostAttributeListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.PostAttributeSerializer
    queryset = models.PostAttribute.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the attribute as inactive by default
            post_attribute = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostAttributeByTypeView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.PostAttributeSerializer

    def get_queryset(self):
        # Get the type of the attribute from the URL
        attribute_type = self.kwargs.get('attribute_type')

        # Filter the PostAttribute model by the given type and only active attributes
        return models.PostAttribute.objects.filter(attribute_type=attribute_type)

class PostAttributeUpdateView(generics.UpdateAPIView):
    permission_classes = [AllowAny]
    queryset = models.PostAttribute.objects.all()
    serializer_class = serializers.PostAttributeSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Allow partial updates by default
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            # Save the updated attribute, reflecting any changes
            serializer.save()

            # Handle any special cases for activated or deactivated attributes if necessary
            if 'is_active' in request.data:
                if request.data['is_active']:  # If the attribute is activated
                    print(f"Attribute '{instance.name}' activated.")
                else:  # If the attribute is deactivated
                    print(f"Attribute '{instance.name}' deactivated.")

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#CALENDER
class ClientCalendarListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.ClientCalendarSerializer

    def get_queryset(self):
        client_id = self.kwargs.get('id')
        return models.ClientCalendar.objects.filter(client_id=client_id)

    def post(self, request, *args, **kwargs):
         # Check if the user is a marketing manager
        if request.user.role != 'marketing_manager':
            return Response({"error": "Only marketing managers can create calendars."}, status=status.HTTP_403_FORBIDDEN)

        client_id = self.kwargs.get('id')
        client = get_object_or_404(models.Clients, id=client_id)
        month_name = request.data.get('month_name')

        calendar = models.ClientCalendar.objects.create(client=client, month_name=month_name)
        serializer = self.get_serializer(calendar)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ClientCalendarRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.ClientCalendarSerializer

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        return models.ClientCalendar.objects.filter(client_id=client_id)

    def delete(self, request, *args, **kwargs):
        # Restrict deletion to marketing managers
        if request.user.role != 'marketing_manager':
            return Response({"error": "Only marketing managers can delete calendars."}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # Restrict updates to certain roles
        if request.user.role not in ['marketing_manager', 'account_manager', 'content_writer', 'graphics_designer']:
            return Response({"error": "You are not authorized to update this calendar."}, status=status.HTTP_403_FORBIDDEN)

        # Fetch the calendar instance
        calendar = self.get_object()

        # Check and validate fields based on the role
        if 'strategy_completed' in request.data:
            # Only marketing_manager is allowed to update strategy_completed
            if request.user.role != 'marketing_manager':
                return Response({"error": "Only marketing managers can update strategy completion."}, status=status.HTTP_403_FORBIDDEN)

            # Check if all strategy fields are completed before updating
            if not self._check_all_strategy_completed(calendar):
                return Response({"error": "Not all strategy fields are filled in the calendar dates."}, status=status.HTTP_400_BAD_REQUEST)

        if 'content_completed' in request.data:
            if request.user.role != 'content_writer':
                return Response({"error": "only content writer can update content completion."}, status=status.HTTP_403_FORBIDDEN)
            
            if not self._check_all_content_completed(calendar):
                return Response({"error": "Not all content fields are filled in the calender dates"})

        if 'creatives_completed' in request.data:
            if request.user.role != 'graphics_designer':
                return Response({"error": "Only the graphics designer can update creatives completion."}, status=status.HTTP_403_FORBIDDEN)
            
            missing_dates = self._check_all_creatives_completed(calendar)
            
            if missing_dates is not True:
                return Response({"error": f"Creatives approval missing for the following dates: {', '.join(missing_dates)}"}, status=status.HTTP_400_BAD_REQUEST)

        if 'mm_content_completed' in request.data:
            if request.user.role != 'marketing_manager':
                return Response({"error": "only marketing manager can approved contents."}, status=status.HTTP_403_FORBIDDEN)
            
            if not self._check_all_content_approved_internal_status(calendar):
                return Response({"error": "Not all approved in the internal_status of calender dates"})

        if 'mm_creative_completed' in request.data:
            if request.user.role != 'marketing_manager':
                return Response({"error": "only creatives can update creatives completion."}, status=status.HTTP_403_FORBIDDEN)
            
            if not self._check_all_creatives_approved_internal_status(calendar):
                return Response({"error": "Not all approved in the internal_status of calender dates"})
           
        if 'acc_content_completed' in request.data:
            if request.user.role != 'account_manager':
                return Response({"error": "only account manager can update final content completion."}, status=status.HTTP_403_FORBIDDEN)
            
            if not self._check_all_content_approved_client_approval(calendar):
                return Response({"error": "Not all approved in the client approval of calender dates"})

        if 'acc_creative_completed' in request.data:
            if request.user.role != 'account_manager':
                return Response({"error": "only account manager can update final creatives completion."}, status=status.HTTP_403_FORBIDDEN)
            
            if not self._check_all_creatives_approved_client_approval(calendar):
                return Response({"error": "Not all approved in the client approval of calender dates"})

        # Perform partial updates without overriding existing values
        serializer = self.get_serializer(calendar, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _check_all_strategy_completed(self, calendar):
        # Ensure all strategies are filled in calendar dates
        dates = models.ClientCalendarDate.objects.filter(calendar=calendar)
        for date in dates:
            if not date.resource:
                print(f"Strategy missing for date: {date.date}")
                return False
        return True

    def _check_all_content_completed(self, calendar):
        # Ensure all content fields are completed in calendar dates
        dates = models.ClientCalendarDate.objects.filter(calendar=calendar)
        field_required = ['tagline', 'caption', 'hashtags', 'e_hooks', 'creatives_text']

        # Check each field for each date
        for date in dates:
            for field in field_required:
                field_value = getattr(date, field, None)  # Get field value or None if the field does not exist
                if field_value is None or str(field_value).strip() == "":  # Check for None or empty string
                    print(f"{field.capitalize()} is missing for date: {date.date}")
                    return False  # Exit early if any required field is missing
        
        # Only return True after all dates and fields have been checked
        return True

    def _check_all_creatives_completed(self, calendar):
        # Ensure all creatives fields are completed in calendar dates
        dates = models.ClientCalendarDate.objects.filter(calendar=calendar)
        missing_creatives_dates = []  

        for date in dates:
            if not date.creatives:
                missing_creatives_dates.append(date.date)

        if missing_creatives_dates:
            print(f"Creatives approval missing for the following dates: {', '.join(missing_creatives_dates)}")
            return missing_creatives_dates

        return True


    def _check_all_content_approved_internal_status(self, calendar):
        """Check that `content_approval` is True in `internal_status` for all dates in the calendar."""
        dates = models.ClientCalendarDate.objects.filter(calendar=calendar)

        for date in dates:
            internal_status = date.internal_status or {}

            # Ensure `internal_status` is a dictionary and contains `content_approval`
            if not isinstance(internal_status, dict):
                print(f"Unexpected type for internal_status on date {date.date}: {type(internal_status)}")
                return False

            # Debugging output
            print(f"Checking content approval for date {date.date}: {internal_status}")

            # Check if 'content_approval' exists and is True
            if not internal_status.get('content_approval', False):
                print(f"Content approval missing or not True for date: {date.date}")
                return False

        return True

    def _check_all_creatives_approved_internal_status(self, calendar):
        """Check that `creatives_approval` is True in `internal_status` for all dates in the calendar."""
        dates = models.ClientCalendarDate.objects.filter(calendar=calendar)

        for date in dates:
            internal_status = date.internal_status or {}

            # Ensure `internal_status` is a dictionary and contains `creatives_approval`
            if not isinstance(internal_status, dict):
                print(f"Unexpected type for internal_status on date {date.date}: {type(internal_status)}")
                return False

            # Debugging output
            print(f"Checking creatives approval for date {date.date}: {internal_status}")

            # Check if 'creatives_approval' exists and is True
            if not internal_status.get('creatives_approval', False):
                print(f"Creatives approval missing or not True for date: {date.date}")
                return False

        return True

    def _check_all_content_approved_client_approval(self, calendar):
        # Check if all content fields are approved in the client_approval JSON field
        dates = models.ClientCalendarDate.objects.filter(calendar=calendar)
        for date in dates:
            if 'content_approval' not in date.client_approval or not date.client_approval['content_approval']:
                print(f"Content approval missing in client_approval for date: {date.date}")
                return False
        return True

    def _check_all_creatives_approved_client_approval(self, calendar):
        # Check if all creatives fields are approved in the client_approval JSON field
        dates = models.ClientCalendarDate.objects.filter(calendar=calendar)
        for date in dates:
            if 'creatives_approval' not in date.client_approval or not date.client_approval['creatives_approval']:
                print(f"Creatives approval missing in client_approval for date: {date.date}")
                return False
        return True

class ClientCalendarDateListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.ClientCalendarDateSerializer

    def get_queryset(self):
        calendar_id = self.kwargs.get('calendar_id')
        return models.ClientCalendarDate.objects.filter(calendar_id=calendar_id)

    def post(self, request, *args, **kwargs):
        # Check if the user is a marketing manager
        if request.user.role != 'marketing_manager':
            return Response({"error": "Only marketing managers can create row for next dates."}, status=status.HTTP_403_FORBIDDEN)

        calendar_id = self.kwargs.get('calendar_id')
        calendar = get_object_or_404(models.ClientCalendar, id=calendar_id)
        date = request.data.get('date')

        # Set default values for required fields
        calendar_date = models.ClientCalendarDate.objects.create(
            calendar=calendar,
            date=date,
            type='other',  # Set a default value for 'type' to avoid null error
            category='',  # Default empty string for other required fields
            cta='',
            resource='',
            tagline='',
            caption='',
            hashtags='',
            creatives='',
            e_hooks='',
            internal_status='none',
            client_approval='',
            comments='',
            collaboration=''
        )

        serializer = self.get_serializer(calendar_date)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ClientCalendarDateRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.ClientCalendarDateSerializer

    def get_queryset(self):
        calendar_id = self.kwargs.get('calendar_id')
        return models.ClientCalendarDate.objects.filter(calendar_id=calendar_id)

    def put(self, request, *args, **kwargs):
        # Retrieve the calendar date to be updated
        calendar_date = self.get_object()
        user_role = request.user.role  # Assuming the user has a role attribute

        # Get allowed fields based on role
        allowed_fields = self.get_allowed_fields_by_role(user_role)

        # Ensure client_approval and comments are excluded for restricted roles
        if user_role in ['marketing_manager', 'marketing_assistant', 'content_writer', 'graphics_designer', 'marketing_director']:
            restricted_fields = ['client_approval', 'comments']
            for field in restricted_fields:
                if field in request.data:
                    return Response(
                        {"error": f"{user_role} is not allowed to update {field}."},
                        status=status.HTTP_403_FORBIDDEN
                    )

        # Filter the request data to only include allowed fields
        filtered_data = {key: value for key, value in request.data.items() if key in allowed_fields}

        if not filtered_data:
            return Response(
                {"error": f"{user_role} is not allowed to update the provided fields."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Use partial=True to allow partial updates
        serializer = self.get_serializer(calendar_date, data=filtered_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        # This method allows partial updates with the PATCH HTTP method
        return self.put(request, *args, **kwargs)

    def get_allowed_fields_by_role(self, role):
        """Returns a list of fields the user is allowed to update based on their role."""
        if role == 'account_manager':
            return ['client_approval']

        elif role == 'marketing_manager':
            return [
                'post_count', 'type', 'category', 'cta', 'strategy', 'resource',
                'internal_status', 'collaboration'
            ]

        elif role == 'content_writer':
            return ['tagline', 'caption', 'hashtags', 'e_hooks', 'creatives_text']  # Added 'creatives_text' here

        elif role == 'graphics_designer':
            return ['creatives']

        else:
            return []

#CALENDER DATA FOR CLIENT
class ClientCalendarByMonthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_id, month_name, *args, **kwargs):
        # Ensure the client exists
        client = get_object_or_404(models.Clients, id=client_id)

        # Retrieve the calendars for the specific client and month_name
        calendars = models.ClientCalendar.objects.filter(client=client, month_name__icontains=month_name)

        # If no calendars are found for the client in the given month, return a 404 response
        if not calendars.exists():
            return Response({"error": f"No calendar found for client {client.business_name} in the month {month_name}."}, status=status.HTTP_404_NOT_FOUND)

        # Get all the calendar dates related to the found calendars
        calendar_dates = models.ClientCalendarDate.objects.filter(calendar__in=calendars)

        # Serialize the result
        serializer = serializers.FilteredClientCalendarDateSerializer(calendar_dates, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)

# class ClientCalendarDateRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = serializers.ClientCalendarDateSerializer
#     lookup_field = 'calendar_id'  # Specify lookup_field to match your URL parameter

#     def get_queryset(self):
#         calendar_id = self.kwargs.get('calendar_id')
#         return models.ClientCalendarDate.objects.filter(calendar_id=calendar_id)

#     def put(self, request, *args, **kwargs):
#         # Retrieve the calendar date to be updated
#         calendar_date = self.get_object()

#         # Use partial=True to allow partial updates
#         serializer = self.get_serializer(calendar_date, data=request.data, partial=True)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, *args, **kwargs):
#         return self.put(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         # Delete the specific calendar date entry
#         calendar_date = self.get_object()
#         calendar_date.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

#CLIENT INVOICE
class ClientInvoicesListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.ClientInvoicesSerializer

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        return models.ClientInvoices.objects.filter(client_id=client_id)
    
    def post(self, request, *args, **kwargs):
        client_id = self.kwargs.get('client_id')
        client = get_object_or_404(models.Clients, id=client_id)

        # Create a new invoice and assign the client
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=client)  # Set the client from the URL
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientInvoicesRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.ClientInvoicesSerializer

    def get_queryset(self):
        # Retrieve the specific invoice related to a client
        client_id = self.kwargs.get('client_id')
        return models.ClientInvoices.objects.filter(client_id=client_id)

    def put(self, request, *args, **kwargs):
        # Retrieve the invoice to be updated
        invoice = self.get_object()

        # Allow partial updates to avoid overwriting all fields
        serializer = self.get_serializer(invoice, data=request.data, partial=True)

        if serializer.is_valid():
            # Save the updated invoice data
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        # Use PATCH method for partial updates
        return self.put(request, *args, **kwargs)

# TEAM
class TeamListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = models.Team.objects.all()
    serializer_class = serializers.TeamSerializer

    # Allowed roles in a team
    REQUIRED_ROLES = {'marketing_manager', 'marketing_assistant', 'content_writer', 'graphics_designer'}

    def create(self, request, *args, **kwargs):
        # Ensure only account managers can create teams
        if request.user.role != 'account_manager':
            return Response(
                {"error": "Only account managers can create teams."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Extract team data from the request
        team_data = request.data.get('team', {})
        
        # Add the current account manager as the creator of the team
        team_data['created_by'] = request.user.id  # Assuming 'created_by' is in the Team model

        # Create the team
        team_serializer = self.get_serializer(data=team_data)
        if team_serializer.is_valid():
            team = team_serializer.save()

            # Add members to the team
            members_data = request.data.get('members', [])
            roles_added = set()
            members_added = []

            for member_data in members_data:
                user_id = member_data.get('user_id')
                user = models.CustomUser.objects.get(id=user_id)

                # Check if the user's role is in the allowed roles
                if user.role not in self.REQUIRED_ROLES:
                    return Response(
                        {"error": f"Invalid role: {user.role}. Only {', '.join(self.REQUIRED_ROLES)} roles are allowed in the team."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                membership = models.TeamMembership.objects.create(team=team, user=user)
                roles_added.add(user.role)
                members_added.append({
                    'user_id': user.id,
                    'username': user.username,
                    'role': user.get_role_display()
                })

            # Check if the team is complete based on the required roles
            missing_roles = self.REQUIRED_ROLES - roles_added
            team_status = "complete" if not missing_roles else f"incomplete, missing roles: {', '.join(missing_roles)}"

            response_data = {
                'team': team_serializer.data,
                'members': members_added,
                'message': f"Team creation {team_status}."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(team_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request, *args, **kwargs):
        teams = self.get_queryset()
        team_data = []

        for team in teams:
            members_count = team.memberships.count()
            clients_count = team.clients.count()
            
            # Check if the team is complete
            team_roles = set(team.memberships.values_list('user__role', flat=True))
            missing_roles = self.REQUIRED_ROLES - team_roles
            team_status = "complete" if not missing_roles else f"incomplete, missing roles: {', '.join(missing_roles)}"

            team_data.append({
                'team_id': team.id,
                'name': team.name,
                'description': team.description,
                'members_count': members_count,
                'clients_count': clients_count,
                'status': team_status
            })

        return Response(team_data, status=status.HTTP_200_OK)

class TeamRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = models.Team.objects.all()
    serializer_class = serializers.TeamSerializer

    # Allowed roles in a team
    REQUIRED_ROLES = {'marketing_manager', 'marketing_assistant', 'content_writer', 'graphics_designer'}

    def retrieve(self, request, *args, **kwargs):
        team = self.get_object()
        members = team.memberships.all()
        member_data = []

        for membership in members:
            member_data.append({
                'membership_id': membership.id,  # Include membership ID for member-specific actions
                'user_id': membership.user.id,
                'username': membership.user.username,
                'role': membership.user.get_role_display()
            })

        response_data = {
            'team': self.get_serializer(team).data,
            'members': member_data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        # Update the team details using request.data
        team_serializer = self.get_serializer(instance, data=request.data['team'], partial=partial)
        if team_serializer.is_valid():
            team = team_serializer.save()

            # Update members if 'members' key is present in the request data
            members_data = request.data.get('members', [])
            if members_data:
                roles_added = set()
                members_added = []

                for member_data in members_data:
                    user_id = member_data.get('user_id')
                    user = models.CustomUser.objects.get(id=user_id)
                    
                    # Check if the user's role is in the allowed roles
                    if user.role not in self.REQUIRED_ROLES:
                        return Response(
                            {"error": f"Invalid role: {user.role}. Only {', '.join(self.REQUIRED_ROLES)} roles are allowed in the team."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Create or update the membership
                    membership, created = models.TeamMembership.objects.update_or_create(
                        team=team, user=user, defaults={}
                    )
                    roles_added.add(user.role)
                    members_added.append({
                        'membership_id': membership.id,
                        'user_id': user.id,
                        'username': user.username,
                        'role': user.get_role_display()
                    })

                # Check if the team is complete based on the required roles
                missing_roles = self.REQUIRED_ROLES - roles_added
                team_status = "complete" if not missing_roles else f"incomplete, missing roles: {', '.join(missing_roles)}"

                response_data = {
                    'team': team_serializer.data,
                    'members': members_added,
                    'status': team_status
                }
            else:
                response_data = {
                    'team': team_serializer.data,
                    'members': "No members were provided for update."
                }

            return Response(response_data, status=status.HTTP_200_OK)
        return Response(team_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        team.delete()
        return Response({"message": "Team deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def remove_member(self, request, *args, **kwargs):
        """Remove a specific member from the team."""
        team = self.get_object()
        member_id = request.data.get('membership_id')

        try:
            membership = models.TeamMembership.objects.get(id=member_id, team=team)
            membership.delete()
            return Response({"message": "Member removed successfully."}, status=status.HTTP_200_OK)
        except models.TeamMembership.DoesNotExist:
            return Response({"error": "Member not found in this team."}, status=status.HTTP_404_NOT_FOUND)

    def edit_member(self, request, *args, **kwargs):
        """Edit a specific member's role in the team."""
        team = self.get_object()
        member_id = request.data.get('membership_id')
        new_role = request.data.get('new_role')

        if new_role not in self.REQUIRED_ROLES:
            return Response(
                {"error": f"Invalid role: {new_role}. Only {', '.join(self.REQUIRED_ROLES)} roles are allowed in the team."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            membership = models.TeamMembership.objects.get(id=member_id, team=team)
            user = membership.user
            user.role = new_role
            user.save()
            return Response({
                "message": "Member role updated successfully.",
                "user_id": user.id,
                "username": user.username,
                "new_role": user.get_role_display()
            }, status=status.HTTP_200_OK)
        except models.TeamMembership.DoesNotExist:
            return Response({"error": "Member not found in this team."}, status=status.HTTP_404_NOT_FOUND)

class AssignClientToTeamView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    queryset = models.Clients.objects.all()
    serializer_class = serializers.AssignClientToTeamSerializer

    def update(self, request, *args, **kwargs):
        # Check if the logged-in user has the "marketing_director" role
        if request.user.role != 'marketing_director':
            return Response(
                {"error": "Only Marketing Director can assign a client to a team."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Proceed with team assignment if the user is a marketing director
        client = self.get_object()  # Get the client object based on the client ID (pk)
        team_id = request.data.get('team_id')

        # Validate the team_id
        if not team_id:
            return Response({"error": "Team ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            team = models.Team.objects.get(id=team_id)  # Fetch the team based on the team_id in the request data
        except models.Team.DoesNotExist:
            return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        # Assign the client to the team
        client.team = team
        client.save()

        serializer = self.get_serializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)

# MEETING 
class MeetingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = models.Meeting.objects.all()
    serializer_class = serializers.MeetingSerializer

    def perform_create(self, serializer):
        # Ensure only Account Managers can schedule meetings
        if self.request.user.role != 'account_manager':
            raise PermissionDenied("Only account managers can schedule meetings.")

        client_id = serializer.validated_data.get('client').id if serializer.validated_data.get('client') else None
        assignee_type = self.request.data.get('assignee_type')  # Expected to be "team" or "marketing_manager"

        # Check if client is provided
        if not client_id:
            raise ValidationError({"error": "Client is required."})

        client = get_object_or_404(models.Clients, id=client_id)

        # Filter based on the assignee type
        if assignee_type == 'team':
            if not client.team:
                raise ValidationError({"error": "No team is assigned to this client."})
            team = client.team
            serializer.save(scheduled_by=self.request.user, team=team)

        elif assignee_type == 'marketing_manager':
            if not client.team:
                raise ValidationError({"error": "No team is assigned to this client."})
            marketing_manager = client.team.memberships.filter(user__role='marketing_manager').first()
            if not marketing_manager:
                raise ValidationError({"error": "No marketing manager found for the client's assigned team."})
            serializer.save(scheduled_by=self.request.user, marketing_manager=marketing_manager.user)

        else:
            raise ValidationError({"error": "Invalid assignee type. Must be 'team' or 'marketing_manager'."})

        # Handle timezone conversion and UTC storage
        date = serializer.validated_data.get('date')
        time = serializer.validated_data.get('time')
        user_timezone_str = serializer.validated_data.get('timezone')

        user_timezone = pytz_timezone(user_timezone_str)
        local_datetime = user_timezone.localize(datetime.combine(date, time))
        utc_datetime = local_datetime.astimezone(pytz_timezone('UTC'))

        # Extract the date and time in UTC
        date_utc = utc_datetime.date()
        time_utc = utc_datetime.time()

        # Check for existing meetings at the same time
        existing_meeting = models.Meeting.objects.filter(date=date_utc, time=time_utc).first()

        if existing_meeting:
            new_datetime = datetime.combine(date_utc, existing_meeting.time) + timedelta(minutes=20)
            date_utc = new_datetime.date()
            time_utc = new_datetime.time()

        # Save the meeting, including the updated date and time in UTC
        serializer.save(scheduled_by=self.request.user, date=date_utc, time=time_utc, timezone=user_timezone_str)

    def create(self, request, *args, **kwargs):
        if request.user.role != 'account_manager':
            return Response({"error": "Only account managers can schedule meetings"}, status=status.HTTP_403_FORBIDDEN)

        return super().create(request, *args, **kwargs)

class MeetingRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = models.Meeting.objects.all()
    serializer_class = serializers.SpecificMeetingSerializer  

    def get_object(self):
        meeting_id = self.kwargs.get("pk")
        return get_object_or_404(models.Meeting, pk=meeting_id)

    def convert_to_local_timezone(self, date, time, timezone_str):
        """Helper method to convert UTC to the specified timezone."""
        meeting_timezone = pytz_timezone(timezone_str)
        meeting_datetime_utc = datetime.combine(date, time)
        meeting_datetime_utc = pytz_timezone('UTC').localize(meeting_datetime_utc)
        return meeting_datetime_utc.astimezone(meeting_timezone)

    def get(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(meeting)

        # Convert the meeting time from UTC to the original timezone
        meeting_datetime_local = self.convert_to_local_timezone(meeting.date, meeting.time, meeting.timezone)

        # Modify serializer data to return the date and time in the original time zone
        response_data = serializer.data
        response_data['date'] = meeting_datetime_local.strftime('%Y-%m-%d')
        response_data['time'] = meeting_datetime_local.strftime('%H:%M:%S')

        # Customizing the 'details' field based on the data
        response_data['details'] = [
            meeting.team.name if meeting.team else "No team assigned with this client",
            meeting.scheduled_by.role if meeting.scheduled_by else None,
            meeting.marketing_manager.role if meeting.marketing_manager else None
        ]
        
        # Filter out any 'None' values from the 'details' list
        response_data['details'] = [item for item in response_data['details'] if item is not None]

        return Response(response_data)

    def update(self, request, *args, **kwargs):
        meeting = self.get_object()  # Fetch the existing meeting instance

        # Allow partial updates by passing 'partial=True' to the serializer
        serializer = self.get_serializer(meeting, data=request.data, partial=True)

        if serializer.is_valid():
            # Get the existing date and time or use the provided values from the request
            new_date = serializer.validated_data.get('date', meeting.date)
            new_time = serializer.validated_data.get('time', meeting.time)

            # Handle potential time conflicts if any (this logic needs to be implemented based on your needs)
            new_datetime, rescheduled_message = self.handle_time_conflicts(new_date, new_time, meeting.pk)

            # Update only the fields that were provided in the request, leaving other fields unchanged
            if 'date' in serializer.validated_data:
                meeting.date = new_datetime.date()
            if 'time' in serializer.validated_data:
                meeting.time = new_datetime.time()

            if 'meeting_name' in serializer.validated_data:
                meeting.meeting_name = serializer.validated_data['meeting_name']
            if 'meeting_link' in serializer.validated_data:
                meeting.meeting_link = serializer.validated_data['meeting_link']
            if 'timezone' in serializer.validated_data:
                meeting.timezone = serializer.validated_data['timezone']
            if 'is_completed' in serializer.validated_data:
                meeting.is_completed = serializer.validated_data['is_completed']

            # Save the updated meeting instance
            meeting.save()

            # Prepare the response data
            response_data = {'meeting': serializer.data}
            if rescheduled_message:
                response_data['message'] = rescheduled_message

            return Response(response_data, status=status.HTTP_200_OK)

        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def handle_time_conflicts(self, date, time, meeting_id):
        """Helper method to handle time conflicts and reschedule if needed."""
        existing_meeting = models.Meeting.objects.filter(date=date, time=time).exclude(pk=meeting_id).first()
        
        if existing_meeting:
            # Adjust the time to 20 minutes after the existing meeting
            new_datetime = datetime.combine(existing_meeting.date, existing_meeting.time) + timedelta(minutes=20)
            rescheduled_message = f"Meeting has been rescheduled to {new_datetime.strftime('%Y-%m-%d %H:%M')}."
        else:
            new_datetime = datetime.combine(date, time)
            rescheduled_message = None

        return new_datetime, rescheduled_message

    def delete(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting.delete()
        return Response({"message": "Meeting deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# TASK  
class CompleteTaskView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request, task_id):
        task = get_object_or_404(models.Task, id=task_id)

        if request.user != task.assigned_to:
            return Response({"error": "You are not authorized to complete this task."}, status=status.HTTP_403_FORBIDDEN)

        if not task.client.team:
            return Response({"error": f"Client '{task.client.business_name}' is not assigned to a team."}, status=status.HTTP_400_BAD_REQUEST)

        if task.is_completed:
            return self._handle_completed_task(task)

        # Perform task-specific checks (including meeting check for 'schedule_meeting')
        task_check_result = self._perform_task_checks(task)
        if not task_check_result["success"]:
            return Response({"error": task_check_result["message"]}, status=status.HTTP_400_BAD_REQUEST)

        # Mark the task as completed and proceed
        mark_task_as_completed(task)
        self._handle_client_status_update(task)

        return Response({"message": "Task completed successfully."}, status=status.HTTP_200_OK)

    def _perform_task_checks(self, task):
        """Perform task-specific checks before marking a task as completed."""
        
        if task.task_type == 'create_proposal' and not task.client.proposal_pdf:
            return {"success": False, "message": f"Proposal not uploaded for client: {task.client.business_name}."}

        if task.task_type == 'approve_proposal':
            return self._check_proposal_approval_status(task)

        if task.task_type == 'schedule_meeting':
            return self._check_meeting_created(task)
         
        if task.task_type == 'assigned_plan_to_client':
            # Check if a plan has been assigned to the client
            client_plan_exists = task.client.client_plans.exists()  # Checks if any ClientsPlan exists for the client
            if not client_plan_exists:
                return {"success": False, "message": f"No plan is assigned to client '{task.client.business_name}'. Please assign a plan before completing this task."}

        if task.task_type == 'create_strategy':
            return self._check_calendar_resources(task)
        
        if task.task_type == 'content_writing':
            return self._check_content_writing_task(task)
        
        if task.task_type == 'approve_content_by_marketing_manager':
            return self._check_approve_content_by_marketing_manager_task(task)
        
        if task.task_type == 'approve_content_by_account_manager':
            return self._check_approve_content_by_account_manager_task(task)
        
        if task.task_type == 'approve_creatives_by_marketing_manager':
            return self._check_approve_creatives_by_marketing_manager_task(task)
        
        if task.task_type == 'approve_creatives_by_account_manager':
            return self._check_approve_creatives_by_account_manager_task(task)
        
        if task.task_type == 'creatives_design':
            return self._check_creatives_design_task(task)

        return {"success": True}


    # def _handle_completed_task(self, task):
    def _handle_completed_task(self, task):
        next_step, next_user = get_next_step_and_user(task)

        if next_step and next_user:
            print(f"Creating next task: {next_step} assigned to {next_user.username} for client {task.client.business_name}")
            create_task(task.client, next_step, next_user)
            return Response({"message": f"Next task '{next_step}' created successfully."}, status=status.HTTP_200_OK)

        print("No further steps found. Workflow complete or misconfigured.")
        return Response({"message": "Task completed, but no further steps available."}, status=status.HTTP_400_BAD_REQUEST)

        # next_step, next_user = get_next_step_and_user(task)
        # if next_step and next_user:
        #     create_task(task.client, next_step, next_user)
        #     return Response({"message": "Next task created as previous task was already completed."}, status=status.HTTP_200_OK)
        # return Response({"message": "This task has already been completed and no next step is available."}, status=status.HTTP_400_BAD_REQUEST)

    def _check_proposal_approval_status(self, task):
        approval_status = task.client.proposal_approval_status
        if approval_status == 'declined':
            return {"success": False, "message": f"Proposal for client '{task.client.business_name}' was declined. Task cannot be completed."}
        
        if approval_status == 'changes_required':
            mark_task_as_completed(task, reassign_to_marketing=True)
            return {"success": False, "message": f"Proposal for client '{task.client.business_name}' requires changes. Task has been sent back to the marketing manager."}

        if not approval_status or approval_status != 'approved':
            return {"success": False, "message": f"Proposal for client '{task.client.business_name}' is not approved yet."}

        return {"success": True}

    def _handle_client_status_update(self, task):
        """Handles the client status update after task completion, if needed."""
        if task.task_type == 'payment_confirmation':
            print(f"Updating client status to 'Completed' for client: {task.client.business_name}")
            update_client_status(task.client, 'Completed')

    def _check_meeting_created(self, task):
        """Checks if a meeting has been created for the client in the current month before completing 'schedule_meeting' or 'schedule_brief_meeting' task."""
        client = task.client

        # Check the current date
        current_date = datetime.now().date()
        current_year = current_date.year
        current_month = current_date.month

        print(f"Checking if a meeting exists for client '{client.business_name}' in {current_month}/{current_year}.")

        # Query the meetings based on the current year and month
        meetings = models.Meeting.objects.filter(
            client=client,
            date__year=current_year,
            date__month=current_month
        )

        if not meetings.exists():
            print(f"No meeting found for client '{client.business_name}' in {current_month}/{current_year}.")
            return {"success": False, "message": f"No meeting has been scheduled for client '{client.business_name}' in the current month. Please schedule a meeting before completing this task."}

        # Log the meetings found
        for meeting in meetings:
            print(f"Meeting found: {meeting.meeting_name}, Date: {meeting.date}, Time: {meeting.time} for client '{client.business_name}'.")

        return {"success": True}

    def _check_calendar_resources(self, task):
        """
        Check if the 'strategy_completed' field in the ClientCalendar table is set to True for the client's calendar.
        """
        client = task.client

        try:
            # Retrieve the client's calendar
            client_calendar = models.ClientCalendar.objects.get(client=client)

            # Check if the strategy is completed
            if not client_calendar.strategy_completed:
                return {"success": False, "message": f"The strategy for client '{client.business_name}' is not marked as completed. Please complete the strategy before proceeding with this task."}

            # Strategy is completed
            return {"success": True}
        except models.ClientCalendar.DoesNotExist:
            # If no calendar exists for the client
            return {"success": False, "message": f"No calendar found for client '{client.business_name}'. Please create a calendar and complete the strategy before proceeding with this task."}

    def _check_content_writing_task(self, task):
        """
        Check if the 'content_writing_completed' field in the ClientCalender table is set to True for the client's calender.
        """
        client = task.client
        try: 
            client_calender = models.ClientCalendar.objects.get(client=client)
            
            if not client_calender.content_completed:
                return {"success": False, "message": f"The content for client '{client.business_name}' is not marked as completed. Please complete the strategy before proceeding with this task."}

            # content is completed
            return {"success": True}
        except models.ClientCalendar.DoesNotExist:
            # If no calendar exists for the client
            return {"success": False, "message": f"No calendar found for client '{client.business_name}'. Please create a calendar and complete the strategy before proceeding with this task."}

    def _check_approve_content_by_marketing_manager_task(self, task):
        """
        Check if the 'content_writing_completed' field in the ClientCalender table is set to True for the client's calender.
        """
        client = task.client
        try: 
            client_calender = models.ClientCalendar.objects.get(client=client)
            
            if not client_calender.mm_content_completed:
                return {"success": False, "message": f"The content approval for client '{client.business_name}' by marketing manager is not marked as completed. Please complete the content approval before proceeding with this task."}

            # content is completed
            return {"success": True}
        except models.ClientCalendar.DoesNotExist:
            # If no calendar exists for the client
            return {"success": False, "message": f"No calendar found for client '{client.business_name}'. Please create a calendar and complete the stracontent approval before proceeding with this task."}

    def _check_approve_content_by_account_manager_task(self, task):
        """
        Check if the 'content_writing_completed' field in the ClientCalender table is set to True for the client's calender.
        """
        client = task.client
        try: 
            client_calender = models.ClientCalendar.objects.get(client=client)
            
            if not client_calender.acc_content_completed:
                return {"success": False, "message": f"The content approval for client '{client.business_name}' by account manager is not marked as completed. Please complete the content approval before proceeding with this task."}

            # content is completed
            return {"success": True}
        except models.ClientCalendar.DoesNotExist:
            # If no calendar exists for the client
            return {"success": False, "message": f"No calendar found for client '{client.business_name}'. Please create a calendar and complete the content approval before proceeding with this task."}

    def _check_approve_creatives_by_marketing_manager_task(self, task):
        """
        Check if the 'content_writing_completed' field in the ClientCalender table is set to True for the client's calender.
        """
        client = task.client
        try: 
            client_calender = models.ClientCalendar.objects.get(client=client)
            
            if not client_calender.mm_creative_completed:
                return {"success": False, "message": f"The creatives approval for client '{client.business_name}' by marketing manager is not marked as completed. Please complete the content approval before proceeding with this task."}

            # content is completed
            return {"success": True}
        except models.ClientCalendar.DoesNotExist:
            # If no calendar exists for the client
            return {"success": False, "message": f"No calendar found for client '{client.business_name}'. Please create a calendar and complete the stracontent approval before proceeding with this task."}

    def _check_approve_creatives_by_account_manager_task(self, task):
        """
        Check if the 'content_writing_completed' field in the ClientCalender table is set to True for the client's calender.
        """
        client = task.client
        try: 
            client_calender = models.ClientCalendar.objects.get(client=client)
            
            if not client_calender.acc_creative_completed:
                return {"success": False, "message": f"The creative approval for client '{client.business_name}' by account manager is not marked as completed. Please complete the content approval before proceeding with this task."}

            # content is completed
            return {"success": True}
        except models.ClientCalendar.DoesNotExist:
            # If no calendar exists for the client
            return {"success": False, "message": f"No calendar found for client '{client.business_name}'. Please create a calendar and complete the creative approval before proceeding with this task."}

    def _check_creatives_design_task(self, task):
        """
        Check if the 'content_writing_completed' field in the ClientCalender table is set to True for the client's calender.
        """
        client = task.client
        try: 
            client_calender = models.ClientCalendar.objects.get(client=client)
            
            if not client_calender.creatives_completed:
                return {"success": False, "message": f"The creatives for client '{client.business_name}'is not marked as completed. Please complete the creatives before proceeding with this task."}

            # content is completed
            return {"success": True}
        except models.ClientCalendar.DoesNotExist:
            # If no calendar exists for the client
            return {"success": False, "message": f"No calendar found for client '{client.business_name}'. Please create a calendar and complete the creative before proceeding with this task."}


class TaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TaskSerializer

    def get_queryset(self):
        # Ensure the user is authenticated before filtering tasks
        if self.request.user.is_authenticated:
            return models.Task.objects.filter(assigned_to=self.request.user)
        else:
            return models.Task.objects.none()  # Return an empty queryset for anonymous users

class UserAssignedTaskListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.MyTaskSerializer

    def get_queryset(self):
        # Fetch tasks assigned to the currently authenticated user and filter by completion status
        return models.Task.objects.filter(assigned_to=self.request.user, is_completed=False).select_related('client')

class UpdateClientWorkflowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, client_id):
        client = get_object_or_404(models.Clients, id=client_id)
        task_type = request.data.get('task_type')
        assigned_to_id = request.data.get('assigned_to')

        if not task_type or not assigned_to_id:
            return Response({"error": "task_type and assigned_to are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Update or create the task for the client
        task, created = models.Task.objects.update_or_create(
            client=client,
            task_type=task_type,
            defaults={'assigned_to_id': assigned_to_id, 'is_completed': False}
        )

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class UploadProposalView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, client_id, *args, **kwargs):
        client = get_object_or_404(models.Clients, id=client_id)
        serializer = serializers.ClientProposalSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, client_id, *args, **kwargs):
        client = get_object_or_404(models.Clients, id=client_id)
        serializer = serializers.ClientProposalSerializer(client, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, client_id, *args, **kwargs):
        client = get_object_or_404(models.Clients, id=client_id)
        
        # Delete the proposal file
        if client.proposal_pdf:
            client.proposal_pdf.delete()  # Deletes the file from storage
            client.proposal_pdf = None
            client.save()
            return Response({"message": "Proposal PDF deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "No proposal PDF found to delete."}, status=status.HTTP_404_NOT_FOUND)

#PLANS
class PlanView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Plans.objects.all()
    serializer_class = serializers.PlanSerializer

    # List all plans or create a new plan
    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            return self.retrieve(request, *args, **kwargs)  # Retrieve a specific plan by ID
        return self.list(request, *args, **kwargs)  # List all plans

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Create the new plan
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # Update a plan
    def put(self, request, *args, **kwargs):
        # Retrieve the plan to be updated
        plan = self.get_object()
        data = request.data

        # Merge the pricing_attributes field
        if 'pricing_attributes' in data:
            current_pricing_attributes = plan.pricing_attributes or {}
            current_pricing_attributes.update(data.get('pricing_attributes', {}))
            data['pricing_attributes'] = current_pricing_attributes

        # Merge the standard_attributes field
        if 'standard_attributes' in data:
            current_standard_attributes = plan.standard_attributes or {}
            current_standard_attributes.update(data.get('standard_attributes', {}))
            data['standard_attributes'] = current_standard_attributes

        # Merge the advanced_attributes field
        if 'advanced_attributes' in data:
            current_advanced_attributes = plan.advanced_attributes or {}
            current_advanced_attributes.update(data.get('advanced_attributes', {}))
            data['advanced_attributes'] = current_advanced_attributes

        # Merge the pricing_platforms field
        if 'pricing_platforms' in data:
            current_pricing_platforms = plan.pricing_platforms or {}
            current_pricing_platforms.update(data.get('pricing_platforms', {}))
            data['pricing_platforms'] = current_pricing_platforms

        # Pass the merged data to the serializer for validation
        serializer = self.get_serializer(plan, data=data, partial=True)  # Allow partial updates

        if serializer.is_valid():
            # Save the updated plan
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Handle the deletion of a plan
    def delete(self, request, *args, **kwargs):
        plan = get_object_or_404(models.Plans, pk=kwargs['pk'])
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
      
class PlanAssignView(generics.UpdateAPIView):
    permission_classes = [AllowAny]
    queryset = models.Plans.objects.all()
    serializer_class = serializers.PlanAssignSerializer

    def update(self, request, *args, **kwargs):
        plan = self.get_object()
        serializer = self.get_serializer(plan, data=request.data, partial=True)
        
        if serializer.is_valid():
            account_manager_id = serializer.validated_data.get('account_manager_id')

            # Check if the account manager already has an assigned plan
            if account_manager_id:
                existing_plan = models.Plans.objects.filter(assigned_account_managers=account_manager_id).exclude(id=plan.id).first()
                
                if existing_plan:
                    return Response(
                        {"detail": "This account manager is already assigned to another plan."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Save the updated plan with assigned account managers
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnassignedAccountManagerSearchView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Get data from the request body
        agency_name = request.data.get('agency_name', None)
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        role = request.data.get('role', 'account_manager')  # Default to 'account_manager' if role is not provided

        # Build the query based on provided parameters
        query = Q(role=role)
        
        if agency_name:
            query &= Q(agency_name__icontains=agency_name)
        
        if first_name:
            query &= Q(first_name__icontains=first_name)

        if last_name:
            query &= Q(last_name__icontains=last_name)

        # Exclude account managers (or users with any specified role) already assigned to any plan
        query &= Q(assigned_plans__isnull=True)

        # Search for users that match the criteria and are not assigned to any plan
        account_managers = models.CustomUser.objects.filter(query)

        # Serialize the results
        serializer = serializers.UserSerializer(account_managers, many=True)
        
        # Return the response with the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)

class AssignedAccountManagerSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Get query parameters for searching
        plan_id = request.query_params.get('plan_id', None)  # Plan ID to search for assigned account managers

        if not plan_id:
            return Response({"error": "Plan ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the plan instance
        plan = get_object_or_404(models.Plans, id=plan_id)

        # Retrieve all account managers assigned to the specific plan using the related name "assigned_plans"
        assigned_account_managers = models.CustomUser.objects.filter(assigned_plans=plan)

        # Serialize the results
        serializer = serializers.UserSerializer(assigned_account_managers, many=True)
        
        # Return the response with the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)

# class AssignedPlansForAccountManagerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        account_manager_id = request.query_params.get('account_manager_id', None)

        if not account_manager_id:
            return Response({"error": "Account Manager ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the account manager
        account_manager = get_object_or_404(models.CustomUser, id=account_manager_id)

        # Retrieve assigned plans directly via the reverse relation
        assigned_plans = account_manager.assigned_plans.all()

        # Debugging output to verify the query result
        print(f"Assigned Plans for Account Manager {account_manager_id}: {[plan.plan_name for plan in assigned_plans]}")

        # Serialize the results
        serializer = serializers.PlanSerializer(assigned_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AssignedPlansForAccountManagerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, client_id, *args, **kwargs):
        # Retrieve the client instance based on the client_id from the URL
        client = get_object_or_404(models.Clients, id=client_id)

        # Retrieve the Account Manager related to the client
        account_manager = client.account_manager  # Assuming a ForeignKey relation exists in Client model

        # Validate if Account Manager is found
        if not account_manager:
            return Response({"error": "No Account Manager associated with this Client ID."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve assigned plans for the Account Manager
        assigned_plans = account_manager.assigned_plans.all()

        # Debugging: Log the plans to verify
        print(f"Assigned Plans for Client {client_id} (Account Manager {account_manager.id}): {[plan.plan_name for plan in assigned_plans]}")

        # Serialize the assigned plans
        serializer = serializers.PlanSerializer(assigned_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class RemoveAccountManagerFromPlanView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Get the plan ID and account manager ID from the request data
        plan_id = request.data.get('plan_id')
        account_manager_id = request.data.get('account_manager_id')

        # Ensure both plan ID and account manager ID are provided
        if not plan_id or not account_manager_id:
            return Response({"error": "Both plan_id and account_manager_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the plan and account manager instances
        plan = get_object_or_404(models.Plans, id=plan_id)
        account_manager = get_object_or_404(models.CustomUser, id=account_manager_id, role='account_manager')

        # Check if the account manager is assigned to the plan
        if account_manager in plan.account_managers.all():
            # Remove the account manager from the plan
            plan.account_managers.remove(account_manager)
            return Response({"message": f"Account Manager '{account_manager.username}' removed from Plan '{plan.plan_name}'."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": f"Account Manager '{account_manager.username}' is not assigned to Plan '{plan.plan_name}'."}, status=status.HTTP_400_BAD_REQUEST)

# CLIENT PLAN 
class ClientPlanListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.ClientPlanSerializer

    def get_queryset(self):
        # Retrieve all plans related to a specific client
        client_id = self.kwargs.get('client_id')
        return models.ClientsPlan.objects.filter(client_id=client_id)

    def post(self, request, *args, **kwargs):
        # Get the client ID from the URL parameters
        client_id = self.kwargs.get('client_id')
        client = get_object_or_404(models.Clients, id=client_id)

        # Check if the client already has a plan
        if models.ClientsPlan.objects.filter(client=client).exists():
            # If a plan already exists for the client, return an error response
            return Response({"error": "Client already has an existing plan."}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed to create the new plan
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the plan with the associated client
            serializer.save(client=client)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientPlanRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.ClientPlanSerializer
    queryset = models.ClientsPlan.objects.all()

    def get_object(self):
        # Get the specific plan by client ID and plan ID
        client_id = self.kwargs.get('client_id')
        plan_id = self.kwargs.get('plan_id')
        return get_object_or_404(models.ClientsPlan, client_id=client_id, id=plan_id)

    def put(self, request, *args, **kwargs):
        # Retrieve the plan to be updated
        plan = self.get_object()                                   

        # Allow partial updates
        serializer = self.get_serializer(plan, data=request.data, partial=True)
        
        if serializer.is_valid():
            # For JSON fields like 'attributes', 'platforms', 'add_ons', handle the merging of existing and new data
            updated_data = serializer.validated_data

            # Merge attributes
            if 'attributes' in updated_data:
                current_attributes = plan.attributes or {}
                current_attributes.update(updated_data['attributes'])
                updated_data['attributes'] = current_attributes

            # Merge platforms
            if 'platforms' in updated_data:
                current_platforms = plan.platforms or {}
                current_platforms.update(updated_data['platforms'])
                updated_data['platforms'] = current_platforms

            # Merge add_ons
            if 'add_ons' in updated_data:
                current_add_ons = plan.add_ons or {}
                current_add_ons.update(updated_data['add_ons'])
                updated_data['add_ons'] = current_add_ons

            # Save the updated plan data
            serializer.save(**updated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        # Retrieve the plan to be deleted
        plan = self.get_object()
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ThreadMessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ClientMessageThreadSerializer

    def get_queryset(self):
        # Allow anyone to view messages in the thread
        client_id = self.kwargs['client_id']
        client = get_object_or_404(models.Clients, id=client_id)
        return models.ClientMessageThread.objects.filter(client=client)

    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        client = get_object_or_404(models.Clients, id=client_id)
        
        # Check if the user is a member of the client's team
        if not client.team.memberships.filter(user=self.request.user).exists():
            raise PermissionDenied("You do not have permission to send messages in this thread.")
        
        # If user is authorized, save the message
        serializer.save(client=client, sender=self.request.user)

class CreateNoteView(generics.CreateAPIView):
    """
    API view to create a new note.
    """
    queryset = models.Notes.objects.all()
    serializer_class = serializers.NotesSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Automatically set the sender as the currently logged-in user.
        """
        serializer.save(sender=self.request.user)
        
# List and Create Strategy
class StrategyListCreateView(generics.GenericAPIView):
    queryset = models.Strategy.objects.all()
    serializer_class = serializers.StrategySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """List all strategies."""
        strategies = self.get_queryset()
        serializer = self.get_serializer(strategies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create a new strategy."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
# Edit and Delete Strategy
class StrategyEditDeleteView(generics.GenericAPIView):
    queryset = models.Strategy.objects.all()
    serializer_class = serializers.StrategySerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        """Edit a strategy."""
        strategy = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(strategy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """Delete a strategy."""
        strategy = get_object_or_404(self.get_queryset(), pk=pk)
        strategy.delete()
        return Response({"message": "Strategy deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
                 
# Assign strategy to a client
class StrategyAssignView(generics.UpdateAPIView):
    queryset = models.Strategy.objects.all()
    serializer_class = serializers.StrategySerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        strategy = self.get_object()
        serializer = self.get_serializer(strategy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    