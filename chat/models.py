'''
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, age, contact, gender, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            age=age,
            contact=contact,
            gender=gender
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, age, contact, gender, password=None):
        user = self.create_user(email, username, age, contact, gender, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    age = models.IntegerField()
    contact = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'age', 'contact', 'gender']

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin

class ChatRoom(models.Model):
    ROOM_TYPE_CHOICES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )
    name = models.CharField(max_length=255, blank=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='private')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_rooms', null=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rooms')

    def __str__(self):
        return self.name or f"Room {self.id}"

    def is_owner(self, user):
        return self.owner == user


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    media = models.FileField(upload_to='chat_media/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"

    def formatted_time(self):
        return self.timestamp.strftime('%I:%M %p, %A')  # e.g., 03:15 PM, Tuesday


'''

# ✅ Updated models.py for full features
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, age, contact, gender, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            age=age,
            contact=contact,
            gender=gender
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, age, contact, gender, password=None):
        user = self.create_user(email, username, age, contact, gender, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    age = models.IntegerField()
    contact = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)  # ✅ Added this

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'age', 'contact', 'gender']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin

class ChatRoom(models.Model):
    ROOM_TYPE_CHOICES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )
    name = models.CharField(max_length=255, blank=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='private')
    members = models.ManyToManyField(CustomUser, related_name='rooms')
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    created_at = models.DateTimeField(default=timezone.now)  # ✅ Creation time

    class Meta:
        unique_together = ('name', 'room_type')

    def __str__(self):
        return self.name or f"Room {self.id}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    media = models.FileField(upload_to='chat_media/', blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
