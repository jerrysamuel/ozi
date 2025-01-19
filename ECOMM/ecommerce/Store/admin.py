from django.contrib import admin
from .models import Order, Product, Mystore, Dispute

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Mystore)

from django.contrib import admin

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ("order", "buyer_email", "seller_email", "status", "created_at", "resolved_at")
    actions = ["resolve_as_cancelled", "resolve_as_completed"]

    def resolve_as_cancelled(self, request, queryset):
        for dispute in queryset:
            try:
                dispute.order.resolve_dispute("cancel")
                self.message_user(request, f"Order {dispute.order.order_id} canceled successfully.")
            except ValueError as e:
                self.message_user(request, str(e), level="error")

    def resolve_as_completed(self, request, queryset):
        for dispute in queryset:
            try:
                dispute.order.resolve_dispute("complete")
                self.message_user(request, f"Order {dispute.order.order_id} completed successfully.")
            except ValueError as e:
                self.message_user(request, str(e), level="error")

    resolve_as_cancelled.short_description = "Mark as Cancelled"
    resolve_as_completed.short_description = "Mark as Completed"
