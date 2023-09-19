from django.db import models

# Create your models here.


class Author(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name}, {self.last_name}, [email: {self.email}]"


class Publisher(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=300)
    price = models.IntegerField(default=0)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name="books")
    authors = models.ManyToManyField(Author, related_name="books")

    class Meta:
        default_related_name = 'books'

    def __str__(self):
        return f"{self.name}, {self.price} $, [publisher: {self.publisher}], authors: {self.authors}"


class Store(models.Model):
    name = models.CharField(max_length=300)
    books = models.ManyToManyField(Book)

    class Meta:
        default_related_name = 'stores'

    def __str__(self):
        return self.name
