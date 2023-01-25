import datetime
import collections
import email
from django.shortcuts import HttpResponse, redirect, render
import requests
from django.core.files.storage import FileSystemStorage
import json
import pymongo
from email import message
from typing import Collection
from pymongo import MongoClient
import smtplib
import random



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

def getUsr(email_):
    db=DBConnect.getInstance()
    collection=db["users"]
    usr=collection.find_one({"email":email_})
    return usr

def myMsgList(request):
  db=DBConnect.getInstance()
  collection=db["message"]
  email=request.session['email']
  
  my_chat= collection.find({"from":email})
  my_chat2= collection.find({"to":email})

  chat_list=[]
  for i in my_chat:
    a=getUsr(i['from'])
    if(a not in chat_list):
      chat_list.append(a)
    a=getUsr(i['to'])
    if(a not in chat_list):
      chat_list.append(a)
  
  for i in my_chat2:
    a=getUsr(i['from'])
    if(a not in chat_list):
      chat_list.append(a)
    a=getUsr(i['to'])
    if(a not in chat_list):
      chat_list.append(a)
  
  try:
    chat_list.remove(getUsr(email))
  except:
    pass
  return  render(request,'myChat.html',{"chatWith":chat_list})
    




def messageOneToOne(request):
    nid=request.session['email']
    usrNid=request.GET['email']
    if(nid==usrNid):
      return redirect(request.META.get('HTTP_REFERER'))

    me=getUsr(nid)
    other=getUsr(usrNid)
    message={}
    fs = FileSystemStorage()
    myData={
        "name":me['name'],
        "nid":me['email'],
        'dp':fs.url(me['dp']),
    }

    message['myInfo']=myData
    message['otherInfo']={
        "name": other['name'],
        "nid": other['email'],
        'dp': fs.url(other['dp']),
    }


    db = DBConnect.getInstance()
    collection = db["message"]
    msgs=[]
    myMsg=collection.find({"from":nid,"to":usrNid})
    for i in myMsg:
        msgs.append(i)

    toMeMsg=collection.find({"from":usrNid,"to":nid})
    for i in toMeMsg:
        msgs.append(i)

    msgs=sorted(msgs,key=lambda d: d['time'])
    message['conversation']=msgs

    return render(request, "message.html",{"message":message})

def saveMsg(request):

    from_=request.GET['myNid']
    to_ =request.GET['otherNid']
    now_=datetime.datetime.now()
    db = DBConnect.getInstance()
    collection = db["message"]
    msg=request.GET['message']
    if(len(msg)==0):
        return redirect(request.META.get('HTTP_REFERER'))
    msgBlock={
        "from":from_,
        "to":to_,
        "message":msg,
        "time":now_,
    }
    collection.insert_one(msgBlock)
    return redirect(request.META.get('HTTP_REFERER'))



def main(request):
  try:
    request.session['email']
    return redirect('/home')
  except:
    return render(request,"main.html")

def index(request):
  try:
    request.session['email']
    return redirect('/home')
  except:
    return render(request,"index.html")

def login(request):
  if request.method == 'GET':
    try:
      request.session['email']
      return redirect('/home')
    except:
      return render(request,"login.html")
  
  if(request.method=='POST'):
    db = DBConnect.getInstance()
    collection = db["users"]
    email = request.POST['email']
    password = request.POST['password']

    if(collection.count_documents({"email":email ,"password":password})!=1):
      message = {"msg": "invalid email or password"}
      return render(request, 'login.html', message)     

    request.session['email'] = email
    
    return redirect("/home")

def signup(request):
  if request.method == 'GET':
    try:
      request.session['email']
      return redirect('/home')
    except:
      return render(request,"login.html")

  if request.method =='POST':
    db = DBConnect.getInstance()
    collection = db['users']
    
    # taking information via POST method
    name = request.POST['name']
    email = request.POST['email']
    password = request.POST['password']

    msg = None
    
    
    if(collection.count_documents({"email": email})!=0):
      msg = "Email is already used"
      message = {"msg": msg}
      return render(request, 'login.html', message)
    
    #for sending otp in user email
    otp = ""
    for i in range(6):
      n = random.randint(0,9)
      otp += str(n)
    
    sender_email = "bachelorneed@gmail.com"
    sender_pass = "csjcwenzefdejpwc"
    rec_email = email
    otp_msg  = "Your 6 digit otp is : "+otp
     
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(sender_email,sender_pass)
    server.sendmail(sender_email,rec_email,otp)

    #saving user information in database
    userInfo = {
        "name": name,
        "email": email,
        "password": password,
        "gender": None,
        "phone_number": None,
        "bloodGroup": None,
        "homeAddress": None,
        "notification": [],
        "dp": "nodp.jpg",
        "cover":"noCover.jpeg",
        "otp": otp

    }

    request.session['email'] = email
    

    collection.insert_one(userInfo)
    return render(request, 'enterOtp.html')

