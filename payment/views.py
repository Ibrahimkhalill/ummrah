from rest_framework.response import Response
from rest_framework.decorators import api_view
from mainapp.serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from mainapp.models import Transactions
from django.core.exceptions import ObjectDoesNotExist
import stripe
from rest_framework.response import Response
from django.http import JsonResponse , HttpResponse
from collections import defaultdict
from datetime import datetime
from notifications.views import send_firebase_notification
from notifications.models import Notification, FirebaseToken

from authentications.models import CustomUser

# # Set your Stripe secret key
# stripe.api_key = "sk_test_51RIsTHQSRjpsKWf56YNwHsjJSJ2rUWGbjyp11dn8MmFbxbfK84jF2HCOyAOk3DMCQ5BctbVc9xKqGjjKkaQS6l6700AEWZ0n4w"

# # Webhook secret (get this from your Stripe Dashboard)
# endpoint_secret = 'whsec_neyb2HN7aKRfTcNoSgOh4mHWZY4vl84z'




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    # Use environment variable for domain
    DOMAIN = "https://nusukey.duckdns.org/api/payment"

    # Get request data
    amount = request.data.get("amount")
    transactions_id = request.data.get("transactions_id")
    currency = request.data.get("currency", "sar")

    # Validate amount
    if not amount:
        return Response({"error": "Amount is required."}, status=400)

    try:
        amount = int(float(amount) * 100)  # Convert to smallest unit
        if amount <= 0:
            return Response({"error": "Amount must be greater than 0."}, status=400)
    except (ValueError, TypeError):
        return Response({"error": "Invalid amount format."}, status=400)

    # Validate currency
    if currency not in ["sar", "usd"]:
        return Response({"error": "Unsupported currency."}, status=400)

    # Validate transaction ID
    if not transactions_id:
        return Response({"error": "Transaction ID is required."}, status=400)
    # Get the authenticated user
    user = request.user
    
    try:
        # Create Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": amount,
                        "product_data": {
                            "name": "Tourist Guide Service Payment",
                            "description": f"Payment for guide service ",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{DOMAIN}/checkout/success/",
            cancel_url=f"{DOMAIN}/checkout/cancel/",
            metadata={
                "user_id": str(user.id),
                "transaction_id": str(transactions_id),
                "custom_note": "Tracking payment for tourist guide service",
            },
        )

        return Response({"checkout_url": session.url}, status=200)

    except stripe.error.InvalidRequestError as e:
        return Response({"error": f"Stripe request error: {str(e)}"}, status=400)
    except stripe.error.AuthenticationError as e:
        return Response({"error": "Authentication with Stripe failed."}, status=401)
    except stripe.error.StripeError as e:
        return Response({"error": f"Stripe error: {str(e)}"}, status=400)
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_admin_session(request):
    # Use environment variable for domain
    DOMAIN = "https://lamprey-included-lion.ngrok-free.app/api/payment"

    # Get request data
    amount = request.data.get("amount")
    transactions_id = request.data.get("transactions_id")
    currency = request.data.get("currency", "sar")

    # Validate amount
    if not amount:
        return Response({"error": "Amount is required."}, status=400)

    try:
        amount = int(float(amount) * 100)  # Convert to smallest unit
        if amount <= 0:
            return Response({"error": "Amount must be greater than 0."}, status=400)
    except (ValueError, TypeError):
        return Response({"error": "Invalid amount format."}, status=400)

    # Validate currency
    if currency not in ["sar", "usd"]:
        return Response({"error": "Unsupported currency."}, status=400)

    # Validate transaction ID
    if not transactions_id:
        return Response({"error": "Transaction ID is required."}, status=400)
    # Get the authenticated user
    user = request.user
    
    try:
        # Create Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": amount,
                        "product_data": {
                            "name": "Tourist Guide Service Payment",
                            "description": f"Payment for guide service ",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"{DOMAIN}/checkout/success/",
            cancel_url=f"{DOMAIN}/checkout/cancel/",
            metadata={
                "user_id": str(user.id),
                "transaction_id": str(transactions_id),
                "custom_note": "Tracking payment for tourist guide service",
            },
        )

        return Response({"checkout_url": session.url}, status=200)

    except stripe.error.InvalidRequestError as e:
        return Response({"error": f"Stripe request error: {str(e)}"}, status=400)
    except stripe.error.AuthenticationError as e:
        return Response({"error": "Authentication with Stripe failed."}, status=401)
    except stripe.error.StripeError as e:
        return Response({"error": f"Stripe error: {str(e)}"}, status=400)
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    
@api_view(["POST"])
def stripe_webhook(request):
    payload = request.body.decode("utf-8")  # Decode payload from bytes to string
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    if not sig_header:
        return Response({"error": "Missing Stripe signature header"}, status=400)

    try:
         event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return Response({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response({"error": "Invalid signature"}, status=400)

    # Process successful checkout event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})

        transaction_id = metadata.get("transaction_id")
        user_id = metadata.get("user_id")
        if not transaction_id:
           
            return Response({"error": "Missing transaction ID"}, status=400)

        # Update transaction status
        transaction = get_object_or_404(Transactions, id=transaction_id)
        
        transaction.status = Transactions.StatusChoices.ONGOING
        transaction.payment_status = True  # Mark as paid
        transaction.save()
        
        user = get_object_or_404(CustomUser, id=user_id)
        print("user", user, transaction)
        
        notification = notification = Notification.objects.create(
            user=user,
            title="Payment Complete",
            message=f"Tourist {transaction.user.name} has made a payment."
        )
        notification.save()
        try:
            user_token = FirebaseToken.objects.get(user=user)
            send_firebase_notification(
                user_token.token,
                title="Payment Complete",
                body=f"Tourist {transaction.user.name} has made a payment."
            )
        except ObjectDoesNotExist:
            print(f"No Firebase token found for user {transaction.guide.user}")


    return Response({"status": "success"}, status=200)

def checkout_success(request):
    return HttpResponse("Your checkout was successful!", status=200)


def checkout_cencel(request):
    return HttpResponse("Your checkout was successful!", status=200)



# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_subscription(request):
#     """
#     Retrieve the subscription details for the authenticated user.
#     """
#     user = request.user
#     try:
#         # Retrieve subscription for the current user
#         subscription = Subscription.objects.get(user=user)
#         serializer = SubscriptionSerializer(subscription)
#         return Response({"subscription": serializer.data}, status=200)
#     except Subscription.DoesNotExist:
#         return Response({"message": "No subscription found for this user."}, status=404)
    
    


# @background(schedule=60)  # Check every 60 seconds (adjust as needed)
# def check_subscription_status():
#     """
#     Automatically check and deactivate expired free trials or subscriptions.
#     """
#     now = datetime.now()

#     # Check for expired free trials
#     free_trial_expired = Subscription.objects.filter(
#         free_trial=True, free_trial_end__lte=now
#     )
#     for subscription in free_trial_expired:
#         subscription.free_trial = False
#         subscription.save()
#         print(f"Free trial expired for user {subscription.user.username}")

#     # Check for expired subscriptions
#     subscription_expired = Subscription.objects.filter(
#         is_active=True, end_date__lte=now
#     )
#     for subscription in subscription_expired:
#         subscription.is_active = False
#         subscription.save()
#         print(f"Subscription expired for user {subscription.user.username}")

#     print("Checked free trial and subscription statuses.")
    
    


# def get_invoices_by_subscription(subscription_id):
#     """
#     Fetch all invoices associated with a subscription.
#     """
#     try:
#         invoices = stripe.Invoice.list(subscription=subscription_id)
#         return invoices
#     except stripe.error.StripeError as e:
#         # Handle Stripe API errors
#         print(f"Stripe Error: {e}")
#         return None


# def get_total_revenue_by_subscription(subscription_id):
#     """
#     Calculate the total revenue for a specific subscription based on paid invoices.
#     """
#     invoices = get_invoices_by_subscription(subscription_id)
#     if not invoices:
#         return 0  # Return 0 if the Stripe API call fails

#     total_revenue = 0
#     for invoice in invoices.auto_paging_iter():
#         if invoice.get("paid", False):  # Safely access "paid" to avoid KeyError
#             total_revenue += invoice.get("amount_paid", 0) / 100  # Stripe amounts are in cents

#     return total_revenue


# @api_view(["GET"])
# def calculate_all_for_dashboard(request):
#     """
#     Calculate the revenue for all users and classify them into free and pro users.
#     """
#     # Step 1: Fetch all Stripe subscriptions
#     subscriptions = Subscription.objects.all()
#     if not subscriptions:
#         return Response({"error": "Failed to fetch subscriptions from Stripe"}, status=500)

#     # Step 2: Classify users
#     pro_user_count = Subscription.objects.filter(is_active=True).count()  # Count active users
#     free_user_count = Subscription.objects.filter(free_trial_end__isnull=False).count()

#     # Step 3: Calculate total revenue
#     total_revenue = 0
#     for subscription in subscriptions:
#         if subscription.stripe_subscription_id is not None:
#             subscription_revenue = get_total_revenue_by_subscription(subscription.stripe_subscription_id)
#             total_revenue += subscription_revenue

#     # Step 4: Build response
#     response = {
#         "free_user": free_user_count,
#         "pro_user": pro_user_count,
#         "total_revenue": round(total_revenue, 2),  # Ensure total revenue is rounded to 2 decimal places
#     }

#     return Response(response, status=200)


@api_view(["GET"])
def calculate_yearly_revenue(request):
    """
    Calculate monthly revenue starting from the first subscription year to the current year.
    """
    # Step 1: Fetch all subscriptions from the database
    subscriptions = Transactions.objects.all()
    if not subscriptions:
        return Response({"error": "No subscriptions found"}, status=404)

    # Step 2: Calculate revenue grouped by year and month
    yearly_monthly_revenue = defaultdict(lambda: {month: 0 for month in range(1, 13)})  # Year -> Month -> Revenue

    first_year = datetime.now().year  # Initialize with the current year
    for subscription in subscriptions:
      

     
            if subscription.status("Comeplete"):  # Only consider paid invoices
                created_date = datetime.fromtimestamp(subscription["created"])
                year = created_date.year
                month = created_date.month
                yearly_monthly_revenue[year][month] += subscription.get("amount_paid", 0) / 100  # Convert cents to dollars
                first_year = min(first_year, year)  # Update the first year if earlier

    # Step 3: Prepare data from the first year to the current year
    current_year = datetime.now().year
    all_revenue_data = []

    for year in range(first_year, current_year + 1):
        data = [yearly_monthly_revenue[year].get(month, 0) for month in range(1, 13)]
        all_revenue_data.append({
            "year": year,
            "data": data
        })

    # Step 4: Build response
    response = {
        "all_revenue_data": all_revenue_data
    }

    return Response(response, status=200)