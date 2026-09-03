from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import EmployeeProfile, Attendance


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    name = serializers.CharField(write_only=True)

    phone = serializers.CharField(
        write_only=True, 
        validators=
        [ RegexValidator
            ( regex=r'^[6-9]\d{9}$',
              message='Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.' 
            ) 

        ]
    )

    city = serializers.CharField(write_only=True)

    email = serializers.EmailField(
        Required = True
    )

    class Meta:
        model = User

        fields = [
            'id',
            'username',
            'email',
            'password',
            'name',
            'phone',
            'city'
        ]

    def validate_email(self, value): 
        if User.objects.filter(email=value).exists(): 
            raise serializers.ValidationError( "Email already exists." ) 
        return value 

    def validate_password(self, value): 
        if len(value) < 8: 
            raise serializers.ValidationError( "Password must be at least 8 characters." ) 
            return value

    def create(self, validated_data):

        name = validated_data.pop('name')
        phone = validated_data.pop('phone')
        city = validated_data.pop('city')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=password
        )

        EmployeeProfile.objects.create(
            user=user,
            name=name,
            phone=phone,
            city=city
        )

        return user


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        username = data.get("username")
        password = data.get("password")

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled"
            )

        data["user"] = user

        return data


class UpdateUserSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        source='employeeprofile.name'
    )

    phone = serializers.CharField(
        source='employeeprofile.phone',
        validators=
        [ RegexValidator
            ( regex=r'^[6-9]\d{9}$', 
                message='Phone number must be exactly 10 digits and start with 6, 7, 8, or 9.' 
            ) 
        ]
    )

    city = serializers.CharField(
        source='employeeprofile.city'
    )

    email = serializers.EmailField()

    class Meta:

        model = User

        fields = [
            'username',
            'email',
            'name',
            'phone',
            'city'
        ]

    def validate_email(self, value): 
        user = self.instance 
        if User.objects.filter( email=value ).exclude( id=user.id ).exists(): 
            raise serializers.ValidationError( "Email already exists." ) 
        return value

    def update(self, instance, validated_data):

        profile_data = validated_data.pop(
            'employeeprofile',
            {}
        )

        instance.username = validated_data.get(
            'username',
            instance.username
        )

        instance.email = validated_data.get(
            'email',
            instance.email
        )

        instance.save()

        profile = instance.employeeprofile

        profile.name = profile_data.get(
            'name',
            profile.name
        )

        profile.phone = profile_data.get(
            'phone',
            profile.phone
        )

        profile.city = profile_data.get(
            'city',
            profile.city
        )

        profile.save()

        return instance


class AttendanceSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    name = serializers.CharField(
        source='user.employeeprofile.name',
        read_only=True
    )

    class Meta:

        model = Attendance

        fields = [
            'id',
            'username',
            'name',
            'date',
            'punch_in',
            'punch_out'
        ]