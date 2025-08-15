
import random
from datetime import timedelta

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import CustomUser, ChatRoom, Message
from .forms import RegisterForm, OTPForm, PasswordSetForm, LoginForm
from django.core.exceptions import ValidationError

from django.http import JsonResponse


User = get_user_model()

# -------------------------
# Helper: Consistent Private Room Naming
# -------------------------
def get_private_room_name(user1, user2):
    return f"chat_{min(user1.username, user2.username)}_{max(user1.username, user2.username)}"

# -------------------------
# Helper: Timestamp Formatting
# -------------------------
def format_timestamp(timestamp):
    now = timezone.localtime(timezone.now())
    timestamp = timezone.localtime(timestamp)
    if timestamp.date() == now.date():
        day_str = "Today"
    elif timestamp.date() == (now - timedelta(days=1)).date():
        day_str = "Yesterday"
    else:
        day_str = timestamp.strftime("%d %b %Y")
    time_str = timestamp.strftime("%I:%M %p")
    return f"{time_str}, {day_str}"

# -------------------------
# Helper: File Validation
# -------------------------
def validate_media(file):
    allowed_types = ["image/jpeg", "image/png", "image/gif", "video/mp4"]
    max_size_mb = 10
    if file.content_type not in allowed_types:
        raise ValidationError("Unsupported file type.")
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File too large. Max size is {max_size_mb}MB.")

