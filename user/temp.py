import smtplib, random
from email import message
from typing import Collection
from django.shortcuts import redirect, render
from django.http import HttpResponse
from pymongo import MongoClient
import requests
import json


class DBConnect:
    __instance = None

    @staticmethod
    def getInstance():
        if DBConnect.__instance == None:
            DBConnect()
        return DBConnect.__instance

    def __init__(self):
        if DBConnect.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            cluster = MongoClient("mongodb+srv://root:1234@cluster1.8jmyghr.mongodb.net/?retryWrites=true&w=majority")
            db = cluster["ethica"]

            DBConnect.__instance = db





def validateLogin(request):
    # came in the right way
    if (request.method == 'POST'):
        db = DBConnect.getInstance()
        collection = db["user"]
        email = request.POST["email"]
        password = request.POST["password"]

        # invalid try
        if (collection.count_documents({"email": email, "password": password}) != 1):
            message = {"msg": "invalid email or password"}
            return render(request, 'html/login.html', message)

        # valid user
        data = collection.find_one({"email": email, "password": password})
        nid = data["nid"]

        # save session
        request.session['nid'] = nid

        return redirect("/home")

    # came from somewere else
    return render(request, 'html/createAccount.html', message)