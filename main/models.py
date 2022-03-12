from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.db import models
from .utilities import get_timestamp_path
from datetime import timedelta,datetime
import jwt
from django.conf import settings


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('Имя пользователя должно быть указанно')
        if not email:
            raise ValueError('Почта пользователя должна быть указанна')

        email=self.normalize_email(email)
        user=self.model(username=username,email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self,username,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_activated',True)
        extra_fields.setdefault('seller',True)
        extra_fields.setdefault('buyer', True)

        return self._create_user(self,username,email,password,**extra_fields)

    def create_superuser(self,username,email,password,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_activated', True)
        extra_fields.setdefault('seller', True)
        extra_fields.setdefault('buyer', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self._create_user(username, email, password, **extra_fields)


class AdvUser(AbstractUser):
    username = models.CharField(db_index=True, max_length=55, unique=True, verbose_name='Ник-нейм')
    email = models.EmailField(unique=True, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
    seller = models.BooleanField(default=True, verbose_name='Продавец')
    buyer = models.BooleanField(default=False, verbose_name='Покупатель')
    last_request = models.DateTimeField(blank=True, null=True, verbose_name='Последний запрос')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)
    object = UserManager()

    def __str__(self):
        return self.username

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%S'))

        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')

    def delete(self, *args, **kwargs):
        for pp in self.product_set.all():
            pp.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True, verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Сортировка')
    super_category = models.ForeignKey('SuperCategory', on_delete=models.PROTECT, null=True, blank=True,
                                       verbose_name='Надрубрика')


class SuperCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_category__isnull=True)


class SuperCategory(Category):
    objects = SuperCategoryManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class SubCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_category__isnull=False)


class SubCategory(Category):
    object = SubCategoryManager()

    def __str__(self):
        return '%s - %s' % (self.super_category.name, self.name)

    ''' Прокси-модель  объявляется  заданием  в  параметрах  производной  модели  (во  вло
    женном  классе  меtа )  параметра  proxy  со  значением  тrue.  В  базовой  модели  при 
    этом никаких дополнительных параметров записывать не нужно.'''

    class Meta:
        proxy = True
        ordering = ('super_category__order', 'super_category__name', 'order', 'name')
        verbose_name = 'Под Категория'
        verbose_name_plural = 'Под Категории'


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название продукта')
    descriptions = models.TextField(verbose_name='Описание')
    created = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликованно')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Продавец')
    price = models.FloatField(default=0, verbose_name='Цена')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path,verbose_name='Изображение')
    is_active = models.BooleanField(default=True, verbose_name='Выставить на продажу')
    category = models.ForeignKey(SubCategory, on_delete=models.PROTECT, verbose_name='Категория')
    super_product = models.ForeignKey('SuperProduct', on_delete=models.PROTECT, verbose_name='Продукт',
                                      null=True,blank=True)
    deadline = models.DateTimeField(verbose_name='Завершается прием ставок на продукт')

    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created']


class AdditionalImage(models.Model):
    pp = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображения')

    class Meta:
        verbose_name = 'Допольнительная иллюстрация'
        verbose_name_plural = 'Допольнительные иллюстрации'


class SuperProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_product__isnull=True)


class SuperProduct(Product):
    object = SuperProductManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('name', 'created')
        verbose_name = 'Название продукта'
        verbose_name_plural = 'Название продуктов'


class SubProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_product__isnull=False)


class SubProduct(Product):
    object = SubProductManager()

    def __str__(self):
        return '%s - %s' % (self.super_product.name,self.name)

    class Meta:
        proxy = True
        ordering = ('super_product__name','name','price','created')
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Tip(models.Model):
    product_name = models.ForeignKey(Product,on_delete=models.CASCADE,verbose_name='Название продукта')
    value_tip = models.IntegerField(verbose_name='Ваша ставка')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Покупатель')
    time_tip = models.DateTimeField(auto_now_add=True,db_index=True,verbose_name='Время ставки')
    order = models.SmallIntegerField(default=0,db_index=True,verbose_name='Сортировка')

    def __str__(self):
        return str(self.value_tip)

    class Meta:
        verbose_name = 'Ставка'
        verbose_name_plural = 'Ставки'
        ordering = ['-time_tip']