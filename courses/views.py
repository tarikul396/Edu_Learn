
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Course, Lesson, Student
from .forms import CourseForm, LessonForm, CourseEnrollmentForm
from django.shortcuts import render, get_object_or_404
from .models import Course, Student
from .forms import UserUpdateForm, CustomUserCreationForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from .models import Course
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course
from .serializers import CourseSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Course

class EnrollStudentAPI(APIView):
    def post(self, request):
        student_email = request.data.get('email')
        course_id = request.data.get('course_id')

        if not student_email or not course_id:
            return Response({'error': 'Email and course_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        student, created = Student.objects.get_or_create(email=student_email)
        student.enrolled_courses.add(course)

        return Response({'message': f'{student.email} has been enrolled in {course.title}'})

class CourseListAPI(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class CourseDetailAPI(APIView):
    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CourseSerializer(course)
        return Response(serializer.data)

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list2.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

class CourseCreateView(CreateView):
    model = Course
    fields = ['title', 'description', 'duration', 'thumbnail']
    template_name = 'courses/course_form2.html'
    success_url = reverse_lazy('course_list2')

# Course List
@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

# Course Detail
@login_required
# def course_detail(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
    
#     return render(request, 'courses/course_detail.html', {'course': course, 'lessons': lessons})



def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, email=request.user.email)
    lessons = course.lessons.all()
    
    context = {
        'student': student,
        'course': course,
        'lessons': lessons,
    }
    
    return render(request, 'courses/course_detail.html', context)


# Create Course
@login_required
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully!")
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})

# Update Course
@login_required
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form})

# Delete Course
@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

# Create Lesson
@login_required
def lesson_create(request):
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson created successfully!")
            return redirect('course_list')
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form})

# Update Lesson
@login_required
def lesson_update(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect('course_list')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form})

# Delete Lesson
@login_required
def lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})

# Enroll Student
@login_required
def enroll_student(request):
    if request.method == 'POST':
        form = CourseEnrollmentForm(request.POST)
        if form.is_valid():
            student_name = form.cleaned_data['student_name']
            student_email = form.cleaned_data['student_email']
            course = form.cleaned_data['course']
            
            student, created = Student.objects.get_or_create(email=student_email)
            
            if course in student.enrolled_courses.all():
                messages.error(request, f"{student_name} is already enrolled in this course.")
                return redirect('course_list')
            
            if student.name != student_name:
                student.name = student_name
                student.save()
            
            student.enrolled_courses.add(course)
            messages.success(request, f"{student_name} has been successfully enrolled in {course.title}.")
            return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
        else:
            messages.error(request, 'There was an error with your enrollment form. Please try again.')
    else:
        form = CourseEnrollmentForm()
    return render(request, 'courses/enroll_student.html', {'form': form})

# View students enrolled in a course
@login_required
def view_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.students_enrolled()
    return render(request, 'courses/view_students.html', {'course': course, 'students': students})



# User Registration
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('courses/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'courses/register.html', {'form': form})

# User Login
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('courses/')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'courses/login.html', {'form': form})

# User Logout
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'courses/profile.html', {'form': form})



# # from django.shortcuts import render, HttpResponse
# # from django.shortcuts import get_object_or_404
# # from .models import  Course
# # # Create your views here.
# # def home(request):
# #     courses=Course.objects.all()
# #     #return HttpResponse("hello world")
# #     return render(request,'courses/index.html',{'allCourses':courses})

# # def course_details(request,id):
# #     course=get_object_or_404(Course,id=id)
# #     lessons=course.lessons.all()
# #     return render(request,'courses/des.html',{'lessons':lessons, 'course': course })

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import Course, Lesson
# from .forms import CourseForm, LessonForm

# from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm



# # Course List
# def course_list(request):
#     courses = Course.objects.all()
#     return render(request, 'courses/course_list.html', {'courses': courses})

# # Course Detail
# def course_detail(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     lessons = course.lessons.all()
#     return render(request, 'courses/course_detail.html', {'course': course, 'lessons': lessons})

# # Create Course
# def course_create(request):
#     if request.method == "POST":
#         form = CourseForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Course created successfully!")
#             return redirect('course_list')
#     else:
#         form = CourseForm()
#     return render(request, 'courses/course_form.html', {'form': form})

