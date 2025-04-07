from .models import FollowRequest

from django.db.models import Q
from .models import FollowRequest, Message

def navbar_counts(request):
    if request.user.is_authenticated:
        received_followers = FollowRequest.objects.filter(to_user=request.user, status='accepted').count()
        sent_followers = FollowRequest.objects.filter(from_user=request.user, status='accepted').count()

        return {
            'message_count': Message.objects.filter(receiver=request.user, is_read=False).count(),  # Count unread messages
            'request_count': FollowRequest.objects.filter(to_user=request.user, status='pending').count(),
            'followers_count': received_followers + sent_followers  # Count both sides
        }
    return {}
  # If user is not logged in, return empty context

from django.contrib import messages
from django.db.models import Q
from .models import Message

from django.db.models import Q
from .models import Message

def unread_messages_count(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(receiver=request.user, is_read=False).order_by('-timestamp')
        unread_count = unread_messages.count()

        latest_message = unread_messages.first()  # Get latest unread message
        latest_message_info = {
            "id": latest_message.id if latest_message else None,
            "sender": latest_message.sender.first_name if latest_message else None
        }

        return {
            "unread_messages": unread_count,
            "latest_unread_message": latest_message_info
        }
    return {}


from Training.models import CartItem

def cart_context(request):
    cart_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return {'cart_count': cart_count}