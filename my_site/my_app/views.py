import dataclasses
import logging
import sys

from django.http import HttpResponse, HttpRequest, HttpResponseNotFound
from my_app.models import Book, Store, Author, Publisher
from my_app.utils import query_debugger
from django.db.models import Prefetch, Subquery

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s "
           "[%(name)s:%(funcName)s:%(lineno)s] -> %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
    stream=sys.stdout,
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)
django_logger = logging.getLogger('django.db.backends')
django_logger.setLevel(logging.DEBUG)
django_logger.addHandler(logging.StreamHandler())


@query_debugger(logger)
def _get_all_books():
    """
    Lesson 3: Using select_related for ForeignKey
    """
    # queryset = Book.objects.all()
    # logger.warning(f"SQL: {str(queryset.query)}")
    """
    Один запрос для заполнения всех книг и, выполняя итерацию каждый раз, 
    мы получаем доступ к издателю, который выполняет другой отдельный запрос.
    Давайте изменим запрос с помощью select_related следующим образом и посмотрим, что произойдет.
    """
    queryset = Book.objects.select_related("publisher")
    logger.warning(f"SQL: {str(queryset.query)}")

    return [
        {
            'id': book.id, 'name': book.name,
            # here the additional SQL query is executed to get a publisher name
            'publisher': book.publisher.name
        }
        for book in queryset
    ]


@query_debugger(logger)
def _get_expensive_books():
    queryset = Book.objects.select_related("publisher").filter(price__range=(250, 400))
    logger.warning(f"SQL: {str(queryset.query)}")

    return [
        {
            'id': book.id, 'name': book.name,
            'publisher': book.publisher.name
        }
        for book in queryset
    ]


@query_debugger(logger)
def _get_all_stores():
    """
    Lesson 3: Using prefetch_related for ManyToManyField
    """
    # queryset = Store.objects.all()
    # logger.warning(f"SQL 1: {str(queryset.query)}")
    """
    У нас в базе 10 магазинов и в каждом магазине по 10 книг. 
    Здесь происходит один запрос для выборки всех хранилищ, 
    и во время итерации по каждому хранилищу выполняется другой запрос, 
    когда мы получаем доступ к полю books ManyToMany.
    Давайте уменьшим количество запросов с помощью prefetch_related
    """
    queryset = Store.objects.prefetch_related("books")
    logger.warning(f"SQL: {str(queryset.query)}")

    stores = []
    for store in queryset:
        all_books = store.books.all()
        books = [book.name for book in all_books]
        stores.append({'id': store.id, 'name': store.name, 'books': books})

    return stores


@query_debugger(logger)
def _get_stores_with_expensive_books():
    # queryset = Store.objects.prefetch_related('books')
    # logger.warning(f"SQL 1: {str(queryset.query)}")
    """
    Here we need to use additional Prefetch object
    because in query as *queryset = Store.objects.prefetch_related('books')*
    ALL books related to the existing Stores will be joined and retrieved,
    but then we need to filter these Books by the price range, and this
    will override the first Join

    """
    queryset = Store.objects.prefetch_related(
        Prefetch(
            'books',
            queryset=Book.objects.filter(price__range=(250, 400))
        )
    )

    stores = []
    for store in queryset:
        stores_filtered = store.books.all()
        books = [book.name for book in stores_filtered]
        stores.append({'name': store.name, 'id': store.id, 'books': books })

    return stores


@query_debugger(logger)
def _get_all_authors():
    """
    prefetch_related is used for 'Reversed ManyToOne relation' as for 'ManyToMany field'
    """

    authors = Author.objects.prefetch_related('books')

    authors_with_books = []
    for p in authors:
        books = [book.name for book in p.books.all()]
        authors_with_books.append(
            {'id': p.id, 'first_name': p.first_name, 'last_name': p.last_name, 'books': books}
        )

    return authors_with_books


