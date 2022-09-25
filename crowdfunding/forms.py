from django import forms
from crowdfunding.models import Comment, Project, Category, ProjectImage, Profile
from icecream import ic
import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ClearableFileInput, fields

class CreateNewUser(forms.Form):
    username = forms.CharField(label='Tài khoản',max_length=30)
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Nhập lại mật khẩu', widget=forms.PasswordInput())
    email = forms.EmailField(label='Email')

    def clean_password2(self):
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1==password2 and password1:
                return password2
        raise forms.ValidationError("Mật khẩu nhập lại không hợp trùng khớp.")
    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Tên tài khoản có kí tự đặc biệt')
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('Tài khoản đã tồn tại')
    def save(self):
        User.objects.create_user(username=self.cleaned_data['username'], email=self.cleaned_data['email'], password=self.cleaned_data['password1'])

class CreateNewProject(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            'name',
            'category',
            'description',
            'body',
            'fund',
            'video',
        )
        labels = {
            'name': 'Tên dự án',
            'category': 'Loại dự án',
            'description': 'Mô tả về dự án',
            'body': 'Nội dung giới thiệu về dự án',
            'fund': 'Vốn đầu tư cho dự án ($)',
            'video': 'Video giới thiệu về dự án',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows':4}),
            'body': forms.Textarea(attrs={'rows':10})
        }

class AddingProjectImage(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ('image',)
        widgets = {
            'image': ClearableFileInput(attrs={'multiple': True}),
        }
        labels = {
            'image': 'Hình ảnh về dự án'
        }

class CommentForm(forms.ModelForm):
    def __init__(self, *arg, **kwargs):
        self.author =kwargs.pop('author', None)
        self.project =kwargs.pop('project', None)
        super().__init__(*arg, **kwargs)
    def save(self, commit: bool = True):
        comment = super().save(commit=False)
        comment.author = self.author
        comment.project = self.project
        comment.save()
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {'body': 'Viết bình luận',}

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']
    
def form_validation_error(form):
    msg = ""
    for field in form:
        for error in field.errors:
            msg += "%s: %s \\n" % (field.label if hasattr(field, 'label') else 'Error', error)
    return msg