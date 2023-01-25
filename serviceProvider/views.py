import collections
import email
from django.shortcuts import HttpResponse, redirect, render
import requests
import json
import pymongo
from email import message
from typing import Collection
from pymongo import MongoClient
import smtplib
import random
from bson.objectid import ObjectId



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
        cluster = MongoClient("mongodb+srv://demo:demo@cluster0.csdz61e.mongodb.net/?retryWrites=true&w=majority")
        db = cluster["bachelorNeeds"]

        DBConnect.__instance = db
# Create your views here.



def authentication(request):
  if request.method=='GET':
    return render(request,"enterOtp2.html")
  if(request.method=='POST'):
    db = DBConnect.getInstance()
    collection = db["serviceProviders"]
    nid = request.session['nid']
    otp = request.POST['otp']

    if(collection.count_documents({"nid":nid ,"otp":otp})!=1):
      message = {"msg": "invalid opt please try again with correct otp"}
      return render(request, 'enterOtp.html', message)     
    
    collection = db["service"]
    if(collection.count_documents({"nid":nid})!=1):
      return render(request,"registration.html")

    userInfo= collection.find_one({"nid":nid})
    contest = {
      "data":userInfo
    }
    return render(request,"update-sp-registration.html",contest)
def update_post(oldData , newData ):
    db = DBConnect.getInstance()
    collection = db['service']
    collection.delete_one({"_id":ObjectId(oldData['_id'])})
    collection.insert_one(newData)

def login(request):
  if request.method=='GET':
    return render(request,"login2.html")
  if request.method =='POST':
    db = DBConnect.getInstance()
    collection = db['serviceProviders']
    
    # taking information via POST method
    nid = request.POST['nid']
    phoneNumber = request.POST['phoneNumber']
    otp = "1234"
    msg = None
    request.session['nid'] = nid
    
    if(collection.count_documents({"nid": nid})!=0 or collection.count_documents({"phoneNumber": phoneNumber})!=0):
      msg = "This nid or Phone number already Used"
      message = {"msg": msg}
      return render(request,"enterOtp2.html",message) 
    
    #for sending otp in user email
    

    #saving user information in database
    userInfo = {
        "name": None,
        "nid": nid,
        "phoneNumber": phoneNumber,
        "gender": None,
        "bloodGroup": None,
        "homeAddress": None,
        "notification": [],
        "dp": "nodp.jpg",
        "otp": otp,
    }

    request.session['nid'] = nid
    

    collection.insert_one(userInfo)
    return render(request,"enterOtp2.html") 


def registration(request):
  if request.method=='GET':
    db = DBConnect.getInstance()
    collection = db['service']
    nid = request.session['nid']
    
    if(collection.count_documents({"nid": nid})!=0 ):
      data =  collection.find_one({"nid":nid})
      contest = {
         'data' : data
      }
      return render(request,"update-sp-registration.html",contest)
    return render(request,"registration.html")
  if(request.method=='POST'):
    db = DBConnect.getInstance()
    collection = db['service']
    nid = request.session['nid'] 
    userInfo = {
        "f_name": request.POST['first-name'],
        "l_name":request.POST['last-name'],
        "nid": nid,
        "company":request.POST['company'],
        # "tradelicence": request.POST['trade-licence'],
        # "gender": request.POST['company'],
        "address": request.POST['address'],
        # "zipcode": request.POST['zip-code'],
        "phonenumber":request.POST["phone-number"],
        "email":request.POST['email'],
        "state":request.POST['state'],
        "servicetype":request.POST['service-type'],
        "description": request.POST['description'],
        "image": "nodp.jpg",
        
    }
    contest = {
      "data":userInfo
    }
    collection.insert_one(userInfo)
    print(userInfo)
    return render(request,"update-sp-registration.html",contest)

    
def update_registration(request):
  if(request.method=='GET'):
    db = DBConnect.getInstance()
    collection = db['service']
    nid = request.session['nid']
    
    if(collection.count_documents({"nid": nid})!=0 ):
      data =  collection.find_one({"nid":nid})
      contest = {
         'data' : data
      }
      return render(request,"update-sp-registration.html",contest)
    return render(request,"registration.html")
    
  if(request.method=='POST'):
    db = DBConnect.getInstance()
    collection = db['service']
    nid = request.session['nid'] 
    userInfo = {
        "f_name": request.POST['first-name'],
        "l_name": request.POST['last-name'],
        "nid": nid,
        "company":request.POST['company'],
        # "tradelicence": request.POST['trade-licence'],
        # "gender": request.POST['company'],
        "address": request.POST['address'],
        # "zipcode": request.POST['zip-code'],
        "phonenumber":request.POST["phone-number"],
        "email":request.POST['email'],
        "state":request.POST['state'],
        "servicetype":request.POST['service-type'],
        "description": request.POST['description'],
        # "image": "nodp.jpg",
        
    }
    oldData =  collection.find_one({"nid":nid})
    # newData =  { "$set": userInfo }
    update_post(oldData,userInfo)
    contest = {
      'data':userInfo
    }
    return render(request,"update-sp-registration.html",contest)
    


def user_side(request):
  if(request.method=="GET"):
    db = DBConnect.getInstance()
    collection = db['service']
    data = collection.find({})
    contest = {
         'data' : data
      }
    return render(request,"userSide.html",contest)
     


def logout(request):
  session_keys = list(request.session.keys())
  for key in session_keys:
    del request.session[key]
  return render(request,"main.html")


def search(request):
  search_post = request.GET['search']
  db= DBConnect.getInstance()
  collection = db['service']
  data = collection.find({ "company": {"$regex": search_post,"$options":'i'}})
  data= list(data)
  data1 = collection.find({ "servicetype": {"$regex": search_post,"$options":'i'}})
  data2 = collection.find({ "description": {"$regex": search_post,"$options":'i'}})
  data3 = collection.find({ "address": {"$regex": search_post,"$options":'i'}})
  
  for i in data1:
      if(i in data):
          continue
      data.append(i)
  for i in data2:
      if(i in data):
          continue
      data.append(i)
  for i in data3:
      if(i in data):
          continue
      data.append(i)

  
  allPosts=[]


  for i in data:
      postShow={
          "f_name":i["f_name"],
          "l_name": i['l_name'],
          "company":i['company'],
          "address":i['address'],
          "description":i["description"],
          
      }

      allPosts.append(postShow)
  return  render(request,"search_result2.html",{"data":allPosts})