# # Update Course
# def course_update(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     if request.method == "POST":
#         form = CourseForm(request.POST, request.FILES, instance=course)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Course updated successfully!")
#             return redirect('course_list')
#     else:
#         form = CourseForm(instance=course)
#     return render(request, 'courses/course_form.html', {'form': form})

# # Delete Course
# def course_delete(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     if request.method == "POST":
#         course.delete()
#         messages.success(request, "Course deleted successfully!")
#         return redirect('course_list')
#     return render(request, 'courses/course_confirm_delete.html', {'course': course})


# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Lesson
# from .forms import LessonForm

# # Create Lesson
# def lesson_create(request):
#     if request.method == "POST":
#         form = LessonForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Lesson created successfully!")
#             return redirect('course_list')
#     else:
#         form = LessonForm()
#     return render(request, 'courses/lesson_form.html', {'form': form})

# # Update Lesson
# def lesson_update(request, lesson_id):
#     lesson = get_object_or_404(Lesson, id=lesson_id)
#     if request.method == "POST":
#         form = LessonForm(request.POST, instance=lesson)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Lesson updated successfully!")
#             return redirect('course_list')
#     else:
#         form = LessonForm(instance=lesson)
#     return render(request, 'courses/lesson_form.html', {'form': form})

# # Delete Lesson
# def lesson_delete(request, lesson_id):
#     lesson = get_object_or_404(Lesson, id=lesson_id)
#     if request.method == "POST":
#         lesson.delete()
#         messages.success(request, "Lesson deleted successfully!")
#         return redirect('course_list')
#     return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .forms import CourseEnrollmentForm
# from .models import Student

# # def enroll_student(request):
# #     if request.method == 'POST':
# #         form = CourseEnrollmentForm(request.POST)
# #         if form.is_valid():
# #             student_email = form.cleaned_data['student_email']
# #             course = form.cleaned_data['course']

# #             # Get or create the student
# #             student, created = Student.objects.get_or_create(email=student_email)
# #             student.enrolled_courses.add(course)

# #             return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
# #     else:
# #         form = CourseEnrollmentForm()

# #     return render(request, 'courses/enroll_student.html', {'form': form})

# def enroll_student(request):
#     if request.method == 'POST':
#         form = CourseEnrollmentForm(request.POST)
#         if form.is_valid():
#             student_name = form.cleaned_data['student_name']
#             student_email = form.cleaned_data['student_email']
#             course = form.cleaned_data['course']
            
#             # Use get_or_create to avoid duplicates based on the email
#             student, created = Student.objects.get_or_create(email=student_email)
            

#             if course in student.enrolled_courses.all():
#                 messages.error(request, f"{student_name} is already enrolled in this course.")
#                 return redirect('course_list')  # Or wherever you want to redirect
            
#             # Only update the name if it's not already set
#             if student.name != student_name:
#                 student.name = student_name
#                 student.save()
            
#             # Enroll the student in the selected course
#             student.enrolled_courses.add(course)
            
#             # Provide a success message
#             messages.success(request, f"{student_name} has been successfully enrolled in {course.title}.")

#             return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
#         else:
#             messages.error(request, 'There was an error with your enrollment form. Please try again.')

#     else:
#         form = CourseEnrollmentForm()

#     return render(request, 'courses/enroll_student.html', {'form': form})


# # View students enrolled in a specific course
# def view_students(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     students = course.students_enrolled()  # Fetch all students enrolled in this course
#     return render(request, 'courses/view_students.html', {'course': course, 'students': students})







# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, "Registration successful!")
#             return redirect('/')
#     else:
#         form = UserCreationForm()
#     return render(request, 'courses/register.html', {'form': form})

# def user_login(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             messages.success(request, "Login successful!")
#             return redirect('/')
#         else:
#             messages.error(request, "Invalid username or password.")
#     else:
#         form = AuthenticationForm()
#     return render(request, 'courses/login.html', {'form': form})

# def user_logout(request):
#     logout(request)
#     messages.success(request, "You have been logged out.")
#     return redirect('/')

