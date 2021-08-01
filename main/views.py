from django.shortcuts import render
from .models import Product, AdvUser, SubCategory, SubProduct, SuperProduct,Tip
from django.views.generic.edit import UpdateView,CreateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect
from .forms import RegisterUserForm, ChangeUserInfoForm, ProductForm, AIFormset, SubProductForm,ProductFormAdmin, TipUserForm
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer

class RegistrationAPIView(APIView):
    """
    Registers a new user.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        """
        Creates a new User object.
        Username, email, and password are required.
        Returns a JSON web token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'token': serializer.data.get('token', None),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    """
    Logs in an existing user.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """
        Checks is user exists.
        Email and password are required.
        Returns a JSON web token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


def index(request):
    pps=SubProduct.objects.filter(is_active=True)
    context = {'pps': pps}
    return render(request, 'index/index.html', context)


def by_category(request,pk):
    category = get_object_or_404(SubCategory,pk=pk)
    pps = Product.objects.filter(is_active=True,category=pk)
    context={'category':category,'pps':pps}
    return render(request,'category_product/by_category.html',context)


class PpLoginView(LoginView):
    template_name = 'user/login.html'
    success_url = reverse_lazy('main:profile')


class PpLogoutView(LogoutView,LoginRequiredMixin):
    template_name = 'user/logout.html'


class PpRegisterView(CreateView):
    model = AdvUser
    template_name = 'user/register.html'
    success_url = reverse_lazy('main:register_done')
    form_class = RegisterUserForm


class RegisterUserDone(TemplateView):
    template_name = 'user/register_done.html'


@login_required()
def profile(request):
    pps=Product.objects.filter(author=request.user.pk)
    context={'pps':pps}
    return render(request,'user/profile.html',context)


class ChangeUserInfo(SuccessMessageMixin,LoginRequiredMixin,UpdateView):
    model = AdvUser
    template_name = 'user/change_user.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request,*args,**kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset=self.get_queryset()
        return get_object_or_404(queryset,pk=self.user_id)


class DeleteUser(DeleteView,LoginRequiredMixin):
    model = AdvUser
    template_name = 'user/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request,messages.SUCCESS,'Пользователь успешно удален')
        return super().post(request,*args,**kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset=self.get_queryset()
        return get_object_or_404(queryset,pk=self.user_id)


def detail(request,category_pk,pk):
    pp=get_object_or_404(Product,pk=pk)
    ais=pp.additionalimage_set.all()
    tips=Tip.objects.filter(product_name=pk)
    if request.user.is_authenticated:
        if request.method == 'POST':
            form=TipUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request,messages.SUCCESS,'Ставка успешно сделана')

        else:
            form=TipUserForm(initial={'author':request.user.pk,'product_name':pp.pk})
        context={'pp':pp,'ais':ais,'tips':tips,'form':form}
        return render(request,'product/detail_product.html',context)
    else:
        messages.add_message(request,messages.ERROR,'Вы должны авторизироваться!')

@login_required()
def profile_pp_add(request):
    user = request.user
    if user.has_perm('auth.change_user'):
        if request.method == 'POST':
            form = ProductFormAdmin(request.POST,request.FILES)
            if form.is_valid():
                pp=form.save()
                formset=AIFormset(request.POST,request.FILES,instance=pp)
                if formset.is_valid():
                    formset.save()
                    messages.add_message(request,messages.SUCCESS,'Объявление успешно добавлено')
                    return redirect('main:profile')
        else:
            form = ProductFormAdmin(initial={'author':request.user.pk})
            formset = AIFormset()
        context={'form':form,'formset':formset}
        return render(request,'product/create_product.html',context)
    else:
        if request.method == 'POST':
            form = ProductForm(request.POST,request.FILES)
            if form.is_valid():
                pp=form.save()
                formset=AIFormset(request.POST,request.FILES,instance=pp)
                if formset.is_valid():
                    formset.save()
                    messages.add_message(request,messages.SUCCESS,'Объявление успешно добавлено')
                    return redirect('main:profile')
        else:
            form = ProductForm(initial={'author':request.user.pk})
            formset = AIFormset()
        context={'form':form,'formset':formset}
        return render(request,'product/create_product.html',context)


@login_required()
def profile_pp_change(request,pk):
    pp = get_object_or_404(Product,pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST,instance=pp)
        if form.is_valid():
            pp=form.save()
            messages.add_message(request,messages.SUCCESS,'Продукт успешно изменен')
            return redirect('main:profile')

    else:
        form=ProductForm(instance=pp)
        context={'form':form}
        return render(request,'product/change_product.html',context)


@login_required()
def profile_pp_delete(request,pk):
    pp=get_object_or_404(Product,pk=pk)
    if request.method == 'POST':
        pp.delete()
        messages.add_message(request,messages.SUCCESS,'Объявление успешно удалено')
        return redirect('main:profile')
    else:
        context={'pp':pp}
        return render(request,'product/delete_product.html',context)


@login_required()
def user_tips(request):
    tips=Tip.objects.filter(author=request.user.pk)
    context={'tips':tips}
    return render(request,'tip/all_my_tips.html',context)


@login_required()
def user_tips_delete(request,pk):
    tips=get_object_or_404(Tip,pk=pk)
    if request.method == 'POST':
        tips.delete()
        messages.add_message(request,messages.SUCCESS,'Ставка удаленна')
        return redirect('main:user_tips')
    else:
        context={'tips':tips}
        return render(request,'tip/delete_tip.html',context)