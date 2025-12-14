from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import logout
import logging
from django.conf import settings

    
logger = logging.getLogger(__name__)

class LogoutView(APIView):
    """
    View to handle user logout by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            username = request.user.username
            # refresh_token = request.COOKIES.get('refresh_token')
            # if not refresh_token:
            #     return Response(
            #         {'error': 'Refresh token is required'},
            #         status=status.HTTP_400_BAD_REQUEST
            #     )

            # # Blacklist the refresh token
            # token = RefreshToken(refresh_token)
            # token.blacklist()
            logout(request)
            # Create response with success message
            response = Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_205_RESET_CONTENT
            )
            
            # Clear both auth and refresh tokens with same settings as when they were set
            for cookie_name in ['auth_token', 'refresh_token']:
                response.delete_cookie(
                    key=cookie_name,
                    path='/',
                    samesite='Lax',
                )
            
            # Log the logout
            logger.info(f"User {request.user.username} logged out successfully, ")
            print(f"User {username} logged out successfully, ")
            return response
            
        except TokenError as e:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            
            logger.error(f"Logout error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An error occurred during logout'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutAllView(APIView):
    """
    View to log user out from all devices by blacklisting all refresh tokens.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            tokens = OutstandingToken.objects.filter(user_id=request.user.id)
            for token in tokens:
                try:
                    refresh_token = str(token)
                    RefreshToken(refresh_token).blacklist()
                except TokenError:
                    pass  # Token is already blacklisted or invalid
            
            # Log the logout all
            logger.info(f"User {request.user.username} logged out from all devices")
            
            return Response(
                {'message': 'Successfully logged out from all devices'},
                status=status.HTTP_205_RESET_CONTENT
            )
            
        except Exception as e:
            logger.error(f"Logout all error: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An error occurred during logout from all devices'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )