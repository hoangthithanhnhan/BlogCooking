from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # View
    path('home/', views.home, name='home'),
    path('', views.viewhome, name='viewhome'),

    # Login-out----
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('register/', views.register, name='register'),
    # User

    path('postfood/', views.postfood, name='postfood'),  # Đăng bài
    path('detail/<int:recipe_id>/', views.detail, name='detail'),  # Xem Chi Tiet Từng SP
    path('savefood/', views.savefood, name='savefood'),  # Lưu Bài
    path('like-recipe/<int:recipe_id>/', views.like_recipe, name='like_recipe'),  # Like SP
    path('page_user/', views.page_user, name='page_user'),  # Trang cá Nhân
    path('edit_user/', views.edit_user, name='edit_user'),  # Chỉnh Sửa Trang cá Nhân
    path('user/<int:user_id>/', views.detail_user, name='detail_user'),  # Xem Người Dùng Khác

    path('myfood/', views.myfood, name='myfood'),
    path('recipe/delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),  # Xóa bài của mình
    path('recipe/edit/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),  # Chỉnh Sửa bài của mình
    path('search_title/', views.search_title, name='search_title'),  # Tìm Kiếm SP
    path('report-food/<int:recipe_id>/', views.report_food, name='report_food'),  # Report

    # Admin
    path('ad/', views.home_admin, name='ad'),  # Đường dẫn đến trang admin
    path('rpfood/', views.rpfood, name='rpfood'),  # Đường dẫn đến trang Report Food
    path('delete-admin/<int:post_id>/', views.admin_delete, name='admin_delete'),  # Admin Xóa Bài Viết
    path('detail_admin/<int:recipe_id>/', views.detail_admin, name='detail_admin'),  # Admin Xóa Bài Viết

    # Filter Food
    path('recipes/vegetarian/', views.vegetarian, name='vegetarian'),  # Chay
    path('recipes/grill/', views.grill, name='grill'),  # Nướng
    path('recipes/asian/', views.asian, name='asian'),  # Á
    path('recipes/european/', views.european, name='european'),  # ÂU
    path('recipes/appetizer/', views.appetizer, name='appetizer'),  # Khai Vị
    path('recipes/dessert/', views.dessert, name='dessert'),  # Tráng Miện
    path('recipes/snacks/', views.snacks, name='snacks'),  # Ăn Vặt

    # User
    path('users/', views.list_user, name='list_user'),
    path('search/', views.search_user, name='search_user'),

    # Follow
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('notifications/', views.notifications, name='notifications'),  # Thông Báo
]       