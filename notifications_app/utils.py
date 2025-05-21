from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from .models import Notification, UserNotification, NotificationCategory, NotificationPreference


def create_notification(category_name, title, message, users=None, priority='medium',
                        expires_at=None, related_object=None, is_system_wide=False):
    """
    Create a notification and assign it to users

    Args:
        category_name (str): Name of the notification category
        title (str): Title of the notification
        message (str): Message content of the notification
        users (list): List of user objects to receive the notification
        priority (str): Priority level ('low', 'medium', 'high')
        expires_at (datetime): When the notification expires
        related_object (Model instance): Related object for the notification
        is_system_wide (bool): Whether this is a system-wide notification

    Returns:
        Notification: The created notification object
    """
    # Get or create the category
    category, _ = NotificationCategory.objects.get_or_create(name=category_name)

    # Create the notification
    notification = Notification.objects.create(
        category=category,
        title=title,
        message=message,
        priority=priority,
        expires_at=expires_at,
        is_system_wide=is_system_wide,
    )

    # Link to related object if provided
    if related_object:
        content_type = ContentType.objects.get_for_model(related_object)
        notification.content_type = content_type
        notification.object_id = related_object.id
        notification.save()

    # Assign to users
    if users:
        for user in users:
            # Check user preferences before creating notification
            if should_notify_user(user, category, 'in_app'):
                UserNotification.objects.create(
                    user=user,
                    notification=notification
                )

                # Send email if user prefers email notifications
                if should_notify_user(user, category, 'email'):
                    send_notification_email(user, notification)

    return notification


def should_notify_user(user, category, channel='in_app'):
    """
    Check if a user should be notified based on their preferences

    Args:
        user (User): The user to check
        category (NotificationCategory): The notification category
        channel (str): The notification channel ('in_app', 'email')

    Returns:
        bool: Whether the user should be notified
    """
    try:
        preference = NotificationPreference.objects.get(user=user, category=category)

        if not preference.is_enabled:
            return False

        if preference.channel == 'none':
            return False

        if preference.channel == 'both':
            return True

        return preference.channel == channel

    except NotificationPreference.DoesNotExist:
        # Default to notify if no preference is set
        return True


def send_notification_email(user, notification):
    """
    Send an email notification to a user

    Args:
        user (User): The user to email
        notification (Notification): The notification to send

    Returns:
        bool: Whether the email was sent successfully
    """
    subject = f"CozyWish: {notification.title}"
    message = f"{notification.message}\n\nThis is an automated message from CozyWish."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def get_user_notifications(user, include_read=False, include_deleted=False):
    """
    Get notifications for a user

    Args:
        user (User): The user to get notifications for
        include_read (bool): Whether to include read notifications
        include_deleted (bool): Whether to include deleted notifications

    Returns:
        QuerySet: QuerySet of UserNotification objects
    """
    query = Q(user=user)

    if not include_read:
        query &= Q(is_read=False)

    if not include_deleted:
        query &= Q(is_deleted=False)

    return UserNotification.objects.filter(query).select_related('notification', 'notification__category')


def get_unread_count(user):
    """
    Get the count of unread notifications for a user

    Args:
        user (User): The user to get the count for

    Returns:
        int: Count of unread notifications
    """
    return UserNotification.objects.filter(user=user, is_read=False, is_deleted=False).count()


def mark_all_as_read(user):
    """
    Mark all notifications as read for a user

    Args:
        user (User): The user to mark notifications for

    Returns:
        int: Number of notifications marked as read
    """
    now = timezone.now()
    count = UserNotification.objects.filter(user=user, is_read=False, is_deleted=False).update(
        is_read=True,
        read_at=now
    )
    return count


