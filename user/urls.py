from django.urls import path
from . import views
from serviceProvider import views as spViews

urlpatterns =[
    path('',views.main,name = "main"),
    path('index/',views.index,name = "user-index"),
    path('login/',views.login,name="user-login"),
    path('signup/',views.signup,name="user-signup"),
    path('home/',views.home,name="home"),
    path('logout/',views.logout,name = "user-logout"),
    path('userVarification/',views.userVarification, name="userVarification"),
    path('userAddPost/',views.userAddPost,name = 'user-add-post'),
    path('userProfile',views.profile,name='user-profile'),
    path('userUpdateProfile',views.updateProfile,name='user-update-profile'),
    path('searchPost',views.searchPost,name='searchPost'),
    path('messageOneToOne',views.messageOneToOne,name='messageOneToOne'),
    path('saveMsg',views.saveMsg,name='saveMsg'),
    path('myMsgList',views.myMsgList,name='myMsgList'),
]