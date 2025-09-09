from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from register.models import Account, Transaction
from django.db.models import Q

def transaction_history_list(request):
    # For direct payments only
    payment_history = Transaction.objects.filter(sender=request.user, transaction_type="payment").order_by("-id")
    receive_history = Transaction.objects.filter(receiver=request.user, transaction_type="payment").order_by("-id")

    # For payment requests only
    request_sent_history = Transaction.objects.filter(Q(transaction_type="request") | Q(transaction_type="request_acc"), sender=request.user).order_by("-id")
    request_received_history = Transaction.objects.filter(Q(transaction_type="request") | Q(transaction_type="request_acc"),receiver=request.user).order_by("-id")

    context = {
        "payment_history": payment_history,
        "receive_history": receive_history,
        "request_sent_history": request_sent_history,
        "request_received_history": request_received_history
    }

    return render(request, "pay/view-all-transactions.html", context)
