# from rest_framework.authentication import BaseAuthentication
# from rest_framework_simplejwt.tokens import AccessToken
# from rest_framework.exceptions import AuthenticationFailed
# from django.conf import settings
# from .models import CustomUser

# class CookieJWTAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         # Get the access token from the cookies
#         access_token = request.COOKIES.get('access_token')

#         if not access_token:
#             return None  # No authentication information was provided

#         try:
#             # Decode the access token
#             token = AccessToken(access_token)
#             user_id = token['user_id']

#             # Retrieve the user associated with the token
#             user = CustomUser.objects.get(id=user_id)

#             if not user.is_active:
#                 raise AuthenticationFailed('User is inactive')

#             # If successful, return a tuple of (user, token)
#             return (user, None)
#         except Exception as e:
#             raise AuthenticationFailed(f'Invalid token: {str(e)}')



# pro_app/authenticate.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions

# def enforce_csrf(request):
#     """
#     Enforce CSRF validation.
#     """
#     check = CSRFCheck()
#     check.process_request(request)
#     reason = check.process_view(request, None, (), {})
#     if reason:
#         raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')

# class CustomJWTAuthentication(JWTAuthentication):
#     """Custom authentication class"""
#     def authenticate(self, request):
#         # Try to get the token from the header first
#         header = self.get_header(request)
        
#         if header is None:
#             # If header is not found, try to get the token from the cookies
#             raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
#         else:
#             raw_token = self.get_raw_token(header)

#         # If no token is found, return None
#         if raw_token is None:
#             return None

#         # Validate the token
#         validated_token = self.get_validated_token(raw_token)

#         # Enforce CSRF check
#         enforce_csrf(request)

#         # Return the user and the token
#         return self.get_user(validated_token), validated_token


def enforce_csrf(request):
    """
    Enforce CSRF validation.
    """
    check = CSRFCheck()
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)

class CustomJWTAuthentication(JWTAuthentication):
    """Custom authentication class to extract JWT from cookies"""
    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            # Extract token from cookies
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        # Enforce CSRF protection
        enforce_csrf(request)

        return self.get_user(validated_token), validated_token
