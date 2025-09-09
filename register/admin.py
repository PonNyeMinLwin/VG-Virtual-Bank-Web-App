from django.contrib.auth.admin import UserAdmin
from register.models import User
from django.contrib import admin
from register.models import Account, Comment
from register.models import Transaction

# Project description states I cannot use admin functionalities
# However, this is the only way I know how to add functionalities in admin
# Look at Canvas on how to make custom dashboard to view (and edit) Account data
from import_export.admin import ImportExportModelAdmin

# This class controls the admin display for Accounts
class AccountAdmin(ImportExportModelAdmin):
    list_filter = ["account_status"]
    list_editable = ('balance', 'account_status')
    list_display = ('user', 'account_id', 'balance', 'account_status')

# This class controls the admin display for Comments
class CommentAdmin(ImportExportModelAdmin):
    search_fields = ["full_name"]
    list_display = ['user', 'full_name', 'currency']

class TransactionAdmin(admin.ModelAdmin):
    list_editable = ['amount', 'receiver', 'sender', 'transaction_type']
    list_display = ['user', 'amount', 'receiver', 'sender', 'transaction_type']
    
admin.site.register(Account, AccountAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Transaction, TransactionAdmin)