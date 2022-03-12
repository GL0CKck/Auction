from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import AdvUser, Tip, Product, Category, SubProduct,SuperProduct


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=16, min_length=8,write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = AdvUser
        fields = ('username','email','password','token')
        widgets = {'password':serializers.HiddenField}

    def create(self, validated_data):
        return AdvUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=16, write_only=True)

    email = serializers.EmailField(read_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        username = data.get('username', None)
        password = data.get('password', None)

        if username is None:
            raise serializers.ValidationError(
                'An username is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this username and password was not found.'
            )

        if not user.is_activated:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'token': user.token,
        }


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'is_activated', 'seller', 'buyer')


class ProductDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('name','descriptions','created','author','price','is_active','category','super_product')


class TipSerializer(serializers.ModelSerializer):
    product_name = ProductDetailSerializer()
    author = UserSerializer()

    class Meta:
        model = Tip
        fields = ('product_name', 'value_tip', 'author')