def delete_old_notifications(days=30):
    """
    Delete notifications older than the specified number of days

    Args:
        days (int): Number of days to keep notifications

    Returns:
        int: Number of notifications deleted
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    old_notifications = Notification.objects.filter(created_at__lt=cutoff_date)
    count = old_notifications.count()
    old_notifications.delete()
    return count


# Specific notification creation functions for common events

def notify_new_booking(booking):
    """Create notifications for a new booking"""
    # Notify the customer
    create_notification(
        category_name="Booking",
        title="Booking Confirmed",
        message=f"Your booking #{booking.booking_id} has been confirmed. Thank you for choosing CozyWish!",
        users=[booking.user],
        priority="medium",
        related_object=booking
    )

    # Notify the service provider
    create_notification(
        category_name="Booking",
        title="New Booking Received",
        message=f"You have received a new booking #{booking.booking_id} from {booking.user.email}.",
        users=[booking.venue.owner],
        priority="high",
        related_object=booking
    )


def notify_booking_cancellation(booking):
    """Create notifications for a cancelled booking"""
    # Notify the customer
    create_notification(
        category_name="Booking",
        title="Booking Cancelled",
        message=f"Your booking #{booking.booking_id} has been cancelled.",
        users=[booking.user],
        priority="medium",
        related_object=booking
    )

    # Notify the service provider
    create_notification(
        category_name="Booking",
        title="Booking Cancelled",
        message=f"Booking #{booking.booking_id} from {booking.user.email} has been cancelled.",
        users=[booking.venue.owner],
        priority="medium",
        related_object=booking
    )


def notify_new_review(review):
    """Create notifications for a new review"""
    # Notify the service provider
    create_notification(
        category_name="Review",
        title="New Review Received",
        message=f"You have received a new {review.rating}-star review from {review.user.email}.",
        users=[review.venue.owner],
        priority="medium",
        related_object=review
    )


def notify_review_response(review, response):
    """Create notifications for a response to a review"""
    # Notify the customer
    create_notification(
        category_name="Review",
        title="Response to Your Review",
        message=f"{review.venue.name} has responded to your review.",
        users=[review.user],
        priority="medium",
        related_object=review
    )


def notify_service_provider_approval(service_provider):
    """Create notifications for service provider approval"""
    # Notify the service provider
    create_notification(
        category_name="Account",
        title="Account Approved",
        message="Your service provider account has been approved. You can now add services and start receiving bookings.",
        users=[service_provider.user],
        priority="high"
    )


def notify_service_provider_rejection(service_provider, reason):
    """Create notifications for service provider rejection"""
    # Notify the service provider
    create_notification(
        category_name="Account",
        title="Account Not Approved",
        message=f"Your service provider account was not approved. Reason: {reason}",
        users=[service_provider.user],
        priority="high"
    )


def notify_booking_status_changed(booking, old_status):
    """Create notifications for booking status changes"""
    status_messages = {
        'pending': 'pending confirmation',
        'confirmed': 'confirmed',
        'completed': 'marked as completed',
        'cancelled': 'cancelled',
        'no_show': 'marked as no-show',
    }

    new_status = booking.status

    # Notify the customer
    create_notification(
        category_name="Booking",
        title=f"Booking Status Updated",
        message=f"Your booking #{booking.booking_id} has been {status_messages.get(new_status, new_status)}.",
        users=[booking.user],
        priority="medium" if new_status in ['confirmed', 'completed'] else "high",
        related_object=booking
    )

    # Notify the service provider if the customer changed the status
    if old_status != 'pending' and new_status in ['cancelled']:
        create_notification(
            category_name="Booking",
            title=f"Booking Status Updated",
            message=f"Booking #{booking.booking_id} from {booking.user.email} has been {status_messages.get(new_status, new_status)}.",
            users=[booking.venue.owner],
            priority="medium",
            related_object=booking
        )


# Payment notification is commented out until Payment model is available
# def notify_payment_received(payment):
#     """Create notifications for payment received"""
#     # Notify the customer
#     create_notification(
#         category_name="Payment",
#         title="Payment Confirmed",
#         message=f"Your payment of ${payment.amount} for booking #{payment.booking.booking_id} has been confirmed.",
#         users=[payment.booking.user],
#         priority="medium",
#         related_object=payment
#     )
#
#     # Notify the service provider
#     create_notification(
#         category_name="Payment",
#         title="Payment Received",
#         message=f"You have received a payment of ${payment.amount} for booking #{payment.booking.booking_id}.",
#         users=[payment.booking.venue.owner],
#         priority="medium",
#         related_object=payment
#     )


def create_system_announcement(title, message, expires_in_days=7):
    """Create a system-wide announcement"""
    expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)

    return create_notification(
        category_name="Announcement",
        title=title,
        message=message,
        priority="medium",
        expires_at=expires_at,
        is_system_wide=True
    )
