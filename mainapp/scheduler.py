from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone
from .models import Transactions
import logging
from datetime import timedelta
from notifications.models import FirebaseToken
from notifications.views import send_firebase_notification

# Set up logging
logger = logging.getLogger(__name__)

def update_transaction_status():
    try:
        # Get the current date
        current_date = timezone.now().date()

        # Find all transactions that are "Ongoing" and whose trip_end_date has passed
        ongoing_transactions = Transactions.objects.filter(
            status="Ongoing",
            trip_end_date__lt=current_date
        )

        # Update the status to "Completed"
        for transaction in ongoing_transactions:
            transaction.status = Transactions.StatusChoices.COMPLETE
            transaction.save()
            logger.info(f"Transaction {transaction.id} updated to Completed on {current_date}.")

        logger.info(f"Updated {ongoing_transactions.count()} transactions to Completed.")
    except Exception as e:
        logger.error(f"Error updating transaction statuses: {str(e)}")

def cancel_pending_transactions():
    try:
        # Get the current datetime
        current_datetime = timezone.now()

        # Calculate the time threshold (1 hour ago)
        time_threshold = current_datetime - timedelta(hours=1)

        # Find all "Pending" transactions that are older than 1 hour and payment_status is False
        pending_transactions = Transactions.objects.filter(
            status="Pending",
            payment_status=False,
            created_at__lt=time_threshold
        )

        # Delete the transactions
        for transaction in pending_transactions:
            transaction_id = transaction.id
            user = FirebaseToken.objects.get(user=transaction.user.user)
            send_firebase_notification(
                user.token,
                title="Cancel the booking",
                body=f"Booking canceled due to payment timeout."
            )
            transaction.delete()
            logger.info(f"Transaction {transaction_id} canceled and deleted due to payment timeout (based on created_at).")

        logger.info(f"Canceled and deleted {pending_transactions.count()} transactions due to payment timeout (based on created_at).")
    except Exception as e:
        logger.error(f"Error canceling pending transactions (based on created_at): {str(e)}")

def cancel_pending_transactions_by_updated_at():
    try:
        # Get the current datetime
        current_datetime = timezone.now()

        # Calculate the time threshold (1 hour ago)
        time_threshold = current_datetime - timedelta(hours=1)

        # Find all "Pending" transactions that have not been updated in the last 1 hour
        pending_transactions = Transactions.objects.filter(
            status="Pending",
            updated_at__lt=time_threshold
        )

        # Delete the transactions
        for transaction in pending_transactions:
            transaction_id = transaction.id
            try:
                user = FirebaseToken.objects.get(user=transaction.user.user)
                send_firebase_notification(
                    user.token,
                    title="Cancel the booking",
                    body=f"Booking canceled due to remaining in Pending status for too long."
                )
            except FirebaseToken.DoesNotExist:
                logger.warning(f"No FirebaseToken found for user {transaction.user.user.id}. Notification not sent.")
            except Exception as e:
                logger.error(f"Error sending notification for transaction {transaction_id}: {str(e)}")
            transaction.delete()
            logger.info(f"Transaction {transaction_id} canceled and deleted due to remaining in Pending status for too long (based on updated_at).")

        logger.info(f"Canceled and deleted {pending_transactions.count()} transactions due to remaining in Pending status for too long (based on updated_at).")
    except Exception as e:
        logger.error(f"Error canceling pending transactions (based on updated_at): {str(e)}")

def start_scheduler():
    # Create a BackgroundScheduler instance
    scheduler = BackgroundScheduler()

    # Add the update_transaction_status job with an IntervalTrigger (every 1 minute for testing)
    scheduler.add_job(
        update_transaction_status,
        trigger=IntervalTrigger(minutes=60),  # Run every 1 minute
        id="update_transaction_status",
        replace_existing=True,
    )

    # Add the cancel_pending_transactions job with an IntervalTrigger (every 1 minute for testing)
    scheduler.add_job(
        cancel_pending_transactions,
        trigger=IntervalTrigger(minutes=60),  # Run every 1 minute
        id="cancel_pending_transactions",
        replace_existing=True,
    )

    # Add the cancel_pending_transactions_by_updated_at job with an IntervalTrigger (every 1 minute for testing)
    scheduler.add_job(
        cancel_pending_transactions_by_updated_at,
        trigger=IntervalTrigger(minutes=60),  # Run every 1 minute
        id="cancel_pending_transactions_by_updated_at",
        replace_existing=True,
    )

    # Start the scheduler
    scheduler.start()
    print("Scheduler started: update_transaction_status, cancel_pending_transactions, and cancel_pending_transactions_by_updated_at will run every 1 minute.")
    logger.info("Scheduler started: update_transaction_status, cancel_pending_transactions, and cancel_pending_transactions_by_updated_at will run every 1 minute.")