def logout(request):
  session_keys = list(request.session.keys())
  for key in session_keys:
    del request.session[key]
  return render(request,"main.html")




def userVarification(request):
  if(request.method=='POST'):
    db = DBConnect.getInstance()
    collection = db["users"]
    email = request.session['email']
    otp = request.POST['otp']

    if(collection.count_documents({"email":email ,"otp":otp})!=1):
      message = {"msg": "invalid opt please try again with correct otp"}
      return render(request, 'enterOtp.html', message)     
    
    
    return redirect("/home") 


def home(request):
  try:
    request.session['email']
    db = DBConnect.getInstance()
    collection = db['homePosts']
    data = collection.find({"postType":"basic"})
    fs = FileSystemStorage()
    allData = []
    for i in data:
       img = i['images']
       i['images'] = fs.url(img)
       allData.append(i)
    contest = {
         'data' : allData
      }
    return render(request,"home.html",contest)
  except:
    return render(request,"index.html")


def profile(request):
  try:
    request.session['email']
    email = request.session['email']
    db = DBConnect.getInstance()
    collection = db['users']
    data = collection.find_one({"email":email})
    fs = FileSystemStorage()
    
    img = data['dp']
    data['dp'] = fs.url(img)
    
    contest = {
         'data' : data
      }
    return render(request,"profile.html",contest)
  except:
    return render(request,"index.html")
def updateProfile(request):
  # try:
    if(request.method=='GET'):
      request.session['email']
      email = request.session['email']
      db = DBConnect.getInstance()
      collection = db['users']
      data = collection.find_one({"email":email})
      fs = FileSystemStorage()
      
      img = data['dp']
      data['dp'] = fs.url(img)
      
      contest = {
          'data' : data
        }
      return render(request,"updateProfile.html",contest)
    if request.method =='POST':
      request.session['email']
      email = request.session['email']
      db = DBConnect.getInstance()
      collection = db['users']
      uploaded_file = request.FILES['dp']
      fs = FileSystemStorage()   
      photo_name=fs.save(uploaded_file.name, uploaded_file)
      old_data = collection.find_one({'email':email})
      new_data ={
        
        "phone_number": request.POST['phone-number'],
        "bloodGroup": request.POST['bloodGroup'],
        "homeAddress": request.POST['homeAddress'],
        
        "dp": photo_name,
        
      }
      newData =  { "$set": new_data }
    collection.update_one(old_data,newData)
    
    contest = {
          'data' : collection.find_one({"email":email})
        }
    return render(request,"profile.html",contest)
  # except:
  #   return render(request,"index.html")

def userAddPost(request):
  if(request.method=='GET'):
    return render(request,"addPost.html")
  if(request.method=='POST'):
    db = DBConnect.getInstance()
    collection = db["homePosts"]
    email = request.session['email']
    uploaded_file = request.FILES['images']
    fs = FileSystemStorage()   
    photo_name=fs.save(uploaded_file.name, uploaded_file)
    adminCollection = db["users"]
    old_data = adminCollection.find_one({'email':email})
    postInfo = {
       'postAdmin':email,
       'postAdminName':old_data['name'],
       'state' : request.POST['state'],
       'postType' : 'basic',
       'location': request.POST['location'],
       'phonenumber': request.POST['phone-number'],
       'rent': request.POST['rent'],
       'description': request.POST['description'],
       'images': photo_name

    }
    collection.insert(postInfo)
    
    collection = db['homePosts']
    data = collection.find({"postType":"basic"})
    fs = FileSystemStorage()
    allData = []
    for i in data:
       img = i['images']
       i['images'] = fs.url(img)
       allData.append(i)
    contest = {
         'data' : allData
      }
    return render(request,"home.html",contest)

def viewPost(request):
  pass


def searchPost(request):
    search_post = request.GET['search']
    db= DBConnect.getInstance()
    collection = db['homePosts']
    data = collection.find({ "location": {"$regex": search_post,"$options":'i'}})
    data= list(data)
    data1 = collection.find({ "description": {"$regex": search_post,"$options":'i'}})
    data2 = collection.find({ "state": {"$regex": search_post,"$options":'i'}})
    
    for i in data1:
        if(i in data):
            continue
        data.append(i)
    for i in data2:
        if(i in data):
            continue
        data.append(i)

    fs= FileSystemStorage()
    allPosts=[]


    for i in data:
        postShow={
            "postNo":i["_id"],
            "postAdmin": i['postAdmin'],
            "location":i['location'],
            "state":i['state'],
            "photo":None,
            "phonenumber":i["phonenumber"],
            "rent": i['rent'],
            "description":i['description'],
        }

        if(i['images']):
            postShow['photo']=fs.url(i['images'])


        allPosts.append(postShow)

    
    return  render(request,"search_result.html",{"data":allPosts})