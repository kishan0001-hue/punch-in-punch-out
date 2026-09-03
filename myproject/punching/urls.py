from django.urls import path

from . import views


urlpatterns = [

    # USER
    path(
        'users/create/',
        views.create_user,
        name='create-user'
    ),

    path(
        'users/',
        views.get_users,
        name='get-users'
    ),

    path(
        'users/<int:id>/',
        views.get_user,
        name='get-user'
    ),

    path(
        'users/<int:id>/update/',
        views.update_user,
        name='update-user'
    ),

    path(
        'users/<int:id>/delete/',
        views.delete_user,
        name='delete-user'
    ),


    # AUTH
    path(
        'login/',
        views.login_user,
        name='login'
    ),


    # ATTENDANCE
    path(
        'punch-in/',
        views.punch_in,
        name='punch-in'
    ),

    path(
        'punch-out/',
        views.punch_out,
        name='punch-out'
    ),

    path(
        'my-attendance/',
        views.my_attendance,
        name='my-attendance'
    ),

    path(
        'refresh/',
        views.refresh_token,
        name='refresh_token'
    ),
]