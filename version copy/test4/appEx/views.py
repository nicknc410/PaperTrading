from django.shortcuts import render, redirect
import re
from django.utils.timezone import datetime
from django.http import HttpResponse
import requests
from django.contrib.auth.forms import UserCreationForm
from .forms import *
import urllib.request
from datetime import date, datetime, timedelta
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen
import json
import ssl
from urllib.request import urlopen
from .models import *
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
import yfinance as yf
api_key="09af29ab6806b18e3306fda218cac2d1"

# function to render stock page
def stock(request):
    return render(request, "appEx/stock.html")
# function to render information of each stock where name is the Ticker 
def stock_info(request, name):
    if request.method=="POST":
        existing = FavoriteStock.objects.filter(name=request.session.get('username'), favorite=name).exists()
        if not existing:
            FavoriteStock.objects.create(name=request.session.get('username'), favorite=name)
    stock_data=yf.Ticker(name)
    data=(stock_data.history(period="1y", interval="1mo")).to_json(orient='records')
    datesIni=stock_data.history(period="1y", interval="1mo").index.tolist()
    datesFinal=[]
    for i in datesIni:
        datesFinal.append(str(i)[:10])
    url="https://financialmodelingprep.com/api/v3/income-statement/"+name+"?limit=120&apikey="+api_key
    def get_data(url, stock):
        ssl_context=ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        response = urllib.request.urlopen(url,context=ssl_context)
        data = response.read().decode("utf-8")
        return json.loads(data)
    income_data=get_data(url, name)
    
    return render(request, "appEx/stockFormat/"+ name+".html", {
        'data':data, 
        'ebitda':income_data[0]['ebitda'],
        'revenue':income_data[0]['revenue'],
        'grossProfit':income_data[0]['grossProfit'],
        'ebitdaratio':income_data[0]['ebitdaratio'],
        'netIncome':income_data[0]['netIncome'],
        'eps':income_data[0]['eps'],
        'dates':json.dumps(datesFinal)
        })
#function to send and receive messages between user
def message(request):
    if request.method == 'POST':
        form = SendForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['send']
            message = form.cleaned_data['message']
            Message.objects.create(sender=request.session.get('username'),receive=username,content=message)
            return redirect("/home")
    else:
        form=SendForm()
        mess=Message.objects.filter(receive=request.session.get('username'))
        messagesList=[]
        for m in mess:
            messagesList.append(m.sender+ ": "+m.content)
        print(messagesList)
        return render(request, "appEx/contact.html",{'messages':messagesList,'form':form})

#renders home page with user info and assets graph
def home(request):
    favs = FavoriteStock.objects.filter(name=request.session.get('username'))
    investments=Invested.objects.filter(name=request.session.get('username'))
    investList=[]
    for tick in investments:
        investList.append(tick.invested)
    fav_list=[]
    for stock in favs:
        fav_list.append(stock.favorite)
    
    createdDate=Acc.objects.filter(username=request.session.get('username'))
    createdDate=createdDate[0].created
    send={}
    if createdDate=="1" or createdDate=="":
        send={}
    else:
        startDate = datetime.strptime(createdDate, "%m/%d/%Y")
        end=datetime.today()
        new_list=list(set(investList))
        send={}
        l=yf.Ticker("AAPL").history(start=startDate, end=datetime.today())
        for idx in range(len(l.index.tolist())):
            send[idx]=[]
            send[idx].append(l.index.tolist()[idx].strftime("%m/%d/%Y"))
        for i in new_list:
            temp=yf.Ticker(i)
            newObj=Invested.objects.filter(name=request.session.get('username'), invested=i)
            pDiff=newObj[0].price
            hist=temp.history(start=startDate, end=datetime.today())
            for j in range(min(len(send),len(hist['Open']))):
                send[j].append(10000-(pDiff-hist['Open'][j])*newObj[0].shares)
    return render(request, "appEx/home.html", {'name': request.session.get('username'), 'balance':round(request.session.get('balance'),2), 'favs':fav_list, 'invest':list(set(investList)), 'send':json.dumps(send)})
#function to handle sign up and render its page
def signup(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            existing_user = Acc.objects.filter(username=username).exists()
            if existing_user:
                messages.info(request, "Username is already taken")
                return redirect("/signup", )
            password = form.cleaned_data['password']
            hashed_password = make_password(password)
            today = date.today().strftime("%m/%d/%Y")
            Acc.objects.create(username=username, password=hashed_password, balance=10000.00, created=today)
            return redirect("/")
    else:
        form = LoginForm()
    return render(request, 'appEx/signup.html', {'form':form})

#function to handle login and render the login page
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['username']
            pw=form.cleaned_data['password']
            try:
                user = Acc.objects.get(username=name)
            except Acc.DoesNotExist:
                messages.info(request, "Incorrect User")
                return redirect("/")
            if check_password(pw,user.password):
                request.session['username']=name
                request.session['balance']=user.balance
                return redirect("/home")
            else:
                messages.info(request, "Incorrect Password")
                return redirect("/")
    else:
        form = LoginForm()
    return render(request, 'appEx/login.html', {'form':form})

#function to handle the calculation of assets of the user
def invest(request):
    if request.method=="POST":
        form = InvestForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['stock']
            share=form.cleaned_data['shares']
            stock=yf.Ticker(ticker)
            priceCur=stock.history()['Open'][-1]
            if priceCur*share>request.session.get('balance'):
                messages.info(request, "Not enough balance")
                return redirect("appEx/invest.html")
            query=Acc.objects.filter(username=request.session.get('username'))
            request.session['balance']-=priceCur*share
            instance = query.first()
            instance.balance -= priceCur*share
            instance.save()
            Invested.objects.create(name=request.session.get('username'), invested=ticker, price=priceCur, shares=share)
            return redirect("/home")
    else:
        form=InvestForm()
    return render(request, 'appEx/invest.html', {'form':form})

