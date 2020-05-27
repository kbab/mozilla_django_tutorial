from datetime import date
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

import uuid #Required for unique book instances

# Create your models here.

class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)

    # Foriegn Key used because book can have only one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    # ManyToManyField used because genre can contain many books. Book can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    language = models.ForeignKey('Language', 
        on_delete=models.SET_NULL,
        null=True,
        help_text='Select a language for this book'
    )

    def display_genre(self):
        """Create a string for the genre. This is required to display genre in Admin."""

        return ','.join(genre.name for genre in self.genre.all()[:3])

    def __str__(self):
        """String for reprensenting the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book"""
        return reverse('book-detail', args=[str(self.id)])


class BookInstance(models.Model):
    """Model representing a specifice copy of a book (i.e. that can be borrowed from the library)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this physical book across whole library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True, verbose_name="died")

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance"""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'

class Language(models.Model):
    """Language book is written in"""

    name = models.CharField(max_length=100, help_text='Enter language book is written in')

    def __str__(self):
        """Return string representation of this field"""
        return (self.name)

class A(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    permission = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}: {self.permission}"

class B(models.Model):
    A_name = models.ManyToManyField(A)