# -------------------------
# Views
# -------------------------
def home(request):
    return render(request, 'chat/home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            age = form.cleaned_data.get('age')
            contact = form.cleaned_data.get('contact')
            gender = form.cleaned_data.get('gender')

            # Don’t proceed if email or username already taken
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return redirect('register')
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
                return redirect('register')

            # Stash the user info in session (not DB)
            request.session['pending_user'] = {
                "email": email,
                "username": username,
                "age": age,
                "contact": contact,
                "gender": gender,
            }

            # Send OTP (store in session)
            otp = _generate_otp()
            _store_otp_in_session(request, "reg", email, otp)

            # Email OTP (use console backend in dev if you want)
            send_mail(
                subject='Your Registration OTP',
                message=f'Your OTP is: {otp}. It expires in 30 seconds.',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('verify_otp')
    else:
        form = RegisterForm()

    return render(request, 'chat/register.html', {'form': form})

from datetime import timedelta

def verify_otp_view(request):
    # Must have pending registration
    pending = request.session.get('pending_user')
    reg_email = request.session.get('reg_email')
    if not pending or not reg_email:
        return redirect('register')

    if request.method == 'POST':
        # If you have OTPForm, use it; otherwise read from POST
        try:
            form = OTPForm(request.POST)
            valid = form.is_valid()
            otp_input = form.cleaned_data['otp'] if valid else request.POST.get('otp', '').strip()
        except Exception:
            otp_input = request.POST.get('otp', '').strip()

        ok, err = _otp_is_valid(request, "reg", otp_input, max_age_seconds=30)
        if not ok:
            messages.error(request, err)
            _clear_reg_session(request)
            return redirect('register')

        # Mark verified and continue to set password
        request.session['reg_verified'] = True
        request.session.modified = True
        return redirect('set_password')

    # GET
    return render(request, 'chat/verify_otp.html')

def set_password_view(request):
    pending = request.session.get('pending_user')
    reg_verified = request.session.get('reg_verified', False)
    if not pending or not reg_verified:
        return redirect('register')

    if request.method == 'POST':
        pwd1 = request.POST.get('password1', '').strip()
        pwd2 = request.POST.get('password2', '').strip()

        if not pwd1 or not pwd2:
            messages.error(request, "Please enter your password twice.")
            return render(request, 'chat/set_password.html')

        if pwd1 != pwd2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'chat/set_password.html')

        # ✅ Create the user now
        user = CustomUser(
            email=pending['email'],
            username=pending['username'],
            age=pending['age'],
            contact=pending['contact'],
            gender=pending['gender'],
            is_active=True,
        )
        user.set_password(pwd1)
        user.save()

        # ✅ Clear only after saving
        _clear_reg_session(request)

        messages.success(request, "Registration complete! Please log in.")
        return redirect('login')

    return render(request, 'chat/set_password.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()
    return render(request, 'chat/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    rooms = ChatRoom.objects.filter(room_type="group")
    return render(request, "chat/dashboard.html", {
        "users": users,
        "rooms": rooms
    })

@login_required
def chat_with(request, username):
    other_user = get_object_or_404(CustomUser, username=username)
    room_name = get_private_room_name(request.user, other_user)

    # Only look for PRIVATE rooms
    room, created = ChatRoom.objects.get_or_create(
        name=room_name,
        room_type="private",  # Ensures it's a private room
        defaults={"creator": request.user}
    )

    if created:
        room.members.set([request.user, other_user])

    messages_qs = Message.objects.filter(room=room).order_by("timestamp")
    for msg in messages_qs:
        msg.formatted_time = format_timestamp(msg.timestamp)

    return render(request, "chat/chat.html", {
        "other_user": other_user,
        "messages": messages_qs
    })


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type="group")
    messages_qs = Message.objects.filter(room=room).order_by("timestamp")
    for msg in messages_qs:
        msg.formatted_time = format_timestamp(msg.timestamp)
    group_created_time = format_timestamp(room.created_at)

    return render(request, "chat/chat_room.html", {
        "room": room,
        "messages": messages_qs,
        "group_created_time": group_created_time  # pass to template

    })



from django.shortcuts import get_object_or_404

@login_required
def create_room(request):
    if request.method == "POST":
        room_name = request.POST.get("name")
        if not room_name:
            messages.error(request, "Room name is required.")
            return redirect("create_room")

        # Check if a room with same name and type already exists
        existing_room = ChatRoom.objects.filter(name=room_name, room_type="group").first()
        if existing_room:
            messages.error(request, f"A group room named '{room_name}' already exists.")
            return redirect("create_room")

        # Create the group room
        room = ChatRoom.objects.create(
            name=room_name,
            room_type="group",
            creator=request.user
        )
        room.members.add(request.user)

        messages.success(request, f"Group '{room.name}' created successfully.")
        return redirect("chat_room", room_id=room.id)

    return render(request, "chat/create_room.html")


@login_required
def manage_group(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type="group", creator=request.user)
    members = room.members.all()
    all_users = CustomUser.objects.exclude(id__in=members.values_list("id", flat=True))

    if request.method == "POST":
        user_ids = request.POST.getlist("members")
        for user_id in user_ids:
            user = CustomUser.objects.get(id=user_id)
            room.members.add(user)
        messages.success(request, "Members added successfully.")
        return redirect("manage_group", room_id=room.id)

    return render(request, "chat/manage_group.html", {
        "room": room,
        "members": members,
        "all_users": all_users
    })

@login_required
def remove_member(request, room_id, user_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    user = get_object_or_404(CustomUser, id=user_id)
    if request.user == room.creator and user in room.members.all():
        room.members.remove(user)
        messages.success(request, f"{user.username} removed from group.")
    return redirect('manage_group', room_id=room.id)

@login_required
def delete_group(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, room_type="group", creator=request.user)
    if request.method == "POST":
        room.delete()
        messages.success(request, "Group deleted successfully.")
    return redirect("dashboard")

@login_required
def add_members(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user != room.creator:
        return redirect('dashboard')

    if request.method == 'POST':
        user_ids = request.POST.getlist('users')
        for uid in user_ids:
            user = CustomUser.objects.get(id=uid)
            room.members.add(user)
    return redirect('manage_group', room_id=room.id)

# -------------------------
# Media Uploads
# -------------------------

@login_required
@csrf_exempt
def upload_media(request, username):
    if request.method == 'POST' and request.FILES.get('media'):
        receiver = get_object_or_404(CustomUser, username=username)
        room_name = f"chat_{min(request.user.username, receiver.username)}_{max(request.user.username, receiver.username)}"
        room = ChatRoom.objects.get(name=room_name)
        file = request.FILES['media']
        msg = Message.objects.create(sender=request.user, room=room, media=file)

        # Broadcast media via WebSocket
        from channels.layers import get_channel_layer
        import asyncio
        channel_layer = get_channel_layer()
        asyncio.run(channel_layer.group_send(
            f"private_chat_{room_name}",
            {
                "type": "chat.message",
                "message": "",
                "media_url": msg.media.url,
                "sender": request.user.username,
                "timestamp": format_timestamp(msg.timestamp)
            }
        ))

        return redirect('chat_with', username=receiver.username)
    return redirect('dashboard')


@login_required
@csrf_exempt
def upload_media_room(request, room_id):
    if request.method == 'POST' and request.FILES.get('media'):
        room = get_object_or_404(ChatRoom, id=room_id)
        file = request.FILES['media']
        msg = Message.objects.create(sender=request.user, room=room, media=file)

        # Broadcast
        from channels.layers import get_channel_layer
        import asyncio
        channel_layer = get_channel_layer()
        asyncio.run(channel_layer.group_send(
            f"group_chat_{room.id}",
            {
                "type": "chat.message",
                "message": "",
                "media_url": msg.media.url,
                "sender": request.user.username,
                "timestamp": format_timestamp(msg.timestamp)
            }
        ))

        return redirect('chat_room', room_id=room.id)
    return redirect('dashboard')

'''
@login_required
def delete_message(request, msg_id):
    msg = get_object_or_404(Message, id=msg_id)
    if msg.sender == request.user:
        msg.delete()
        messages.success(request, "Message deleted.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
'''

from channels.layers import get_channel_layer
import asyncio

# ... your existing imports and code remain here ...

@login_required
@csrf_exempt
def delete_message(request, message_id):
    msg = get_object_or_404(Message, id=message_id)

    if msg.sender != request.user:
        return JsonResponse({'ok': False, 'error': 'Not allowed'}, status=403)

    msg.is_deleted = True
    msg.content = "[message deleted]"
    if msg.media:
        msg.media.delete(save=False)
        msg.media = None
    msg.save()

    # Broadcast deletion
    channel_layer = get_channel_layer()
    if msg.room.room_type == "private":
        room_group_name = f"private_chat_{msg.room.name}"
    else:
        room_group_name = f"group_chat_{msg.room.id}"

    asyncio.run(channel_layer.group_send(
        room_group_name,
        {
            "type": "delete_message_event",
            "message_id": msg.id
        }
    ))

    return JsonResponse({'ok': True, 'message_id': msg.id})




@login_required
def room_list(request):
    rooms = ChatRoom.objects.filter(room_type="group")
    return render(request, "chat/room_list.html", {"rooms": rooms})


#----------------------------------------------------------------

# ----- OTP helpers -----

def _generate_otp():
    return f"{random.randint(0, 999999):06d}"

def _store_otp_in_session(request, prefix, email, otp):
    request.session[f"{prefix}_email"] = email
    request.session[f"{prefix}_otp"] = otp
    request.session[f"{prefix}_otp_created"] = timezone.now().timestamp()
    request.session.modified = True

def _otp_is_valid(request, prefix, otp_input, max_age_seconds=30):
    otp = request.session.get(f"{prefix}_otp")
    created_ts = request.session.get(f"{prefix}_otp_created")
    if not otp or not created_ts:
        return False, "OTP not found. Please start again."

    # expiry
    age = timezone.now().timestamp() - float(created_ts)
    if age > max_age_seconds:
        return False, "OTP expired. Please request a new one."

    if otp_input != otp:
        return False, "Invalid OTP."

    return True, ""

def _clear_reg_session(request):
    for key in ["reg_email", "reg_otp", "reg_otp_created", "pending_user", "reg_verified"]:
        request.session.pop(key, None)
    request.session.modified = True

def _clear_reset_session(request):
    for key in ["reset_email", "reset_otp", "reset_otp_created", "reset_verified"]:
        request.session.pop(key, None)
    request.session.modified = True

from django.conf import settings

def _send_otp_email(email, subject, otp):
    send_mail(
        subject=subject,
        message=f'Your OTP is: {otp}. It expires in 30 seconds.',
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
        recipient_list=[email],
        fail_silently=False,
    )

def resend_otp(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)

    kind = request.POST.get('kind')  # 'reg' or 'reset'
    if kind not in ('reg', 'reset'):
        return JsonResponse({'ok': False, 'error': 'Invalid kind'}, status=400)

    if kind == 'reg':
        pending = request.session.get('pending_user')
        email = request.session.get('reg_email')
        if not pending or not email:
            return JsonResponse({'ok': False, 'error': 'No pending registration'}, status=400)

        otp = _generate_otp()
        _store_otp_in_session(request, 'reg', email, otp)
        _send_otp_email(email, 'Your Registration OTP (Resent)', otp)
        return JsonResponse({'ok': True, 'seconds': 30})

    # kind == 'reset'
    email = request.session.get('reset_email')
    if not email:
        return JsonResponse({'ok': False, 'error': 'No reset flow in progress'}, status=400)

    otp = _generate_otp()
    _store_otp_in_session(request, 'reset', email, otp)
    _send_otp_email(email, 'Your Password Reset OTP (Resent)', otp)
    return JsonResponse({'ok': True, 'seconds': 30})


#------------------Forgot-Password with OTP------------------------------------

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, "Please enter your email.")
            return redirect('forgot_password')

        try:
            CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return redirect('forgot_password')

        otp = _generate_otp()
        _store_otp_in_session(request, "reset", email, otp)

        send_mail(
            subject='Your Password Reset OTP',
            message=f'Your OTP is: {otp}. It expires in 30 seconds.',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('verify_reset_otp')

    return render(request, 'chat/forgot_password.html')

def verify_reset_otp_view(request):
    reset_email = request.session.get('reset_email')
    if not reset_email:
        return redirect('forgot_password')

    if request.method == 'POST':
        try:
            form = OTPForm(request.POST)
            valid = form.is_valid()
            otp_input = form.cleaned_data['otp'] if valid else request.POST.get('otp', '').strip()
        except Exception:
            otp_input = request.POST.get('otp', '').strip()

        ok, err = _otp_is_valid(request, "reset", otp_input, max_age_seconds=30)
        if not ok:
            messages.error(request, err)
            _clear_reset_session(request)
            return redirect('forgot_password')

        request.session['reset_verified'] = True
        request.session.modified = True
        return redirect('set_new_password')

    return render(request, 'chat/verify_reset_otp.html')



def set_new_password_view(request):
    reset_email = request.session.get('reset_email')
    reset_verified = request.session.get('reset_verified', False)
    if not reset_email or not reset_verified:
        return redirect('forgot_password')

    if request.method == 'POST':
        pwd1 = request.POST.get('password1', '').strip()
        pwd2 = request.POST.get('password2', '').strip()

        if not pwd1 or not pwd2:
            messages.error(request, "Please enter your password twice.")
            return redirect('set_new_password')
        if pwd1 != pwd2:
            messages.error(request, "Passwords do not match.")
            return redirect('set_new_password')

        user = get_object_or_404(CustomUser, email=reset_email)
        user.set_password(pwd1)
        user.save()

        _clear_reset_session(request)
        messages.success(request, "Password updated! Please log in.")
        return redirect('login')

    return render(request, 'chat/set_new_password.html')