@query_debugger(logger)
def _get_authors_with_expensive_books():
    queryset = Book.objects.select_related("publisher").prefetch_related("authors").filter(price__range=(250, 400))
    logger.warning(f"SQL: {str(queryset.query)}")

    return [
        {
            'id': book.id, 'name': book.name,
            'publisher': book.publisher.name,
            'authors': book.authors.name,
        }
        for book in queryset
    ]


    # authors = Author.objects.prefetch_related('books')
    # """
    # Делает один запрос и забирает все книги у каждого автора
    # """
    #
    # authors_with_expensive_books = []
    # for p in authors:
    #     books_expensive = Book.objects.filter(price__gte=300)
    #     books = [book.name for book in books_expensive]
    #     authors_with_expensive_books.append(
    #         {'id': p.id, 'first_name': p.first_name, 'last_name': p.last_name, 'books': books}
    #     )
    #
    # return authors_with_expensive_books
    # queryset = Book.objects.select_related("publisher").filter(price__range=(250, 400))
    # logger.warning(f"SQL: {str(queryset.query)}")
    #
    # return [
    #     {
    #         'id': book.id, 'name': book.name,
    #         'publisher': book.publisher.name
    #     }
    #     for book in queryset
    # ]
    # queryset = Author.objects.prefetch_related(
    #     Prefetch(
    #         'books',
    #         queryset=Book.objects.filter(price__gte=200)
    #     )
    # )

    # expensive_books2 = Book.objects.filter(price__gte=200).prefetch_related("authors")
    # #
    # # N queries:
    # # publishers_ids = [book.publisher.id for book in expensive_books]
    # # publishers_with_expensive_books = Publisher.objects.filter(id__in=publishers_ids)
    #
    # # Only one query:
    # authors_with_expensive_books = Author.objects.filter(
    #     id__in=Subquery(expensive_books2.values('authors'))
    # )
    # logger.info(f"SQL: {authors_with_expensive_books.query}")
    #
    # return [item for item in authors_with_expensive_books.values()]

    # authors_with_expensive_books = []
    # for author in queryset:
    #     author_filtered = author.books.all().filter(price__gte=200)
    #     books = [book.name for book in author_filtered]
    #     # if books is None:
    #     #     author.exclude()
    #     authors_with_expensive_books.append({'id': author.id, 'first_name': author.first_name, 'last_name': author.last_name, 'books': books})

    # authors = Author.objects.prefetch_related('books')
    # authors_with_expensive_books = []
    # for p in authors:
    #     books = [book.name for book in p.books.filter(price__range=(250, 400))]
    #     authors_with_expensive_books.append(
    #         {'id': p.id, 'first_name': p.first_name, 'last_name': p.last_name, 'books': books}
    #     )

    # return authors_with_expensive_books


@query_debugger(logger)
def _get_all_publishers():
    """
    prefetch_related is used for 'Reversed ManyToOne relation' as for 'ManyToMany field'
    """
    # Publisher model doesn't have static 'books' field,
    # but Book model has static 'publisher' field as ForeignKey
    # to the Publisher model. In context of the Publisher
    # model the 'books' is dynamic attribute which provides
    # Reverse ManyToOne relation to the Books
    publishers = Publisher.objects.prefetch_related('books')

    publishers_with_books = []
    for p in publishers:
        books = [book.name for book in p.books.all()]
        publishers_with_books.append(
            {'id': p.id, 'name': p.name, 'books': books}
        )

    return publishers_with_books


@query_debugger(django_logger)
def _get_publishers_with_expensive_books():
    """
    Lesson 4: SubQuery example
    """
    expensive_books = Book.objects.filter(price__gte=200)

    # N queries:
    # publishers_ids = [book.publisher.id for book in expensive_books]
    # publishers_with_expensive_books = Publisher.objects.filter(id__in=publishers_ids)

    # Only one query:
    publishers_with_expensive_books = Publisher.objects.filter(
        id__in=Subquery(expensive_books.values('publisher'))
    )
    logger.info(f"SQL: {publishers_with_expensive_books.query}")

    return [item for item in publishers_with_expensive_books.values()]


