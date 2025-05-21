from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'accounts_app'

urlpatterns = [
    # Home - redirect to venues_app home
    path('', lambda request: redirect('venues_app:home'), name='home'),

    # Business
    path('for-business/', views.for_business_view, name='for_business'),

    # Authentication
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/customer/', views.CustomerSignUpView.as_view(), name='customer_signup'),
    path('signup/service-provider/', views.ServiceProviderSignUpView.as_view(), name='service_provider_signup'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/customer/', views.CustomerProfileView.as_view(), name='customer_profile'),
    path('profile/customer/edit/', views.CustomerProfileEditView.as_view(), name='customer_profile_edit'),
    path('profile/service-provider/<slug:slug>/', views.ServiceProviderProfileView.as_view(), name='service_provider_profile'),
    path('profile/service-provider/<slug:slug>/edit/', views.ServiceProviderProfileEditView.as_view(), name='service_provider_profile_edit'),
    path('profile/delete/', views.account_delete_view, name='account_delete'),

    # Password management
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', views.password_change_done_view, name='password_change_done'),
    path('password/reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', views.password_reset_complete_view, name='password_reset_complete'),

    # Staff management
    path('staff/', views.staff_list_view, name='staff_list'),
    path('staff/add/', views.staff_add_view, name='staff_add'),
    path('staff/<int:pk>/edit/', views.staff_edit_view, name='staff_edit'),
    path('staff/<int:pk>/toggle-active/', views.staff_toggle_active_view, name='staff_toggle_active'),
    path('staff/<int:pk>/delete/', views.staff_delete_view, name='staff_delete'),

]
