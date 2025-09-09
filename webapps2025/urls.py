"""
URL configuration for webapps2025 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from register import views # homepage for when a user is registered
from register import views as register_views # homepage for guest/un-registered users

from payapp import transfer, transactions

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Sign-up, Login, & Register
    path("sign-up/", register_views.register_user, name="sign-up"),
    path("login/", register_views.login_view, name="login"),
    path("logout/", register_views.logout_view, name="logout"),

    #Homepage
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("about/", register_views.about, name="about"),
    path("contact-us/", register_views.contact_us, name="contact_us"),

    # Edit & View Accounts
    path("edit-account/", views.edit_user_detail_view, name="edit-account"),
    path("view-account/", views.account_view, name="view-account"),

    # Search Users

    # This is for finding accounts when DIRECTLY TRANSFERRING money
    path("find-user-id/", transfer.search_user_account_id, name="find-user-id"),
    # This is for finding accounts when REQUESTING money
    path("find-request-user-id/", transfer.search_user_requests, name="find-request-user-id"),

    # Transaction and Account Activity Log URLs
    path("view-transactions/", transactions.transaction_history_list, name="view-transactions"),

    # Transfer Money
    path("send-money/<account_id>/", transfer.send_money, name="send-money"),
    path("process-payment/<account_id>/", transfer.process_payment, name="process-payment"),
    path("payment-confirmation/<account_id>/<transaction_id>/", transfer.payment_confirmation, name="payment-confirmation"),

    # Request Money
    path("request-money/<account_id>/", transfer.request_money, name="request-money"),
    path("process-request/<account_id>/", transfer.process_request, name="process-request"),
    path("request-confirmation/<account_id>/<transaction_id>/", transfer.request_confirmation, name="request-confirmation"),

    # Accept or Deny (Delete) Requests
    path("request-choice/<account_id>/<transaction_id>/", transfer.request_accept_or_deny, name="request-choice"),
    path("process-request-choice/<account_id>/<transaction_id>/", transfer.transfer_requested_amount, name="process-request-choice"),
    path("delete-transaction/<transaction_id>/", transfer.delete_transaction, name="delete-transaction"),
]
