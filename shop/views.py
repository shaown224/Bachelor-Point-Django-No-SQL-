from bson.objectid import ObjectId
import datetime
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
from django.core.files.storage import FileSystemStorage

def getAllComment(post):
    allComment=[]
    db=DBConnect.getInstance()
    collection=db["users"]
    for i in post['comment']:
        commenterEmail=i[0]
        commenter=collection.find_one({"email":commenterEmail})
        commenterName=commenter['name']
        allComment.append({
            "commenterName":commenterName,
            "commenterEmail":commenterEmail,
            "comment":i[1]})
    return allComment

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

def getUsr(email_):
    db=DBConnect.getInstance()
    collection=db["users"]
    usr=collection.find_one({"email":email_})
    return usr

def savePost(request):
    email=request.session['email']
    photo_name=None
    
    uploaded_file = request.FILES["photo"]
    fs = FileSystemStorage()
    photo_name=fs.save(uploaded_file.name, uploaded_file)

    price=request.POST['price']
    category=request.POST['category']
    location=request.POST['location']
    postContent=request.POST['postcontent']



    post={
        "email": email,
        "content":postContent,
        "photo":photo_name,
        "comment":[],
        "price":price,
        "category":category,
        "location":location,
        "date":datetime.datetime.now(),
    }
    print(post)
    db=DBConnect.getInstance()
    collection=db["post"]
    collection.insert_one(post)
    
    collection=db["post"]
    fs= FileSystemStorage()
    allPosts=[]
    usr=getUsr(email)
    posts = collection.find({"email":email})
    for i in posts:
        comments=getAllComment(i)

        postShow={
            "postNo":i["_id"],
            "content": i['content'],
            "comment":comments,
            "date":i['date'],
            "photo":None,
            "category":i["category"],
            "price": i['price'],
            "location":i['location'],
        }

        if(i['photo']):
            postShow['photo']=fs.url(i['photo'])


        allPosts.append(postShow)

    data={}
    data['name']=usr['name']
    data['posts']=allPosts
    return  render(request,"my_posts.html",data)

def addComment(request):
    content=request.POST["comment"]
    postid=request.POST["postid"]
    commenter=request.session['email']
    if(len(content)==0):
        return redirect("seeAllPost")


    db=DBConnect.getInstance()
    collection=db["post"]
    postData=collection.find_one({"_id":ObjectId(postid)})
    allComments=postData["comment"]
    allComments.append([commenter, content])
    postData["comment"]=allComments
    collection.delete_one({"_id":ObjectId(postid)})
    collection.insert_one(postData)

    return redirect(request.META.get('HTTP_REFERER'))

def showPostCategory(request):
    return  render(request,"caterogy_type.html")



def seeAllPost(request):
    email=request.session['email']
    category=request.GET['category']
    db = DBConnect.getInstance()
    collection=db["post"]
    fs= FileSystemStorage()
    allPosts=[]
    usr=getUsr(email)
    posts = collection.find({"category":category})
    for i in posts:
        comments=getAllComment(i)

        postShow={
            "postNo":i["_id"],
            "content": i['content'],
            "comment":comments,
            "date":i['date'],
            "photo":None,
            "category":category,
            "price": i['price'],
            "location":i['location'],
        }

        if(i['photo']):
            postShow['photo']=fs.url(i['photo'])


        allPosts.append(postShow)

    data={}
    data['name']=usr['name']
    data['posts']=allPosts
    return  render(request,"all_post.html",data)






def shopHome(request):
    email=request.session['email']
    db = DBConnect.getInstance()
    collection = db['users']
    usr=collection.find_one({"email":email})
    return render(request,"create_post.html",{"name":usr['name']})

def deletePost(request):
    postid=request.GET['postid']

    db=DBConnect.getInstance()
    collection=db["post"]
    collection.delete_one({"_id":ObjectId(postid)})
    return redirect(request.META.get('HTTP_REFERER'))

def myPosts(request):
    email=request.session['email']

    db = DBConnect.getInstance()
    collection=db["post"]
    fs= FileSystemStorage()
    allPosts=[]
    usr=getUsr(email)
    posts = collection.find({"email":email})
    for i in posts:
        comments=getAllComment(i)

        postShow={
            "postNo":i["_id"],
            "content": i['content'],
            "comment":comments,
            "date":i['date'],
            "photo":None,
            "category":i["category"],
            "price": i['price'],
            "location":i['location'],
        }

        if(i['photo']):
            postShow['photo']=fs.url(i['photo'])


        allPosts.append(postShow)

    data={}
    data['name']=usr['name']
    data['posts']=allPosts
    return  render(request,"my_posts.html",data)

def search_product(request):
    search_post = request.GET.get('search')
    db= DBConnect.getInstance()
    email=request.session['email']
    usr=getUsr(email)
    collection = db['post']
    data = collection.find({ "content": {"$regex": search_post,"$options":'i'}})
    data = list(data)
    data1 = collection.find({ "category": {"$regex": search_post,"$options":'i'}})

    for i in data1:
        if(i in data):
            continue
        data.append(i)
    fs= FileSystemStorage()
    allPosts=[]


    for i in data:
        comments=getAllComment(i)

        postShow={
            "postNo":i["_id"],
            "content": i['content'],
            "comment":comments,
            "date":i['date'],
            "photo":None,
            "category":i["category"],
            "price": i['price'],
            "location":i['location'],
        }

        if(i['photo']):
            postShow['photo']=fs.url(i['photo'])


        allPosts.append(postShow)

    data={}
    data['name']=usr['name']
    data['posts']=allPosts
    return  render(request,"all_post.html",data)
