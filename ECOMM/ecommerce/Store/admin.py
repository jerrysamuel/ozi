from django.contrib import admin
from .models import Order, Product, Mystore, Dispute, MyReview

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Mystore)
admin.site.register(MyReview)


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("order", "buyer_email", "seller_email", "status", "created_at", "resolved_at")
    actions = ["resolve_as_cancelled", "resolve_as_completed"]

    def resolve_as_cancelled(self, request, queryset):
        for dispute in queryset:
            try:
                # Ensure that the dispute is open before resolving
                if dispute.status == Dispute.OPEN:
                    
                    
                    # Move the funds from the buyer's escrow to the seller's balance
                    dispute.order.buyer.wallet.escrow_balance -= dispute.order.amount
                    dispute.order.seller.wallet.balance += dispute.order.amount
                    
                    # Save updated wallet balances
                    dispute.order.buyer.wallet.save()
                    dispute.order.seller.wallet.save()
                    
                    
                    # Mark dispute as resolved
                    dispute.status = Dispute.RESOLVED  
                    dispute.save()

                    self.message_user(request, f"Order #{dispute.order.id} has been cancelled successfully.")
                else:
                    self.message_user(request, f"Dispute for Order #{dispute.order.id} is already resolved.", level="error")
            except ValueError as e:
                self.message_user(request, str(e), level="error")

    resolve_as_cancelled.short_description = "Mark as Cancelled"

    def resolve_as_completed(self, request, queryset):
        for dispute in queryset:
            try:
                # Ensure that the dispute is open before resolving
                if dispute.status == Dispute.OPEN:


                    # Move the funds from the buyer's escrow to the buyer's main wallet
                    dispute.order.buyer.wallet.escrow_balance -= dispute.order.amount
                    dispute.order.buyer.wallet.balance += dispute.order.amount
                    
                    # Save updated wallet balance
                    dispute.order.buyer.wallet.save()
                   
                    # Mark dispute as resolved
                    dispute.status = Dispute.RESOLVED  
                    dispute.save()

                    self.message_user(request, f"Order #{dispute.order.id} has been completed successfully.")
                else:
                    self.message_user(request, f"Dispute for Order #{dispute.order.id} is already resolved.", level="error")
            except ValueError as e:
                self.message_user(request, str(e), level="error")

    resolve_as_completed.short_description = "Mark as Completed"

