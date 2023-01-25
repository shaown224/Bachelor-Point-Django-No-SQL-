from django.urls import path
from . import views

urlpatterns =[
    path('job_home/',views.job_home,name = "job_home"),
    path('post_job/',views.post_job,name = "post_job"),
    path('createjob/',views.createjob,name = "createjob"),
    path('Search_job/',views.Search_job,name = "Search_job"),
    path('myPosts/',views.myPosts,name = "myPosts"),
    path('deletePost/',views.deletePost,name = "deletePost"),
]
