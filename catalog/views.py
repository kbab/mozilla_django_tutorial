import datetime

from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.urls import reverse, reverse_lazy

# Create your views here.

from catalog.models import Book, Author, BookInstance, Genre
from catalog.forms import RenewBookForm

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # Number of visites to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Get count of books by genre
    num_genres = Genre.objects.all().count()
    book_instances_by_genre = {}
    for genre in Genre.objects.all():
        books_by_genre = Book.objects.filter(genre=genre)
        for b in books_by_genre:
            book_instances_by_genre[genre.name] = BookInstance.objects.filter(book=b).count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'book_instances_by_genre': book_instances_by_genre,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on load to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class AllLoanedBooksListView(LoginRequiredMixin, generic.ListView):
    """List all books currently on loan - restricted to staff"""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_books_on_loan.html'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we 
            # just write it to the model due_data
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})


    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renewal_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '12/12/2099'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language',]

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.can_mark_returned'



from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print("Received form posted")
        print(request.FILES['file'])
        if form.is_valid():
            # Do save here
            print("Do save here")
            return HttpResponseRedirect('/') #url to success page
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form}) # upload.html is your template for uploading the file
