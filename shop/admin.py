from django.contrib import admin
from .models import Candle, Order, BulkInquiry


@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    list_display  = ('name', 'price', 'stock', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('id', 'candle_name', 'customer_name', 'customer_phone', 'quantity', 'total_price', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('customer_name', 'customer_phone', 'customer_email', 'candle_name')


@admin.register(BulkInquiry)
class BulkInquiryAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'company', 'phone', 'occasion', 'quantity', 'needed_by', 'status', 'created_at')
    list_filter   = ('status', 'occasion')
    list_editable = ('status',)
    search_fields = ('name', 'company', 'phone', 'email', 'message')
