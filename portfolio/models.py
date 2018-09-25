from django.db import models
from django.utils import timezone
import requests


# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    cust_number = models.IntegerField(blank=False, null=False)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=10)
    email = models.EmailField(max_length=200)
    cell_phone = models.CharField(max_length=50)
    created_date = models.DateTimeField(
        default=timezone.now)
    updated_date = models.DateTimeField(auto_now_add=True)

    def created(self):
        self.created_date = timezone.now()
        self.save()

    def updated(self):
        self.updated_date = timezone.now()
        self.save()

    def __str__(self):
        return str(self.cust_number)


class Investment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='investments')
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    acquired_value = models.DecimalField(max_digits=10, decimal_places=2)
    acquired_date = models.DateField(default=timezone.now)
    recent_value = models.DecimalField(max_digits=10, decimal_places=2)
    recent_date = models.DateField(default=timezone.now, blank=True, null=True)

    def created(self):
        self.acquired_date = timezone.now()
        self.save()

    def updated(self):
        self.recent_date = timezone.now()
        self.save()

    def __str__(self):
        return str(self.customer)

    def results_by_investment(self):
        return self.recent_value - self.acquired_value


class Stock(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='stocks')
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    shares = models.DecimalField (max_digits=10, decimal_places=1)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(default=timezone.now, blank=True, null=True)

    def created(self):
        self.recent_date = timezone.now()
        self.save()

    def __str__(self):
        return str(self.customer)

    def initial_stock_value(self):
        return round((self.shares * self.purchase_price), 2)

    def current_stock_price(self):
        symbol_f = str(self.symbol)
        main_api = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='
        api_key = '&interval=1min&apikey=RQDU8RE5H4CU94R2'
        url = main_api + symbol_f + api_key
        json_data = requests.get(url).json()
        mkt_dt = (json_data["Meta Data"]["3. Last Refreshed"])
        open_price = float(json_data["Time Series (1min)"][mkt_dt]["1. open"])
        share_value = round(open_price, 2)
        return share_value

    def current_stock_value(self):
        symbol_f = str(self.symbol)
        main_api = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='
        api_key = '&interval=1min&apikey=RQDU8RE5H4CU94R2'
        url = main_api + symbol_f + api_key
        json_data = requests.get(url).json()
        mkt_dt = (json_data["Meta Data"]["3. Last Refreshed"])
        open_price = float(json_data["Time Series (1min)"][mkt_dt]["1. open"])
        share_value = open_price
        curr_stk_val = round((float(share_value) * float(self.shares)), 2)
        return curr_stk_val








