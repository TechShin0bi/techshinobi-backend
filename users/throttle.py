from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import Throttled
from django.core.cache import cache
from rest_framework import status
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class LoginThrottle(AnonRateThrottle):
    scope = 'login_attempts'
    
    def get_rate(self):
        # Default rate (5 attempts per minute)
        return '5/minute'
    
    def get_cache_key(self, request, view):
        # Use IP + username for cache key to track per-user attempts
        username = request.data.get('username', '').lower()
        return f'login_attempts_{self.get_ident(request)}_{username}'
    
    def allow_request(self, request, view):
        cache_key = self.get_cache_key(request, view)
        now = timezone.now()
        
        # Get or initialize attempt data
        attempt_data = cache.get(cache_key, {
            'count': 0,
            'last_attempt': None,
            'next_attempt_time': None,
            'current_delay': 0
        })
        
        # If we have a next attempt time and it's in the future
        if attempt_data['next_attempt_time'] and now < attempt_data['next_attempt_time']:
            time_left = (attempt_data['next_attempt_time'] - now).total_seconds()
            time_left_int = int(time_left)
            
            # Format time left as a human-readable string with translations
            hours = time_left_int // 3600
            minutes = (time_left_int % 3600) // 60
            seconds = time_left_int % 60
            
            time_parts = []
            if hours > 0:
                time_parts.append(_('%(count)d hour') % {'count': hours} if hours == 1 else _('%(count)d hours') % {'count': hours})
            if minutes > 0:
                time_parts.append(_('%(count)d minute') % {'count': minutes} if minutes == 1 else _('%(count)d minutes') % {'count': minutes})
            if seconds > 0 or not time_parts:
                time_parts.append(_('%(count)d second') % {'count': seconds} if seconds == 1 else _('%(count)d seconds') % {'count': seconds})
                
            time_str = ', '.join(time_parts)
            
            raise Throttled(
                detail={
                    'error': _('Too many login attempts. Please try again in %(time_str)s.') % {'time_str': time_str},
                    'time_left_seconds': time_left_int,
                    'time_left': {
                        'hours': hours,
                        'minutes': minutes,
                        'seconds': seconds
                    },
                    'status': 'error',
                    'code': status.HTTP_429_TOO_MANY_REQUESTS
                }
            )
        
        # Reset counter if last attempt was more than 8 hours ago
        if attempt_data['last_attempt'] and (now - attempt_data['last_attempt']) > timedelta(hours=8):
            attempt_data = {
                'count': 0,
                'last_attempt': None,
                'next_attempt_time': None,
                'current_delay': 0
            }
        
        # Increment attempt count
        attempt_data['count'] += 1
        attempt_data['last_attempt'] = now
        
        # Set delays based on number of attempts
        if attempt_data['count'] > 5:
            if attempt_data['count'] <= 7:  # 6th and 7th attempt (2 more attempts)
                attempt_data['current_delay'] = 30  # 30 seconds
            elif attempt_data['count'] == 8:  # 8th attempt
                attempt_data['current_delay'] = 3600  # 1 hour
            else:  # 9th+ attempt
                attempt_data['current_delay'] = 28800  # 8 hours
                
            # Set next attempt time
            next_attempt = now + timedelta(seconds=attempt_data['current_delay'])
            attempt_data['next_attempt_time'] = next_attempt
            time_left = attempt_data['current_delay']
            
            # Format time left as a human-readable string with translations
            hours = time_left // 3600
            minutes = (time_left % 3600) // 60
            seconds = time_left % 60
            
            time_parts = []
            if hours > 0:
                time_parts.append(_('%(count)d hour') % {'count': hours} if hours == 1 else _('%(count)d hours') % {'count': hours})
            if minutes > 0:
                time_parts.append(_('%(count)d minute') % {'count': minutes} if minutes == 1 else _('%(count)d minutes') % {'count': minutes})
            if seconds > 0 or not time_parts:
                time_parts.append(_('%(count)d second') % {'count': seconds} if seconds == 1 else _('%(count)d seconds') % {'count': seconds})
                
            time_str = ', '.join(time_parts)
            
            # Save the updated attempt data
            cache.set(cache_key, attempt_data, timeout=60*60*9)  # 9 hours timeout
            
            raise Throttled(
                detail={
                    'error': _('Too many login attempts. Please try again in %(time_str)s.') % {'time_str': time_str},
                    'time_left_seconds': time_left,
                    'time_left': {
                        'hours': hours,
                        'minutes': minutes,
                        'seconds': seconds
                    },
                    'attempts_remaining': 2 if attempt_data['count'] <= 7 else 0,
                    'status': 'error',
                    'code': status.HTTP_429_TOO_MANY_REQUESTS
                }
            )
        
        # Save the attempt data
        cache.set(cache_key, attempt_data, timeout=60*60*9)  # 9 hours timeout
        return True