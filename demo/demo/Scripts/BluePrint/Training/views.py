from django.shortcuts import render

from django.db.models import Count
from django.shortcuts import render
from .models import Course, Enrollment

from django.shortcuts import render
from django.db.models import Count
from .models import Course

from django.shortcuts import render
from django.db.models import Count
from .models import Course

def training_view(request):
    free_courses = Course.objects.filter(is_free=True)
    featured_courses = Course.objects.filter(is_free=False)
    trending_course = Course.objects.annotate(
        num_enrollments=Count('enrollments')
    ).order_by('-num_enrollments').first()

    search_query = request.GET.get('search', '')
    if search_query:
        free_courses = free_courses.filter(title__icontains=search_query) | free_courses.filter(overview__icontains=search_query)
        featured_courses = featured_courses.filter(title__icontains=search_query) | featured_courses.filter(overview__icontains=search_query)

    free_courses = free_courses[:6]
    featured_courses = featured_courses[:6]

    context = {
        'free_courses': free_courses,
        'featured_courses': featured_courses,
        'trending_course': trending_course,
        'search_query': search_query,
    }
    return render(request, 'training.html', context)





from django.shortcuts import render, redirect
from .models import Course, Lesson
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta


from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.db import IntegrityError
from datetime import timedelta
from .models import Course, Lesson


from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.db import IntegrityError
from datetime import timedelta
from .models import Course, Lesson

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.db import IntegrityError
from datetime import timedelta
from .models import Course, Lesson

from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify
from .models import Course, Lesson
from django.db import IntegrityError
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.db import IntegrityError
from datetime import timedelta
from django.contrib import messages
from .models import Course, Lesson 

def create_course(request):
    # Get edit_course_id from the POST data if available (for editing)
    edit_course_id = request.POST.get('edit')
    course = None
    existing_lessons = []

    # If we are editing a course
    if edit_course_id:
        course = get_object_or_404(Course, id=edit_course_id, instructor=request.user)
        existing_lessons = Lesson.objects.filter(course=course)

    # Handle form submission (both for creating and updating)
    if request.method == 'POST':
        is_free = request.POST.get('is_free') == 'on'

        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        overview = request.POST.get('overview')
        category = request.POST.get('category')
        level = request.POST.get('level')
        prerequisites = "\n".join(request.POST.getlist('prerequisites'))
        skills = "\n".join(request.POST.getlist('skills'))
        price = 0 if is_free else request.POST.get('price')
        discount = request.POST.get('discount') or 0
        thumbnail = request.FILES.get('thumbnail') or (course.thumbnail if course else None)
        featured_video = request.FILES.get('featured_video') or (course.featured_video if course else None)

        instructor = request.user

        if course:
            # If we're editing an existing course, update its fields
            course.title = title
            course.subtitle = subtitle
            course.overview = overview
            course.category = category
            course.level = level
            course.prerequisites = prerequisites
            course.skills = skills
            course.price = price
            course.discount = discount
            course.thumbnail = thumbnail
            course.featured_video = featured_video
            course.is_free = is_free
            course.save()

            messages.success(request, f"Course '{course.title}' has been updated successfully!")

        else:
            # If creating a new course, generate a slug and create it
            base_slug = slugify(title)
            slug = base_slug
            count = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            try:
                course = Course.objects.create(
                    instructor=instructor,
                    title=title,
                    subtitle=subtitle,
                    overview=overview,
                    category=category,
                    level=level,
                    prerequisites=prerequisites,
                    skills=skills,
                    price=price,
                    discount=discount,
                    thumbnail=thumbnail,
                    featured_video=featured_video,
                    is_free=is_free,
                    slug=slug
                )

                messages.success(request, f"Course '{course.title}' has been created successfully!")

            except IntegrityError:
                messages.error(request, "This course title already exists. Please choose a different title.")
                return render(request, "create_course_details.html", {"error": "This course title already exists."})

        # Handle lessons (update or add new ones)
        lesson_count = 0
        while True:
            lesson_prefix = f'lessons-{lesson_count}-'
            lesson_id = request.POST.get(f'{lesson_prefix}id')  # Get lesson ID

            if not request.POST.get(f'{lesson_prefix}title'):
                break  # Stop when no more lessons are found

            lesson_data = {
                "title": request.POST.get(f'{lesson_prefix}title'),
                "description": request.POST.get(f'{lesson_prefix}description'),
                "duration": timedelta(minutes=int(request.POST.get(f'{lesson_prefix}duration'))),
            }

            if request.FILES.get(f'{lesson_prefix}video'):
                lesson_data["video"] = request.FILES.get(f'{lesson_prefix}video')

            if lesson_id:  # If lesson ID exists, update the existing lesson
                Lesson.objects.filter(id=lesson_id, course=course).update(**lesson_data)
                messages.success(request, f"Lesson '{lesson_data['title']}' has been updated successfully!")
            else:  # Create a new lesson
                Lesson.objects.create(course=course, **lesson_data)
                messages.success(request, f"Lesson '{lesson_data['title']}' has been added successfully!")

            lesson_count += 1

        # Redirect to the course detail page after creating or updating the course
        return redirect('course_detail', slug=course.slug)

    # Render the form for creating or editing the course
    return render(request, 'create_course_details.html', {
        "course": course,
        "existing_lessons": existing_lessons
    })






