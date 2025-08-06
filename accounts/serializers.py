from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('phone_number', 'first_name', 'last_name', 'password', 'password_confirm', 'location')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Parollar mos kelmaydi.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=str(validated_data['phone_number']),
            **validated_data
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        
        if phone_number and password:
            user = authenticate(username=phone_number, password=password)
            if not user:
                raise serializers.ValidationError('Telefon raqam yoki parol noto\'g\'ri.')
            if not user.is_active:
                raise serializers.ValidationError('Foydalanuvchi hisobi faol emas.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Telefon raqam va parol talab qilinadi.')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'location', 'is_verified', 'date_joined')
        read_only_fields = ('id', 'phone_number', 'is_verified', 'date_joined')