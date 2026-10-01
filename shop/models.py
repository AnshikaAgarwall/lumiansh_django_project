from django.db import models

class Candle(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    candle = models.ForeignKey(Candle, on_delete=models.SET_NULL, null=True)
    candle_name = models.CharField(max_length=200)  # Stores name at time of purchase
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField(max_length=254, blank=True, null=True)

    customer_address = models.TextField()
    upi_id = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"


class BulkInquiry(models.Model):
    OCCASION_CHOICES = [
        ('corporate', 'Corporate Gifting'),
        ('festive', 'Festive Gifting'),
        ('wedding', 'Wedding / Return Gifts'),
        ('party', 'Party / Event'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('confirmed', 'Confirmed'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=254, blank=True)
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES)
    quantity = models.PositiveIntegerField()
    needed_by = models.DateField(blank=True, null=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'bulk inquiries'

    def __str__(self):
        return f"Bulk inquiry {self.id} from {self.name}"