from django.contrib import admin
from django.urls import path
from .import views


urlpatterns = [
    path('',views.main,name='main'),
    path('admin_login/',views.admin_login,name='admin_login'),
    path('user_login/',views.user_login,name='user_login'),
    path('user_signup/',views.user_signup,name='user_signup'),
    path('user_dashboard/',views.user_dashboard,name='user_dashboard'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('add_users/', views.add_users, name='add_users'),
    path('manage_user/', views.manage_user, name='manage_user'),
    path('approve_user/', views.approve_user, name='approve_user'),
    path('block_user/', views.block_user, name='block_user'),
    path('word_recall/', views.word_recall, name='word_recall'),
    path('attempt_test/', views.attempt_test, name='attempt_test'),
    path('view_questions/', views.view_questions, name='view_questions'),
    path('result_page/', views.result_page, name='result_page'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('verbal_fluency/', views.verbal_fluency, name='verbal_fluency'),
    path('attempt_fluency/', views.attempt_fluency, name='attempt_fluency'),
    path('number_memory_test/', views.start_number_memory_test, name='start_number_memory_test'),
    path('check_number_memory_click/', views.check_number_memory_click, name='check_number_memory_click'),
    path('record_recall_start/', views.record_recall_start, name='record_recall_start'),
    path('number_memory_results/', views.number_memory_results, name='number_memory_results'),
    path('number_memory_config/', views.number_memory_config, name='number_memory_config'),
    path('admin_number_memory_results/', views.admin_number_memory_results,name='admin_number_memory_results'),
    path('all_scores/', views.all_scores, name='all_scores'),
    path('submit_word_recall/', views.submit_word_recall, name='submit_word_recall'),
    path('exam-detail/<str:exam_type>/<int:result_id>/', views.user_exam_detail, name='user_exam_detail'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('test_scores/', views.test_scores, name='test_scores'),
]