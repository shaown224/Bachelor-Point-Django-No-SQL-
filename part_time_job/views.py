import collections
import email
from django.shortcuts import HttpResponse, redirect, render
from django.core.files.storage import FileSystemStorage
import requests
import json
import pymongo
from email import message
from typing import Collection
from pymongo import MongoClient
from django.shortcuts import render
from django.db.models import Q
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


def job_home(request):
    db = DBConnect.getInstance()
    collection = db['jobcreateinfo']
    data = collection.find({})
    data = list(data)
    fs = FileSystemStorage()
    content = {
         'data' : data
      }
    return render(request,"job_home.html",content)

def myPosts(request):
  db = DBConnect.getInstance()
  collection = db['jobcreateinfo']
  email=request.session['email']
  data = collection.find({"email":email})
  data = list(data)
  fs = FileSystemStorage()
  content = {
        'data' : data
    }
  return render(request,"my_posts2.html",content)

def deletePost(request):
  db = DBConnect.getInstance()
  collection = db['jobcreateinfo']
  id_= request.GET['id']
  collection.delete_one({"salary":id_})
  return redirect(request.META.get('HTTP_REFERER'))
  

def post_job(request):
    return render(request,"post_job.html")


def createjob(request):
  if request.method =='POST':
    db = DBConnect.getInstance()
    collection = db['jobcreateinfo']
    # taking information via POST method

    email=request.session['email']
    contact=request.POST['contact']
    job_title =request.POST['job_title']
    job_description= request.POST['job_description']
    salary = request.POST['salary']
    job_type = request.POST['job_type']
    #saving information in database
    jobInfo = {
        "email" : email,
        "job_title": job_title,
        "job_description": job_description,
        "contact" : contact,
        "salary" : salary,
        "job_type" : job_type

    }
    #print(jobInfo)
    collection.insert_one(jobInfo)
    collection = db['jobcreateinfo']
    data = collection.find({})
    data = list(data)
    content = {
         'data' : data
      }
    print(content)
    return render(request,"job_home.html",content)

def Search_job(request):
    search_post = request.GET.get('search')
    db= DBConnect.getInstance()
    collection = db['jobcreateinfo']
    data = collection.find({ "job_description": {"$regex": search_post,"$options":'i'}})
    data= list(data)
    data1 = collection.find({ "job_title": {"$regex": search_post,"$options":'i'}})
    # print(data)
    for i in data1:
        if(i in data):
            continue
        data.append(i)
    fs = FileSystemStorage()
    content = {
         'data' : data
      }
    return render(request,"search_job_show.html",content)
