from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Candle, Order, BulkInquiry


VALID_ORDER = {
    'name': 'Asha', 'phone': '9876543210', 'email': 'asha@example.com',
    'upi_id': 'asha@paytm', 'address': '12 MG Road, Pune', 'quantity': '2',
}


class PlaceOrderTests(TestCase):
    def setUp(self):
        self.candle = Candle.objects.create(
            name='Rose', description='Rose candle', price=Decimal('199.50'), stock=3
        )
        self.url = reverse('place_order', args=[self.candle.id])

    def test_valid_order_creates_order_and_reduces_stock(self):
        response = self.client.post(self.url, VALID_ORDER)
        self.assertTemplateUsed(response, 'shop/success.html')
        order = Order.objects.get()
        self.assertEqual(order.total_price, Decimal('399.00'))
        self.candle.refresh_from_db()
        self.assertEqual(self.candle.stock, 1)

    def test_order_more_than_stock_is_rejected(self):
        response = self.client.post(self.url, {**VALID_ORDER, 'quantity': '5'})
        self.assertTemplateUsed(response, 'shop/buy.html')
        self.assertFalse(Order.objects.exists())
        self.candle.refresh_from_db()
        self.assertEqual(self.candle.stock, 3)

    def test_blank_name_and_address_are_rejected(self):
        self.client.post(self.url, {**VALID_ORDER, 'name': ' ', 'address': ''})
        self.assertFalse(Order.objects.exists())

    def test_invalid_phone_is_rejected(self):
        self.client.post(self.url, {**VALID_ORDER, 'phone': '12345'})
        self.assertFalse(Order.objects.exists())


class HomeBestSellerTests(TestCase):
    def test_best_sellers_are_top_four_by_units_sold(self):
        candles = [
            Candle.objects.create(name=f'C{i}', description='', price=Decimal('100'), stock=10)
            for i in range(6)
        ]
        for candle, qty in [(candles[2], 5), (candles[4], 3), (candles[1], 1)]:
            Order.objects.create(
                candle=candle, candle_name=candle.name, customer_name='X',
                customer_phone='9876543210', customer_address='A', upi_id='x@upi',
                quantity=qty, total_price=candle.price * qty,
            )
        response = self.client.get(reverse('home_landing'))
        best = list(response.context['best_sellers'])
        self.assertEqual(len(best), 4)
        self.assertEqual(best[:3], [candles[2], candles[4], candles[1]])


class DashboardAccessTests(TestCase):
    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, '/dashboard/login/?next=/dashboard/', fetch_redirect_response=False)

    def test_non_staff_user_is_redirected(self):
        User.objects.create_user('bob', password='pass12345')
        self.client.login(username='bob', password='pass12345')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_staff_user_sees_dashboard_with_no_orders(self):
        User.objects.create_user('admin', password='pass12345', is_staff=True)
        self.client.login(username='admin', password='pass12345')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_rev'], Decimal('0.00'))

    def test_logout_requires_post(self):
        self.assertEqual(self.client.get(reverse('admin_logout')).status_code, 405)
        self.assertEqual(self.client.post(reverse('admin_logout')).status_code, 302)


VALID_BULK = {
    'name': 'Ravi', 'company': 'Acme', 'phone': '9876543210', 'email': '',
    'occasion': 'corporate', 'quantity': '50', 'needed_by': '', 'message': 'Diwali gifts',
}


class BulkOrderTests(TestCase):
    def test_valid_inquiry_is_saved(self):
        response = self.client.post(reverse('bulk_order'), VALID_BULK)
        self.assertTrue(response.context['submitted'])
        inquiry = BulkInquiry.objects.get()
        self.assertEqual(inquiry.quantity, 50)
        self.assertEqual(inquiry.status, 'new')

    def test_invalid_inquiries_are_rejected(self):
        bad_inputs = [
            {'quantity': '5'},
            {'phone': '123'},
            {'occasion': 'nope'},
            {'name': ''},
            {'needed_by': '2000-01-01'},
            {'needed_by': 'not-a-date'},
        ]
        for bad in bad_inputs:
            self.client.post(reverse('bulk_order'), {**VALID_BULK, **bad})
        self.assertFalse(BulkInquiry.objects.exists())

    def test_staff_can_update_inquiry_status(self):
        inquiry = BulkInquiry.objects.create(name='R', phone='9876543210', occasion='party', quantity=20)
        User.objects.create_user('admin', password='pass12345', is_staff=True)
        self.client.login(username='admin', password='pass12345')
        self.client.post(reverse('admin_bulk_status', args=[inquiry.id]), {'status': 'contacted'})
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.status, 'contacted')

    def test_anonymous_cannot_update_inquiry_status(self):
        inquiry = BulkInquiry.objects.create(name='R', phone='9876543210', occasion='party', quantity=20)
        self.client.post(reverse('admin_bulk_status', args=[inquiry.id]), {'status': 'closed'})
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.status, 'new')
