from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from users.serializers import LoginSerializer ,UserSerializer
import logging
from rest_framework import serializers
# from user.throttle import LoginThrottle
from django_user_agents.utils import get_user_agent
from django.conf import settings


logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    View for user authentication.
    Handles login requests and returns JWT tokens.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Initialize and validate the serializer
            serializer = LoginSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            # Authenticate user and get tokens
            auth_data = serializer.authenticate_user()
            user = auth_data["user"]
            tokens = auth_data["tokens"]
            user_type = auth_data["user_type"]

            # Log successful login
            logger.info(
                f"Successful login - "
                f"Username: {user.username}, "
                f"Type: {user_type}, "
                f"IP: {self._get_client_ip(request)}"
            )

            # Prepare response with serializable data
            response_data = {
                "access": tokens["access"],  # Already a string
                "refresh": tokens["refresh"],  # Already a string
                "user": UserSerializer(instance=user).data,
                "token_expiry": tokens[
                    "access_expiration"
                ],  # Already an ISO format string
            }

            # Create response
            response = Response(response_data)

            # Set auth cookie if needed
            self._set_auth_cookie(response, tokens["access"], tokens["refresh"])

            return response

        except serializers.ValidationError as e:
            # Handle validation errors from the serializer
            error_message = self._extract_error_message(e)
            return Response(
                {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log unexpected errors
            logger.error(
                f"Login error: {str(e)}",
                exc_info=True,
                extra={
                    "username": request.data.get("username"),
                    "ip": self._get_client_ip(request),
                },
            )
            return Response(
                {
                    "error": _(
                        "An error occurred during authentication. Please try again later."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _set_auth_cookie(self, response, access_token, refresh_token):
        """Set both access and refresh cookies."""
        response.set_cookie(
            key='auth_token',
            value=access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='None',
            path='/'
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='None',
            path='/'
        )


    def _extract_error_message(self, exception):
        """Extract error message from validation exception."""
        if hasattr(exception, "detail"):
            if isinstance(exception.detail, dict):
                if "non_field_errors" in exception.detail:
                    return str(exception.detail["non_field_errors"][0])
                return str(exception.detail)
            if hasattr(exception.detail, "__iter__"):
                return str(exception.detail[0])
        return str(exception)

    def _get_client_ip(self, request):
        """
        Get the client's IP address using django_user_agents.
        Handles various proxy and load balancer scenarios.
        """
        # Get the user agent object
        user_agent = get_user_agent(request)

        # Try to get the IP from X-Forwarded-For header first
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # X-Forwarded-For can be a comma-separated list of IPs
            # The client's IP is the first one in the list
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            # Fall back to REMOTE_ADDR if X-Forwarded-For is not present
            ip = request.META.get("REMOTE_ADDR")

        # Log additional user agent information if available
        if user_agent and hasattr(user_agent, "device") and hasattr(user_agent, "os"):
            logger.debug(
                f"Client IP: {ip}, "
                f"Device: {getattr(user_agent.device, 'brand', 'Unknown')} {getattr(user_agent.device, 'model', 'Unknown')}, "
                f"OS: {getattr(user_agent.os, 'family', 'Unknown')} {getattr(user_agent.os, 'version_string', '')}, "
                f"Browser: {getattr(user_agent.browser, 'family', 'Unknown')} {getattr(user_agent.browser, 'version_string', '')}"
            )

        return ip if ip else "0.0.0.0"  # Return a default IP if none found