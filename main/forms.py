from django.contrib import messages
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django import forms
from .models import Product, SubCategory, SuperCategory,SuperProduct,SubProduct, AdvUser, AdditionalImage, Tip
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
import jwt
from datetime import datetime
from datetime import timedelta
from django.conf import settings


AIFormset = inlineformset_factory(Product,AdditionalImage,fields='__all__')


class SubProductForm(forms.ModelForm):
    super_product = forms.ModelChoiceField(queryset=SuperProduct.object.all(),
                                           empty_label=None,
                                           required=True,
                                           label='Продукт')

    class Meta:
        model = SubProduct
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}


class SubCategoryForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(queryset=SuperCategory.objects.all(),
                                          empty_label=None,
                                          required=True,
                                          label='Категория')

    class Meta:
        model = SubCategory
        fields = '__all__'


class ProductFormAdmin(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}


class ProductForm(forms.ModelForm):
    super_product = forms.ModelChoiceField(queryset=SuperProduct.object.all(),
                                           empty_label=None,
                                           required=True,
                                           label='Продукт')
    deadline = forms.DateTimeField(required=True)

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}


class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True,label='Адресс Электронной Почты')
    password1 = forms.CharField(label='Password',widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Повторите пароль',widget=forms.PasswordInput,help_text='Повторите ваш пароль!!!')

    @property
    def token(self):
        return self._generation_token_jwt()

    def _generation_token_jwt(self):
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id':self.pk,
            'exp':int(dt.strftime('%S'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password1':ValidationError('Пароли не совпадают',code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        user.is_activated = True

        if commit:
            user.save()
        return user

    class Meta:
        model = AdvUser
        fields = ('username','email','password1','password2','first_name','last_name','seller','buyer')


class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True,label='Адресс электронной почты')

    class Meta:
        model = AdvUser
        fields = ('username','email','first_name','last_name','seller','buyer')


class TipUserForm(forms.ModelForm):

    class Meta:
        model = Tip
        fields = ('product_name','value_tip','author')
        widgets = {'author': forms.HiddenInput}