# ENDPOINTS
def get_all_books(request: HttpRequest) -> HttpResponse:
    books_list = _get_all_books()
    return HttpResponse(f"All Books from Stores:\n {books_list}")


def get_all_stores(request: HttpRequest) -> HttpResponse:
    stores_list = _get_all_stores()
    return HttpResponse(f"All Stores:\n {stores_list}")


def get_stores_with_expensive_books(request: HttpRequest) -> HttpResponse:
    stores_list = _get_stores_with_expensive_books()
    return HttpResponse(f"Stores with expensive books:\n {stores_list}")


def get_all_publishers(request: HttpRequest) -> HttpResponse:
    pubs = _get_all_publishers()
    return HttpResponse(f"All Publishers:\n {pubs}")


def get_publishers_with_expensive_books(request: HttpRequest) -> HttpResponse:
    pubs = _get_publishers_with_expensive_books()
    return HttpResponse(f"Publishers with expensive books:\n {pubs}")


def get_book_by_id(request: HttpRequest, book_id: int) -> HttpResponse:
    if not (book := Book.objects.filter(id=book_id).first()):
        return HttpResponseNotFound(
            f"<h2 style='font-size: 52px; color: red; text-align: center;'> Book by id:{book_id} is not found</h2>"
        )
    authors = book.authors.all()
    authors ="<h2><p>".join([str(a) for a in authors])
    logger.warning(type(authors))
    return HttpResponse(f"<h1>Found book: {book}, authors: <h2><p>{authors}</h1>")


def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"Hello World!")


def get_expensive_books(request: HttpRequest) -> HttpResponse:
    expensive_books_list = _get_expensive_books()
    return HttpResponse(f"All expensive Books from Stores:\n {expensive_books_list}")


def get_all_authors(request: HttpRequest) -> HttpResponse:
    all_authors_list = _get_all_authors()
    return HttpResponse(f"All Book Authors:\n {all_authors_list}")


def get_authors_with_expensive_books(request: HttpRequest) -> HttpResponse:
    authors_with_expensive_books_list = _get_authors_with_expensive_books()
    return HttpResponse(f"Book Authors of expensive books:\n {authors_with_expensive_books_list}")


def get_publisher_by_id(request: HttpRequest, publisher_id: int) -> HttpResponse:
    if not (publisher := Publisher.objects.filter(id=publisher_id).first()):
        return HttpResponseNotFound(
            f"<h2 style='font-size: 52px; color: red; text-align: center;'> Publisher by id:{publisher_id} is not found</h2>"
        )
    # publisher = Publisher.objects.all().select_related('books')
    pub_books = Publisher.objects.filter(pk=publisher_id).prefetch_related('books')
    # publisher_with_books = []
    # for p in publisher:
    #     books = [book.name for book in p.books.all()]
    #     publisher_with_books.append(
    #         {'id': p.id, 'name': p.name, 'books': books}
    #     )
    # publishers = publisher.objects.all()
    # publishers = "<h2><p>".join([str(a) for a in publishers])
    # logger.warning(type(publishers))
    return HttpResponse(f"<h1>Found Publisher: {publisher}, books: {pub_books}authors: <h2><p></h1>")


def get_store_by_id(request: HttpRequest, store_id: int) -> HttpResponse:
    if not (store := Store.objects.filter(id=store_id).first()):
        return HttpResponseNotFound(
            f"<h2 style='font-size: 52px; color: red; text-align: center;'> Store by id:{store_id} is not found</h2>"
        )

    return HttpResponse(f"<h1>Found Store: {store}, authors: <h2><p></h1>")


def get_author_by_id(request: HttpRequest, author_id: int) -> HttpResponse:
    if not (author := Author.objects.filter(id=author_id).first()):
        return HttpResponseNotFound(
            f"<h2 style='font-size: 52px; color: red; text-align: center;'> Author by id:{author_id} is not found</h2>"
        )
    return HttpResponse(f"<h1>Found Author: {author}, authors: <h2><p></h1>")