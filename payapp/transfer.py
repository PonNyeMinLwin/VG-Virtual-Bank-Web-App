from locale import currency

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from register.models import Account, Transaction
from django.db.models import Q

@login_required
def search_user_account_id(request):
    accounts = Account.objects.all() # Getting all accounts
    query = request.POST.get("account_id") # Gets the account id that the user chose

    # Show the account that the user specified only
    if query:
        accounts = accounts.filter(Q(account_id=query)).distinct()

    context = {"accounts": accounts, "query": query}
    return render(request, "pay/search-account-id.html", context)

def send_money(request, account_id):
    try:
        account = Account.objects.get(account_id=account_id)
    except:
        messages.warning(request, "Account not found with this ID!")
        return redirect("find-user-id")
    context = {"account": account}
    return render(request, "pay/send-money.html", context)

def process_payment(request, account_id):
    # Getting the account of the person the payment is going to
    target_account = Account.objects.get(account_id=account_id)

    # Getting the user details of the recipient (for later use too (for display))
    receiver = target_account.user
    receiver_account = target_account

    # Getting the account and user details of the sender (for later use too (for display))
    sender_account = request.user.account
    sender = request.user

    # If user input is successfully read - go to payment confirmation
    # If not, send an error warning
    if request.method == "POST":
        amount = request.POST.get("transfer-amount")

        # Checking if sender's balance is enough for the payment
        # If it's successful - create a log of the transaction : If not - warn the user (and change status?)
        if float(amount) > 0 :
            if sender_account.balance > float(amount) :
                transaction = Transaction.objects.create(
                    user = request.user,
                    amount = amount,
                    receiver = receiver,
                    sender = sender,
                    receiver_account=receiver_account,
                    sender_account = sender_account,
                    transaction_type = "payment"
                )
                transaction.save() # Save it

                messages.success(request, "Successfully sent money!")
                transaction_id = transaction.transaction_id # And get the transaction ID
                return redirect("payment-confirmation", target_account.account_id, transaction_id)
            else:
                messages.warning(request, "You don't have enough money!")
                return redirect("find-user-id")
        else:
            messages.warning(request, "Amount cannot be negative!")
            return redirect("find-user-id")
    else:
        messages.warning(request, "Error occurred during transaction, try again!")
        return redirect("index")

def payment_confirmation(request, account_id, transaction_id):
    try:
        cur_account = Account.objects.get(account_id=account_id)
        cur_transaction = Transaction.objects.get(transaction_id=transaction_id)

        sender = request.user
        sender_account = request.user.account
        receiver = cur_account.user
        receiver_account = cur_account

        # Take away from the sender account's balance and update
        sender_account.balance -= cur_transaction.amount
        sender_account.save()

        # Add the amount to the receiver's balance and update
        receiver_account.balance += cur_transaction.amount
        receiver_account.save()
    except:
        messages.warning(request, "Transaction not found with this Account ID!")
        return redirect("index")

    context = {"account": cur_account, "transaction": cur_transaction}
    return render(request, "pay/payment-confirmation.html", context)

@login_required
def search_user_requests(request) :
    accounts = Account.objects.all() # Getting all accounts
    query = request.POST.get("account_id") # Gets the account id that the user chose

    if query:
        accounts = accounts.filter(Q(account_id=query)).distinct()

    context = {"accounts": accounts, "query": query}
    return render(request, "pay/search-request-account-id.html", context)

def request_money(request, account_id):
    account = Account.objects.get(account_id=account_id)
    context = {"account": account}
    return render(request, "pay/request-money.html", context)

def process_request(request, account_id):
    # Getting the account of the person the request is going to
    target_account = Account.objects.get(account_id=account_id)

    # Getting the account and user details of the request sender
    requestor = request.user
    requestor_account = request.user.account

    # Getting the account and user details of the request receiver
    receiver = target_account.user
    receiver_account = target_account

    # If user input is successfully read - go to Sent Request page
    # If not, send an error warning
    if request.method == "POST":
        amount = request.POST.get("request_amount")

        if float(amount) > 0:
            new_request = Transaction.objects.create(
                user=request.user,
                amount=amount,
                receiver=receiver,
                sender=requestor,
                receiver_account=receiver_account,
                sender_account=requestor_account,
                transaction_type="request"
            )
            new_request.save()  # Save it

            messages.success(request, "Successfully requested money!")
            transaction_id = new_request.transaction_id  # And get the transaction ID
            return redirect("request-confirmation", target_account.account_id, transaction_id)
        else:
            messages.warning(request, "Amount cannot be negative!")
            return redirect("find-request-user-id")
    else:
        messages.warning(request, "Error occurred during transaction, try again!")
        return redirect("index")

def request_confirmation(request, account_id, transaction_id):
    cur_account = Account.objects.get(account_id=account_id)
    cur_transaction = Transaction.objects.get(transaction_id=transaction_id)

    sender = request.user
    receiver = cur_account.user

    context = {"account": cur_account, "transaction": cur_transaction}
    return render(request,"pay/request-confirmation.html", context)

def request_accept_or_deny(request, account_id, transaction_id):
    cur_account = Account.objects.get(account_id=account_id)
    cur_transaction = Transaction.objects.get(transaction_id=transaction_id)

    context = {"account": cur_account, "transaction": cur_transaction}
    return render(request, "pay/request-accept-or-deny.html", context)

def transfer_requested_amount(request, account_id, transaction_id):
    account = Account.objects.get(account_id=account_id)
    transaction = Transaction.objects.get(transaction_id=transaction_id)

    sender = request.user
    sender_account = request.user.account

    # If sent payment button was clicked
    if request.method == "POST":
        # If amount requested is more than receiver's balance or less than 0
        # No need to check if amount requested is less than 0 because the check was done in process_request
        if sender_account.balance <= 0 or sender_account.balance < transaction.amount:
            messages.warning(request, "Not enough funds! Try again after depositing more money.")
            return redirect("dashboard")
        else:
            sender_account.balance -= transaction.amount
            sender_account.save()

            account.balance += transaction.amount
            account.save()

            transaction.transaction_type = "request_acc"
            transaction.save()

            messages.success(request, f"Successfully transferred requested amount to { account.user.comment.full_name }!")
            return redirect("dashboard")
    else:
        messages.warning(request, "Error occurred during transaction, try again!")
        return redirect("dashboard")

@login_required
def delete_transaction(request, transaction_id):
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        transaction.delete()
        messages.success(request, "Successfully deleted request!")
    except Transaction.DoesNotExist:
        messages.error(request, "Transaction not found!")
    return redirect("view-transactions")