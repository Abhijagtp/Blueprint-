from django.utils import timezone
from Users.models import CustomUser


def reactivate_suspended_users():
    print("Running reactivation check...")
    now = timezone.now()
    suspended_users = CustomUser.objects.filter(
        account_status='Suspend',
        suspended_until__lte=now
    )

    for user in suspended_users:
        user.account_status = 'Open'
        user.is_active = True
        user.suspended_until = None
        user.save()
        print(f"User {user.username} has been automatically re-activated.") 



# from django.utils import timezone
# from Users.models import CustomUser  # replace with your actual user model import

# def reactivate_suspended_users():
#     now = timezone.now()
#     CustomUser.objects.filter(
#         suspended_until__lte=now,
#         is_active=False,
#         account_status="Suspended"
#     ).update(
#         is_active=True,
#         suspended_until=None,
#         account_status="Open"
#     )
