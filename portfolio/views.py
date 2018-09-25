from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from .utils import render_to_pdf
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerSerializer
from .fusioncharts import FusionCharts
from django.http import JsonResponse
from decimal import Decimal





now = timezone.now()


def home(request):
    return render(request, 'portfolio/home.html', {'portfolio': home})


@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    get_currency('USD')
    return render(request, 'portfolio/customer_list.html', {'customers': customer})


@login_required
def customer_new(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_date = timezone.now()
            customer.save()
            customers = Customer.objects.filter(created_date__lte=timezone.now())
            return render(request, 'portfolio/customer_list.html',
                         {'customers': customers})
    else:
        form = CustomerForm()
        # print("Else")
    return render(request, 'portfolio/customer_new.html', {'form': form})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None)
    if request.method == "POST":
       # update
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now())
            return render(request, 'portfolio/customer_list.html',
                         {'customers': customer})
    else:
        # edit
        form = CustomerForm(instance=customer)
    return render(request, 'portfolio/customer_edit.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('portfolio:customer_list')


@login_required
def stock_list(request):
    stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
    return render(request, 'portfolio/stock_list.html', {'stocks': stocks})


@login_required
def stock_new(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html',
                         {'stocks': stocks})
    else:
        form = StockForm()
        # print("Else")
    return render(request, 'portfolio/stock_new.html', {'form': form})


@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            # stock.customer = stock.id
            stock.updated_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
    else:
        # print("else")
        form = StockForm(instance=stock)
    return render(request, 'portfolio/stock_edit.html', {'form': form})


@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    return redirect('portfolio:stock_list')


@login_required
def investment_list(request):
    investments = Investment.objects.filter(recent_date__lte=timezone.now())
    return render(request, 'portfolio/investment_list.html', {'investments': investments})


@login_required
def investment_new(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.created_date = timezone.now()
            investment.save()
            investments = Investment.objects.filter(recent_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html',
                         {'investments': investments})
    else:
        form = InvestmentForm()
        # print("Else")
    return render(request, 'portfolio/investment_new.html', {'form': form})


@login_required
def investment_edit(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save()
            # stock.customer = stock.id
            investment.updated_date = timezone.now()
            investment.save()
            investments = Investment.objects.filter(recent_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html', {'investments': investments})
    else:
        # print("else")
        form = InvestmentForm(instance=investment)
    return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def investment_delete(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    investment.delete()
    return redirect('portfolio:investment_list')


@login_required
def portfolio_1(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.get(id=pk)
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    return render(request, 'portfolio/portfolio.html', {'customers': customers, 'investments': investments,
                                                      'stocks': stocks,
                                                      'sum_acquired_value': sum_acquired_value,})

@login_required
def portfolio(request, pk):
    customers = get_object_or_404(Customer, pk=pk)
    # customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value')).get(
        'acquired_value__sum', 0.00)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value')).get('recent_value__sum',
                                                                                                 0.00)
    total_invest_result = sum_recent_value - sum_acquired_value

    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        # print('1...', stock.result_by_stock(stock.current_stock_value(), stock.initial_stock_value()))
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    total_stock_result = round((float(sum_current_stocks_value) - float(sum_of_initial_stock_value)), 2)
    sum_current_stocks_value = round(sum_current_stocks_value, 2)
    sum_of_initial_stock_value = round(sum_of_initial_stock_value, 2)

    portfolio_initial_invest = float(sum_acquired_value) + float(sum_of_initial_stock_value)
    portfolio_current_invest = float(sum_recent_value) + float(sum_current_stocks_value)
    portfolio_result = float(total_invest_result) + float(total_stock_result)

    print('total_stock_result ', total_stock_result)
    print('total_invest_result ', total_invest_result)
    context = {'customers': customers, 'investments': investments,
                                                        'stocks': stocks,
                                                        'sum_acquired_value': sum_acquired_value,
                                                        'sum_recent_value': sum_recent_value,
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,
                                                        'total_stock_result': total_stock_result,
                                                        'total_invest_result': total_invest_result,
                                                        'portfolio_initial_invest' : portfolio_initial_invest,
                                                        'portfolio_current_invest' : portfolio_current_invest,
                                                        'portfolio_result': portfolio_result,
                                                        }
    return render(request, 'portfolio/portfolio.html', context)


def login_view(request):
    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('portfolio:home')
    return render(request, 'registration/login_form.html', {'form': form, 'title': title})


def register_view(request):
    title = 'Register'
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        return redirect('portfolio:home')

    context = {
        "form": form,
        "title": title
    }
    return render(request, "registration/login_form.html", context)


def logout_view(request):
    logout(request)
    return redirect('portfolio:home')

@login_required
def admin_pdf(request, pk):
    customers = get_object_or_404(Customer, pk=pk)
    # customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value')).get(
        'acquired_value__sum', 0.00)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value')).get('recent_value__sum',
                                                                                                 0.00)
    total_invest_result = sum_recent_value - sum_acquired_value

    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        # print('1...', stock.result_by_stock(stock.current_stock_value(), stock.initial_stock_value()))
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    total_stock_result = round((float(sum_current_stocks_value) - float(sum_of_initial_stock_value)), 2)
    sum_current_stocks_value = round(sum_current_stocks_value, 2)
    sum_of_initial_stock_value = round(sum_of_initial_stock_value, 2)

    portfolio_initial_invest = float(sum_acquired_value) + float(sum_of_initial_stock_value)
    portfolio_current_invest = float(sum_recent_value) + float(sum_current_stocks_value)
    portfolio_result = float(total_invest_result) + float(total_stock_result)

    print('total_stock_result ', total_stock_result)
    print('total_invest_result ', total_invest_result)
    template = get_template('portfolio/pdf.html')
    context = {'customers': customers, 'investments': investments,
               'stocks': stocks,
               'sum_acquired_value': sum_acquired_value,
               'sum_recent_value': sum_recent_value,
               'sum_current_stocks_value': sum_current_stocks_value,
               'sum_of_initial_stock_value': sum_of_initial_stock_value,
               'total_stock_result': total_stock_result,
               'total_invest_result': total_invest_result,
               'portfolio_initial_invest': portfolio_initial_invest,
               'portfolio_current_invest': portfolio_current_invest,
               'portfolio_result': portfolio_result,
               }

    html = template.render(context)
    pdf = render_to_pdf('portfolio/pdf.html', context)
    if pdf:
        response =  HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename= "summary_{}.pdf"'.format(customers.cust_number)
        #return response
        #return HttpResponse(pdf, content_type='application/octet-stream')
        return pdf
    return HttpResponse("Not Found")



@login_required
def admin_pdf_1(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.get(id=pk)
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))

    template = get_template('portfolio/pdf.html')
    context = {'customers': customers, 'investments': investments,
                                                      'stocks': stocks,
                                                      'sum_acquired_value': sum_acquired_value,}
    html = template.render(context)
    pdf = render_to_pdf('portfolio/pdf.html', context)
    if pdf:
        response =  HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename= "summary_{}.pdf"'.format(customers.cust_number)
        #return response
        #return HttpResponse(pdf, content_type='application/octet-stream')
        return pdf
    return HttpResponse("Not Found")



def chart(request, pk):
    # Chart data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    customers = get_object_or_404(Customer, pk=pk)
    dataSource = {}
    dataSource['chart'] = {
        "caption": "Stock Details",
            "subCaption": "EFS",
            "xAxisName": "Stock",
            "yAxisName": "Value (In USD)",
            "numberPrefix": "$",
            "theme": "zune"
        }

    # The data for the chart should be in an array where each element of the array is a JSON object
    # having the `label` and `value` as key value pair.
    dataSource['categories'] = []
    categories = {}
    categories['category'] = []

    for stock_name in stocks:
        category = {}
        category['label'] = stock_name.name
        categories['category'].append(category)

    dataSource['categories'].append(categories)
    dataSource['dataset'] = []
    seriesname = {}
    seriesname['seriesname'] = 'Initial value'
    seriesname['data'] = []
    for key in stocks:
        data = {}
        # data['label'] = key.name
        data['value'] = float(key.initial_stock_value())
        seriesname['data'].append(data)

    dataSource['dataset'].append(seriesname)

    seriesname_1 = {}
    seriesname_1['seriesname'] = 'Current value'
    seriesname_1['data'] = []
    for key in stocks:
        data = {}
        # data['label'] = key.name
        data['value'] = float(key.current_stock_value())
        seriesname_1['data'].append(data)

    dataSource['dataset'].append(seriesname_1)

    print('datasource', str(dataSource))

    dataSource_1 = {}
    dataSource_1['chart'] = {
        "caption": "Investment Details",
        "subCaption": "EFS",
        "xAxisName": "Investment",
        "yAxisName": "Value (In USD)",
        "numberPrefix": "$",
        "theme": "fusion"
    }

    # The data for the chart should be in an array where each element of the array is a JSON object
    # having the `label` and `value` as key value pair.
    dataSource_1['categories'] = []
    categories = {}
    categories['category'] = []

    for invest_name in investments:
        category = {}
        category['label'] = invest_name.category
        categories['category'].append(category)

    dataSource_1['categories'].append(categories)
    dataSource_1['dataset'] = []
    seriesname = {}
    seriesname['seriesname'] = 'Acquired value'
    seriesname['data'] = []
    for key in investments:
        data = {}
        # data['label'] = key.name
        data['value'] = float(key.acquired_value)
        seriesname['data'].append(data)

    dataSource_1['dataset'].append(seriesname)

    seriesname_1 = {}
    seriesname_1['seriesname'] = 'Recent value'
    seriesname_1['data'] = []
    for key in investments:
        data = {}
        # data['label'] = key.name
        data['value'] = float(key.recent_value)
        seriesname_1['data'].append(data)

    dataSource_1['dataset'].append(seriesname_1)

    print('dataSource_1', str(dataSource_1))

    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0
    for stock in stocks:
        #print('1...', stock.result_by_stock(stock.current_stock_value(), stock.initial_stock_value()))
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    total_stock_result = round((float(sum_current_stocks_value) - float(sum_of_initial_stock_value)), 2)
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value')).get(
        'acquired_value__sum', 0.00)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value')).get('recent_value__sum',
                                                                                                 0.00)
    total_invest_result = sum_recent_value - sum_acquired_value
    portfolio_result = float(total_invest_result) + float(total_stock_result)

    dataSource_2 = {
        "chart": {
            "caption": "Split of portfolio result by stock and investment",
            "subCaption": "",
            "numberPrefix": "$",
            "showPercentInTooltip": "0",
            "decimals": "1",
            "useDataPlotColorForLabels": "1",
            "theme": "fusion"
        },
        "data": [
            {
                "label": "Stock",
                "value": float(total_stock_result)
            },
            {
                "label": "Investment",
                "value": float(total_invest_result)
            }
        ]
    }
    print('dataSource_2', str(dataSource_2))
    # Create an object for the Column 2D chart using the FusionCharts class constructor
    #column2D = FusionCharts("column2D", "ex1" , "600", "350", "chart-1", "json", dataSource)
    mscolumn2d = FusionCharts("mscolumn2d", "ex1", "600", "350", "chart-1", "json", dataSource)
    viewchart2 = FusionCharts("mscolumn2d", "ex2", "600", "350", "chart-2", "json", dataSource_1)
    viewchart3 = FusionCharts("pie2d", "chart-container", "550", "350", "chart-3", "json", dataSource_2)

    return render(request, 'portfolio/portfolio_graph.html', {'output': mscolumn2d.render(),
                                                              'output2': viewchart2.render(),
                                                              'output3': viewchart3.render(),
                                                           'customers': customers})



def get_josn_users(request):
    customers = Customer.objects.all().values()  # or simply .values() to get all fields
    users_list = list(customers)  # important: convert the QuerySet to a list object
    return JsonResponse(users_list, safe=False)



# List at the end of the views.py
# Lists all customers
class CustomerList(APIView):

    def get(self,request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)


def get_currency(curr_type):
    main_api = 'http://www.apilayer.net/api/live?access_key=96f793d9a5c161e784d5fec75d68ce77'
    api_currency = '& currencies='+curr_type+'&format=1'
    url = main_api + api_currency
    dataconv = "USD"+curr_type
    json_data = requests.get(url).json()
    print('dataconv ', dataconv)
    curr_val = (json_data["quotes"][dataconv])
    print(json_data)
    print('jsosn value ', curr_val)
    return curr_val

