from django.urls import include, path
from rest_framework import routers

from drf_app import views

router = routers.DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'publishers', views.PublisherViewSet)
router.register(r'stores', views.StoreViewSet)
router.register(r'authors', views.AuthorViewSet)

# router.register(r'authors', views.books_list, basename="book_list")

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('books/', views.books_list),
    # path('publishers/', views.publisher_list),
    # path('publishers/<int:publisher_id>', views.publisher_by_id),
    path('books/<int:book_id>', views.book_by_id),
]

urlpatterns += router.urls
print(urlpatterns)