from .models import LessonProgress
from django.shortcuts import get_object_or_404, render

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    prerequisites_list = course.prerequisites.splitlines()
    

    course_in_cart = False
    if request.user.is_authenticated:
        course_in_cart = CartItem.objects.filter(user=request.user, course=course).exists()

    # Ensure discount calculation only happens when a discount exists
    discounted_price = course.price - course.discount if course.discount and course.discount > 0 else course.price

    # Check if the user is enrolled
    user_enrolled = False
    if request.user.is_authenticated:
        user_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()



    lessons = course.lessons.all()
    # Get the user's progress for each lesson
   # Create a list of progress for each lesson
    lesson_progress = []
    all_completed = True  # Assume all lessons are completed initially
    for lesson in lessons:
        progress = LessonProgress.objects.filter(user=request.user, lesson=lesson).first()
        completed = progress.completed if progress else False
        lesson_progress.append({
            'lesson_id': lesson.id,
            'completed': completed,
            
        })
        if not completed:
            all_completed = False  # If any lesson is not completed, set this to False


    
    # Get the number of students enrolled in this course
    students_count = Enrollment.objects.filter(course=course, is_active=True).count()

    # Get similar courses based on category and level
    similar_courses = Course.objects.filter(
        category=course.category,
        level=course.level
    ).exclude(id=course.id)  # Exclude the current course from the results

    
    context = {
        'course': course,
        'prerequisites_list': prerequisites_list,
        'discounted_price': discounted_price,  # Pass it explicitly
        'user_enrolled': user_enrolled,
         # Pass progress to the template
        'lessons': lessons,
        'lesson_progress': lesson_progress,
        'all_completed': all_completed,
        'students_count': students_count,
        'similar_courses': similar_courses,  # Pass similar courses to the template
        'course_in_cart':course_in_cart

    }
    return render(request, 'course_detail.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Check if the user is already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")
        return redirect('course_detail', slug=course.slug)

    # If the course is free, enroll the user immediately
    if course.is_free or course.discounted_price == 0:
        Enrollment.objects.create(user=request.user, course=course)
        messages.success(request, f"You have successfully enrolled in {course.title}!")
        return redirect('course_detail', slug=course.slug)

    # If the course is paid, redirect to payment page (you may customize this)
    return redirect('checkout', course_id=course.id)  






from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Lesson, LessonProgress

@csrf_exempt
def update_progress(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lesson_id = data.get('lesson_id')
            completed = data.get('completed')

            lesson = get_object_or_404(Lesson, id=lesson_id)

            # Get or create progress entry for the user and lesson
            progress, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson, course=lesson.course)
            
            # Update completion status
            progress.completed = completed
            progress.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})




from django.shortcuts import render
from .models import Enrollment, LessonProgress, Lesson

def my_learning_view(request):
    user = request.user
    enrollments = Enrollment.objects.filter(user=user).select_related('course')

    courses_with_progress = []
    
    for enrollment in enrollments:
        course = enrollment.course
        total_lessons = Lesson.objects.filter(course=course).count()
        completed_lessons = LessonProgress.objects.filter(user=user, course=course, completed=True).count()

        progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0

        courses_with_progress.append({
            'course': course,
            'progress': int(progress)  # Convert to integer for better display
        })

    return render(request, 'learning.html', {'courses_with_progress': courses_with_progress})




from django.shortcuts import render
from .models import Course

def my_courses_view(request):
    # Fetch courses that belong to the logged-in instructor
    courses = Course.objects.filter(instructor=request.user)  # Assuming 'instructor' is a ForeignKey to User
    return render(request, 'my_courses.html', {'courses': courses})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Course
from .forms import CourseForm  # Make sure to create this form for editing courses

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import Course

def edit_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if course.instructor != request.user:  # Ensure the course belongs to the logged-in instructor
        return redirect('my_courses')  # Redirect to 'My Courses' if not authorized

    # Redirect to the course creation page with the course ID as a parameter
    return redirect(reverse('create_course') + f'?edit={course_id}')


def delete_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if course.instructor != request.user:  # Ensure the course belongs to the logged-in instructor
        return redirect('my_courses')  # Redirect to 'My Courses' if not the instructor
    
    if request.method == 'POST':
        course.delete()
        return redirect('my_courses')  # Redirect to 'My Courses' after deletion
    
    return render(request, 'confirm_delete.html', {'course': course})




# cart 

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CartItem, Course
from django.db import transaction

@csrf_exempt  # Remove after fixing CSRF
@login_required
def add_to_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            print(f"Received course_id: {course_id}")  # Debug log
            
            if not course_id:
                return JsonResponse({'success': False, 'error': 'No course ID provided'})
            
            try:
                course = Course.objects.get(id=course_id)
                print(f"Found course: {course.title}")  # Debug log
            except Course.DoesNotExist:
                print(f"Course with ID {course_id} not found")  # Debug log
                return JsonResponse({'success': False, 'error': 'Course not found'})
            
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                course=course
            )
            return JsonResponse({
                'success': True,
                'message': 'Course added to cart' if created else 'Course already in cart'
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.course.discounted_price for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def remove_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, user=request.user)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')

@login_required
def checkout(request):
    # Add your payment processing logic here
    # For now, we'll just clear the cart and redirect
    CartItem.objects.filter(user=request.user).delete()
    return redirect('traning')  # Redirect to courses page after checkout


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment

@login_required
def buy_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the user is already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        # Optionally, add a message to inform the user
        return redirect('course_detail', slug=course.slug)
    
    # Here you would typically integrate payment processing (e.g., Stripe, Razorpay)
    # For now, we'll assume the purchase is successful and enroll the user
    Enrollment.objects.create(user=request.user, course=course)
    
    # Redirect to the course detail page or a success page
    return redirect('course_detail', slug=course.slug)