from django.urls import path
from . import views

urlpatterns =[
    
   path('login/',views.login,name="sp-login"),
   #path('singup/',views.singup,name="sp-singup"),
   path('authentication/',views.authentication, name="authentication"),
   path('registration',views.registration,name="sp-registration"),
   path('logout',views.logout,name="sp-logout"),
   path('update-sp-registration',views.update_registration,name="update-sp-registration"),
   path('user-side',views.user_side,name="user-side"),
   path('search',views.search,name="search")

]