from django.db.models.aggregates import Sum
from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse
import crowdfunding
from crowdfunding.forms import CreateNewUser, CreateNewProject, AddingProjectImage, CommentForm, ProfileForm, form_validation_error
from crowdfunding.models import Payment, Project, ProjectImage, Comment, Profile, Category
from icecream import ic
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic import ListView, DetailView, View
from django.http import HttpResponseRedirect, request, JsonResponse
from django.contrib import messages
from django.db.models import Q # Search
from django.core.paginator import EmptyPage, Paginator
from django.core.mail import send_mail
import stripe
stripe.api_key = "sk_test_51K1hYGJjxVS8lJWosfpE9hmTvq43hW4is742l7jUAVoiAThQEFYTPT7H8N7MeLa9SivcHL3zAucoUe7BLOiqAnUn00dDsx4ENz"

# Create your views here.
def home_view(request):
    category = Category.objects.all()
    context = {'category':category}
    return render(
        request,
        'home.html',
        context
    )

def create_new_user_view(request):
    category = Category.objects.all()
    if request.method == 'POST':
        form = CreateNewUser(request.POST)
        if form.is_valid():
            form.save()
            ok_url = reverse('create_new_user_ok')
            return redirect(ok_url)
    else:
        form = CreateNewUser()
    return render(
        request,
        'new_user_form.html',
        {
            'category':category,
            'form': form
        }
    )

def create_new_user_ok_view(request):
    category = Category.objects.all()
    return render(
        request,
        'create_user_ok.html',
        {
            'category':category,
        }
    )

def create_new_user_ok2_view(request):
    return render(
        request,
        'create_user_ok2.html'
    )

def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def create_new_project_view(request):
    category = Category.objects.all()
    if request.method == 'POST':
        form = CreateNewProject(request.POST, request.FILES)
        image_form = AddingProjectImage(request.FILES)
        images = request.FILES.getlist('image')
        if form.is_valid() and image_form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            for f in images:
                project_image = ProjectImage(image=f, project=project)
                project_image.save()
            ok_url = reverse('create_new_user_ok2')
            return redirect(ok_url)
    else:
        form = CreateNewProject()
        image_form = AddingProjectImage()
    return render(
        request,
        'create_new_project.html',
        {
            'category':category,
            'form': form,
            'image': image_form
        }
    )
    
def all_project_view(request):
    category = Category.objects.all()
    projects = Project.objects.all().order_by('-date')
    profile = Profile.objects.all()

    p = Paginator(projects, 8)
    page_num = request.GET.get('page',1)
    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)

    return render(request, 'project.html', {'category':category, 'projects':page, 'profile':profile, 'p':range(p.num_pages+1)})

def getCategory(request, pk):
    category = Category.objects.all()
    project_category = Category.objects.get(id=pk)
    projects = Project.objects.filter(category=project_category)
    context = {'category':category, 'projects':projects, 'from':project_category}
    return render(request, 'category.html', context)

def project_detail_view(request,pk):
    category = Category.objects.all()
    project = get_object_or_404(Project,pk=pk)
    fund_support = Payment.objects.filter(project=project).aggregate(Sum('fund_support'))['fund_support__sum']
    if fund_support == None:
        fund_support = 0
    ratio = (fund_support/project.fund)*100
    form = CommentForm()
    if request.method == "POST":
        form = CommentForm(request.POST, author= request.user, project = project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.path)
    return render(request, "project_detail.html", {'category':category,"project":project,"form":form, 'crowdfunded':fund_support, 'ratio': ratio})

class ProfileView(View):
    profile = None

    def dispatch(self, request, *args, **kwargs):
        self.profile, __ = Profile.objects.get_or_create(user=request.user)
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {'profile': self.profile}
        return render(request, 'profile.html', context)
    
    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=self.profile)

        if form.is_valid():
            profile = form.save()
            profile.user.first_name = form.cleaned_data.get('first_name')
            profile.user.last_name  = form.cleaned_data.get('last_name')
            profile.user.email      = form.cleaned_data.get('email')
            profile.user.save()
            
            messages.success(request, 'Profile saved successfully')
        else:
            messages.error(request, form_validation_error(form))
        return redirect('profile')

def search_view(request):
    loop = range(5)
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    projects = Project.objects.filter(
        Q(category__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    category = Category.objects.all()
    context = {'category':category,'projects':projects, 'loop':loop}
    return render(request,'search.html', context)

def payment_view(request, pk):
    category = Category.objects.all()
    project = get_object_or_404(Project,pk=pk)
    profile = Profile.objects.all()
    context = {'category':category, 'profile':profile, 'project':project}
    return render(request,'payment.html', context)

def my_project_view(request):
    category = Category.objects.all()
    projects = Project.objects.filter(user=request.user)
    context = {'category':category, 'projects':projects}
    return render(request, 'my_project.html', context)

def charge(request,pk):
    if request.method == 'POST':
        print('Data:', request.POST)
        amount = int(request.POST['amount'])
        customer = stripe.Customer.create(
            name=request.POST['nickname'],
			email=request.POST['email'],
			source=request.POST['stripeToken']
			)
        charge = stripe.Charge.create(
			customer=customer,
			amount=amount*100,
			currency='usd',
			description="Donation",
			)
        project = get_object_or_404(Project,pk=pk)
        Payment.objects.create(
            project = project,
			user=request.user,
			email=request.POST['email'],
			fund_support=amount,
        )
    return redirect(reverse('success', args=[amount]))


def successMsg(request, args):
    category = Category.objects.all()
    amount = args
    return render(request, 'payment_ok.html', {'category':category,'amount':amount})

def my_donate_view(request):
    category = Category.objects.all()
    payment = Payment.objects.filter(user=request.user).order_by('-date')
    return render(request, 'my_donate.html', {'category':category,'payments':payment})