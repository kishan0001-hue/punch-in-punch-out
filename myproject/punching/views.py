from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework.decorators import (
    api_view,
    permission_classes
)

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Attendance

from .serializer import (
    UserSerializer,
    LoginSerializer,
    UpdateUserSerializer,
    AttendanceSerializer
)


# =========================================
# CREATE USER
# =========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):

    serializer = UserSerializer(
        data=request.data
    )

    if serializer.is_valid():

        user = serializer.save()

        return Response(
            {
                "message": "User created successfully",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================================
# LOGIN
# =========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):

    serializer = LoginSerializer(
        data=request.data
    )

    if not serializer.is_valid():

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    user = serializer.validated_data['user']

    refresh = RefreshToken.for_user(user)

    access_token = refresh.access_token

    return Response(
        {
            "message": "Login successful",

            "user_id": user.id,

            "username": user.username,

            "access": str(access_token),

            "refresh": str(refresh)
        }
    )


# =========================================
# REFRESH ACCESS TOKEN
# =========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):

    refresh_token_value = request.data.get(
        'refresh'
    )

    if not refresh_token_value:

        return Response(
            {
                "message": "Refresh token is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:

        refresh = RefreshToken(
            refresh_token_value
        )

        new_access_token = refresh.access_token

        return Response(
            {
                "access": str(new_access_token)
            }
        )

    except Exception:

        return Response(
            {
                "message": "Invalid or expired refresh token"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )


# =========================================
# READ ALL USERS
# =========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):

    users = User.objects.all()

    serializer = UserSerializer(
        users,
        many=True
    )

    return Response(serializer.data)


# =========================================
# READ ONE USER
# =========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, id):

    try:

        user = User.objects.get(
            id=id
        )

    except User.DoesNotExist:

        return Response(
            {
                "message": "User not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserSerializer(user)

    return Response(serializer.data)


# =========================================
# UPDATE USER
# =========================================

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, id):

    try:

        user = User.objects.get(
            id=id
        )

    except User.DoesNotExist:

        return Response(
            {
                "message": "User not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UpdateUserSerializer(
        user,
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            {
                "message": "User updated successfully",
                "user": serializer.data
            }
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================================
# DELETE USER
# =========================================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, id):

    try:

        user = User.objects.get(
            id=id
        )

    except User.DoesNotExist:

        return Response(
            {
                "message": "User not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    user.delete()

    return Response(
        {
            "message": "User deleted successfully"
        }
    )


# =========================================
# PUNCH IN
# =========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def punch_in(request):

    user = request.user

    today = timezone.localdate()

    attendance = Attendance.objects.filter(
        user=user,
        date=today
    ).first()

    if attendance and attendance.punch_in:

        return Response(
            {
                "message": "Already punched in today",
                "punch_in": attendance.punch_in
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if attendance is None:

        attendance = Attendance.objects.create(
            user=user
        )

    attendance.punch_in = timezone.now()

    attendance.save()

    return Response(
        {
            "message": "Punch in successful",
            "user": user.username,
            "punch_in": attendance.punch_in
        }
    )


# =========================================
# PUNCH OUT
# =========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def punch_out(request):

    user = request.user

    today = timezone.localdate()

    try:

        attendance = Attendance.objects.get(
            user=user,
            date=today
        )

    except Attendance.DoesNotExist:

        return Response(
            {
                "message": "Please punch in first"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if attendance.punch_out:

        return Response(
            {
                "message": "Already punched out today"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    attendance.punch_out = timezone.now()

    attendance.save()

    return Response(
        {
            "message": "Punch out successful",
            "user": user.username,
            "punch_out": attendance.punch_out
        }
    )


# =========================================
# MY ATTENDANCE
# =========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_attendance(request):

    attendance = Attendance.objects.filter(
        user=request.user
    ).order_by('-date')

    serializer = AttendanceSerializer(
        attendance,
        many=True
    )

    return Response(serializer.data)