from django.urls import path


from . import views

urlpatterns = [
    path('hello', views.hello),
    path('books', views.get_all_books),
    path('authors', views.get_all_authors),
    path('author/<author_id>', views.get_author_by_id),
    path('authors/expensive_books', views.get_authors_with_expensive_books),
    path('books/expensive', views.get_expensive_books),
    path('stores', views.get_all_stores),
    path('store/<store_id>', views.get_store_by_id),
    path('stores/expensive_books', views.get_stores_with_expensive_books),
    path('publishers', views.get_all_publishers),
    path('publishers/<publisher_id>', views.get_publisher_by_id),
    path('publishers/expensive_books', views.get_publishers_with_expensive_books),
    path('books/<book_id>', views.get_book_by_id)
]
