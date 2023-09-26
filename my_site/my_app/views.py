import dataclasses
import logging
import sys
import result

from django.db.models import Prefetch, Subquery
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from my_app.forms import UserForm, PublisherForm, BookForm
from my_app.models import Author, Book, Publisher, Store, User
from my_app.utils import query_debugger

from django.views.decorators.cache import cache_page

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
    queryset = (
        Book.objects.select_related("publisher")
                    .prefetch_related('authors')
    )
    logger.warning(f"SQL: {str(queryset.query)}")

    return [
        {
            'id': book.id, 'name': book.name,
            # here the additional SQL query is executed to get a publisher name
            'publisher': book.publisher.name,
            'authors': ", ".join([str(a) for a in book.authors.all()])
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


@query_debugger(logger)
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
    # return HttpResponse(f"All Books from Stores:\n {books_list}")
    return render(
        request,
        template_name="books.html",
        context={
            'books': books_list
        }
    )

# def get_first_three_books(request: HttpRequest) -> HttpResponse:    #first version of func
#     match _get_all_books()[:3]:
#         case book1, book2, book3:
#             context = {
#                 'book1': book1,
#                 'book2': book2,
#                 'book3': book3,
#             }
#         case _:
#             context = {
#                 'book1': None,
#                 'book2': None,
#                 'book3': None,
#             }
#
#     return render(
#         request,
#         template_name="books.html",
#         context=context
#     )


@cache_page(60)
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
    return render(request, template_name="index.html")


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
    author_books = Author.objects.prefetch_related('books')
    author_cur_books = []
    for b in author_books:
        books = [book.name for book in b.books.all()]
        author_cur_books.append(
            {'id': b.id, 'books': books}
        )
        return b
    return HttpResponse(f"<h1>Found Author: {author}, books: {author_books} <h2><p></h1>")



# ---------- Lesson DJANGO TEMPLATES ----------- #


def hello_v2(request: HttpRequest) -> HttpResponse:
    """
    Lesson "Django Templates"
    """
    return render(request, "index.html")


def get_first_three_books(request: HttpRequest) -> HttpResponse:
    """
    Lesson "Django Templates"
    """
    keys = ('book1', 'book2', 'book3')
    not_found = 'Not Found'

    match _get_all_books()[:3]:
        case book1, book2, book3:
            context = dict(zip(keys, (book1, book2, book3)))
        case book1, book2:
            context = dict(zip(keys, (book1, book2, not_found)))
        case book1, *_:
            context = dict(zip(keys, (book1, not_found, not_found)))
        case _:
            context = dict.fromkeys(keys, not_found)

    return render(
        request,
        "books1.html",
        context=context
    )


def get_all_books_v2(request: HttpRequest) -> HttpResponse:
    """
    Lesson "Django Templates"
    """
    books_list = _get_all_books()

    return render(
        request,
        "books2.html",
        context={
            'books': books_list
        }
    )


# ---------- Lesson DJANGO TEMPLATES: HOMEWORK ----------- #

@query_debugger(logger)
def _get_only_books_with_authors():
    """
    Lesson "Django Templates" Homework
    """
    queryset = (
        Book.objects.select_related("publisher")
                    .prefetch_related('authors')
                    .filter(authors__isnull=False)
    )
    logger.warning(f"SQL: {str(queryset.query)}")

    return [
        {
            'id': book.id, 'name': book.name,
            # here the additional SQL query is executed to get a publisher name
            'publisher': book.publisher.name,
            'authors': ", ".join([str(a) for a in book.authors.all()])
        }
        for book in queryset
    ]
    pass


def get_only_books_with_authors(request: HttpRequest) -> HttpResponse:
    books_with_authors_list = _get_only_books_with_authors()
    # return HttpResponse(f"All Books from Stores:\n {books_list}")
    return render(
        request,
        template_name="books3.html",
        context={
            'books': books_with_authors_list
        }
    )


def get_user_form(request: HttpRequest) -> HttpResponse:
    form = UserForm()
    return render(
        request,
        "user_form.html",
        context={"form": form}
    )


def get_publisher_form(request: HttpRequest) -> HttpResponse:
    form = PublisherForm()
    return render(
        request,
        "publisher_form.html",
        context={"form": form}
    )


def get_book_form(request: HttpRequest) -> HttpResponse:
    form = BookForm()
    return render(
        request,
        "book_form.html",
        context={"form": form}
    )


def _add_user(user_dict: dict):

    return User.objects.create(
        name=user_dict.get('name') or 'default_name',
        age=user_dict.get('age') or 18,
        gender=user_dict.get('gender') or 'female',
        nationality=user_dict.get('nationality') or 'belarus'
    )


def _add_book(book_dict: dict):

    return Book.objects.create(
        name=book_dict.get('name') or 'default_name',
        price=book_dict.get('price') or 250,
        publisher=book_dict.get('publisher') or 'default_publisher'
    )


def _add_publisher(pub_name: dict):

    return Publisher.objects.create(
        name=pub_name.get('name') or 'default_name'
    )


def add_publisher(request: HttpRequest) -> HttpResponse:
    rq_data = request.POST
    pub_name = rq_data.get("name", "default_name")
    pub_data = {"name": pub_name}

    if Publisher.objects.filter(name=pub_name).exists():
        return HttpResponse(f"Publisher with name {pub_name} already exists.")

    publisher = _add_publisher(pub_data)
    return HttpResponse(f"Publisher: {publisher}")


def add_user(request: HttpRequest) -> HttpResponse:
    rq_data = request.POST
    user_data = {
        "name": rq_data.get("name"),
        "age": rq_data.get("age"),
        "gender": rq_data.get("gender"),
        "nationality": rq_data.get("nationality")
    }
    user = _add_user(user_data)

    return HttpResponse(f"User: {user}")


def add_book(request: HttpRequest) -> HttpResponse:
    rq_data = request.POST
    book_data = {
        "name": rq_data.get("name"),
        "price": rq_data.get("price"),
        # "publisher": rq_data.get("publisher")
    }
    pub_name = rq_data.get("publisher")

    if pub := Publisher.objects.filter(name=rq_data.get("publisher")):
        book_data['publisher'] = pub.first()
    else:
        book_data['publisher'] = _add_publisher({'name': pub_name})

    book = _add_book(book_data)
    return HttpResponse(f"The Book: {book}")
