import io
import requests

from drf_app.models import Book, Publisher, Author
from drf_app.serializers import BookSerializer

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

data = {
    'name': 'ApiBook1',
    'price': 100,

}

publisher = Publisher.objects.last()
book1_data = dict(name='ApiBook1', price=10500, publisher=publisher)
pub = Publisher.objects.create(name="New_Pub")
book = Book.objects.create(name="New_Book", publisher="New_Pub", price=250, authors="Conan Doyle")


book = Book.objects.create(name="New_Book", publisher=pub, price=250)
last_book = Book.objects.last()
last_book


book1 = Book.objects.last()

serializer = BookSerializer(book1)
data = serializer.data


import io

content = JSONRenderer().render(data)
content

content.decode('utf-8')
# '{"id":101,"name":"New_Book","price":250,"publisher":"New_Pub","authors":[{"id":1,"first_name":"Author_1_name","last_name":"Author_1_surname","email":"author.1@gmail.com"},{"id":5,"first_name":"Author_5_name","last_name":"Author_5_surname","email":"author.5@gmail.com"}]}'

import json
data = json.loads(content.decode('utf-8'))
data
# {'id': 101, 'name': 'New_Book', 'price': 250, 'publisher': 'New_Pub', 'authors': [{'id': 1, 'first_name': 'Author_1_name', 'last_name': 'Author_1_surname', 'email': 'author.1@gmail.com'}, {'id': 5, 'first_name': 'Author_5_name', 'last_name': 'Author_5_surname', 'email': 'author.5@gmail.com'}]}


stream = io.BytesIO(content)

#Need to make seek 0
data = JSONParser().parse(stream)
data
# {'id': 101, 'name': 'New_Book', 'price': 250, 'publisher': 'New_Pub', 'authors': [{'id': 1, 'first_name': 'Author_1_name', 'last_name': 'Author_1_surname', 'email': 'author.1@gmail.com'}, {'id': 5, 'first_name': 'Author_5_name', 'last_name': 'Author_5_surname', 'email': 'author.5@gmail.com'}]}
# >>> stream.read()

serializer = BookSerializer()
serializer.create({'id': 101, 'name': 'New_Book', 'price': 250, 'publisher': pub})
serializer.update(book1, {'price': 1, 'publisher': pub})


publisher = Publisher.objects.last()
book1_data = dict(name='ApiBook1', price=105, publisher=publisher)


last_publisher_id = Publisher.objects.last().id
pub_new_data = dict(id=last_publisher_id + 1, name="ApiBook1")



url = "http://127.0.0.1:8000/drf_app/publishers/"


pub_new_data2 = {'id': 15, 'name': 'ApiPublisher2'}
pub_new_data3 = {'id': 16, 'name': 'ApiPublisher3'}


data = [pub_new_data2, pub_new_data3]


resp = requests.post(url=url, json=data)