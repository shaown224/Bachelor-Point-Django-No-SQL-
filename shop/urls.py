from django.urls import path
from . import views

urlpatterns =[
 path('savePost/',views.savePost,name="savePost"),
 path('shopHome/',views.shopHome,name="shopHome"),
 path('addComment/',views.addComment,name="addComment"),
 path('seeAllPost/',views.seeAllPost,name="seeAllPost"),
 path('showPostCategory/',views.showPostCategory,name="showPostCategory"),
 path('myPosts/',views.myPosts,name="myPosts"),
 path('deletePost/',views.deletePost,name="deletePost"),
 path('search_product/',views.search_product,name="search_product"),
]
