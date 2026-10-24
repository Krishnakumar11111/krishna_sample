from django.urls import path
from bookings import views

urlpatterns = [
    path('book-demo/', views.book_demo_page, name='book_demo_page'),
    path('api/book-demo/', views.book_demo_api, name='book_demo_api'),
]