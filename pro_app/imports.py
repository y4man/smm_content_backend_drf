
# Standard library imports
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
from django.utils.timezone import make_aware, utc

# Django imports
from django.core.mail import send_mail, get_connection
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.core.exceptions import PermissionDenied


# Third-party imports (rest_framework)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework import generics  
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser


# Third-party imports (rest_framework) JWT
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

# IMPORT INTERNAL FILE 
from .utils import create_task, update_client_workflow, mark_task_as_completed, get_next_step_and_user,update_client_status




