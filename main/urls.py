from django.urls import path
from .views.base import *
from .views.auth import *
from .views.course import *
from .views.profile import *
from .views.review import *
from .views.complaint import *
from .views.enrollment import *


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('courses/', CourseListView.as_view(), name='courses_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('add-course/', create_course, name='add_course'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('profile/reset-password/<int:user_id>/verify/', VerifyResetCodeView.as_view(), name='verify_reset_code'),  # Добавил проверку кода
    path('profile/reset-password/<int:user_id>/new/', NewPasswordView.as_view(), name='new_password'),
    path('verify-email/<int:user_id>/', VerifyEmailView.as_view(), name='verify_email'),
    path("course/<int:course_id>/sign/", SignCourseView.as_view(), name="sign_course"),
    path("course/<int:course_id>/unsign/", UnsignCourseView.as_view(), name="unsign_course"),
    path("enrollment/<int:enrollment_id>/pay/", PayForCourseView.as_view(), name="pay_for_course"),
    path("enrollment/<int:enrollment_id>/payment-error/", payment_error_view, name="payment_error"),
    path("course/<int:course_id>/confirm-unsign/", confirm_unsign_view, name="confirm_unsign"),
    path("course/<int:course_id>/review/", AddReviewView.as_view(), name="add_review"),
    path("course/<int:course_id>/delete/", CourseDeleteView.as_view(), name="delete_course"),
    path('complaints/', ComplaintListView.as_view(), name='complaint_list'),
    path('complaints/<int:pk>/', ComplaintDetailView.as_view(), name='complaint_detail'),
    path('complaints/create/', ComplaintCreateView.as_view(), name='complaint_create'),
    path('complaints/<int:complaint_id>/message/', SendMessageView.as_view(), name='send_message'),
    path('complaints/<int:complaint_id>/close/', CloseComplaintView.as_view(), name='close_complaint'),
    path('complaints/admin/', AdminComplaintListView.as_view(), name='admin_complaint_list'),
    path('complaints/admin/<int:pk>/', AdminComplaintDetailView.as_view(), name='admin_complaint_detail'),
    path('admin/complaints/<int:pk>/send/', AdminSendMessageView.as_view(), name='admin_send_message'),
    path('admin/complaints/<int:pk>/close/', AdminCloseComplaintView.as_view(), name='admin_close_complaint'),
    path('about/', AboutView.as_view(), name='about'),
    path("reviews/", SchoolReviewListCreateView.as_view(), name="school_reviews"),
    path("reviews/delete/<int:pk>/", SchoolReviewDeleteView.as_view(), name="delete_review"),
    path("contacts/", ContactPageView.as_view(), name="contacts"),

]


