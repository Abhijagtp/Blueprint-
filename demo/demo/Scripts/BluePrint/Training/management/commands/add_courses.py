from django.core.management.base import BaseCommand
from django.utils.text import slugify
from datetime import timedelta
from decimal import Decimal
from Training.models import Course, Lesson
from Users.models import CustomUser

class Command(BaseCommand):
    help = "Add dummy courses and associated lessons to the database for a specific user"

    def handle(self, *args, **kwargs):
        # Fetch the specific user by username
        try:
            instructor = CustomUser.objects.get(username="ajagtap1638@gmail.com")
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR("User with username ajagtap1638@gmail.com does not exist."))
            return
        
        # Sample course data for free and paid courses
        free_courses_data = [
            {
                "title": "Python for Beginners",
                "subtitle": "Learn Python from Scratch",
                "overview": "An introductory course to Python programming, covering the basics of syntax, loops, and functions.",
                "level": "beginner",
                "duration": timedelta(weeks=4),
                "prerequisites": "None",
                "skills": "Python basics, Syntax, Control flow, Functions",
                "category": "development",
                "price": Decimal(0),
                "is_free": True,
            },
            {
                "title": "Introduction to Machine Learning",
                "subtitle": "Get started with machine learning algorithms and models.",
                "overview": "An introductory course to machine learning, including supervised and unsupervised learning.",
                "level": "beginner",
                "duration": timedelta(weeks=5),
                "prerequisites": "Basic knowledge of Python",
                "skills": "Machine learning algorithms, Data preprocessing, Model evaluation",
                "category": "data science",
                "price": Decimal(0),
                "is_free": True,
            },
            {
                "title": "Web Development with Django",
                "subtitle": "Build robust web applications using Django framework.",
                "overview": "Learn the fundamentals of web development using Django, including models, views, and templates.",
                "level": "intermediate",
                "duration": timedelta(weeks=6),
                "prerequisites": "Basic Python and HTML",
                "skills": "Django framework, Web development, REST APIs",
                "category": "development",
                "price": Decimal(0),
                "is_free": True,
            },
            {
                "title": "Data Analysis with Pandas",
                "subtitle": "Analyze and manipulate data using Pandas.",
                "overview": "Learn how to use Pandas for data cleaning, analysis, and visualization.",
                "level": "intermediate",
                "duration": timedelta(weeks=4),
                "prerequisites": "Basic Python knowledge",
                "skills": "Pandas, Data analysis, Data visualization",
                "category": "data science",
                "price": Decimal(0),
                "is_free": True,
            },
        ]

        paid_courses_data = [
            {
                "title": "Advanced Python Programming",
                "subtitle": "Master advanced Python concepts and techniques.",
                "overview": "An advanced Python course covering topics such as decorators, generators, and context managers.",
                "level": "advanced",
                "duration": timedelta(weeks=4),
                "prerequisites": "Intermediate Python knowledge",
                "skills": "Advanced Python, Generators, Decorators, Context managers",
                "category": "development",
                "price": Decimal(100),
                "discounted_price": Decimal(80),
                "is_free": False,
            },
            {
                "title": "Full-Stack Web Development with React and Node.js",
                "subtitle": "Build full-stack web applications with React and Node.js.",
                "overview": "Learn how to develop both frontend and backend applications using React and Node.js.",
                "level": "intermediate",
                "duration": timedelta(weeks=8),
                "prerequisites": "Basic knowledge of HTML, CSS, JavaScript",
                "skills": "React, Node.js, MongoDB, Full-stack development",
                "category": "development",
                "price": Decimal(150),
                "discounted_price": Decimal(120),
                "is_free": False,
            },
            {
                "title": "Data Science with Python",
                "subtitle": "Learn the key skills in data science using Python.",
                "overview": "Master data science concepts such as data cleaning, visualization, and machine learning using Python.",
                "level": "intermediate",
                "duration": timedelta(weeks=6),
                "prerequisites": "Basic Python knowledge",
                "skills": "Data science, Machine learning, Python, Data visualization",
                "category": "data science",
                "price": Decimal(120),
                "discounted_price": Decimal(100),
                "is_free": False,
            },
            {
                "title": "Cloud Computing with AWS",
                "subtitle": "Learn how to deploy applications using AWS Cloud services.",
                "overview": "Understand AWS core services and how to deploy and manage scalable cloud applications.",
                "level": "advanced",
                "duration": timedelta(weeks=5),
                "prerequisites": "Basic understanding of cloud computing",
                "skills": "AWS, Cloud computing, Deployment, Scalability",
                "category": "cloud computing",
                "price": Decimal(130),
                "discounted_price": Decimal(100),
                "is_free": False,
            },
            {
                "title": "AI for Business Leaders",
                "subtitle": "Learn how artificial intelligence can be applied in business contexts.",
                "overview": "A course designed to introduce AI concepts and how they can be applied to solve business problems.",
                "level": "beginner",
                "duration": timedelta(weeks=3),
                "prerequisites": "None",
                "skills": "Artificial Intelligence, Business applications, Problem solving",
                "category": "business",
                "price": Decimal(80),
                "discounted_price": Decimal(65),
                "is_free": False,
            },
        ]

        # Helper function to create courses
        def create_course(course_data):
            course = Course.objects.create(
                instructor=instructor,
                title=course_data['title'],
                subtitle=course_data['subtitle'],
                slug=slugify(course_data['title']),
                overview=course_data['overview'],
                level=course_data['level'],
                duration=course_data['duration'],
                prerequisites=course_data['prerequisites'],
                skills=course_data['skills'],
                category=course_data['category'],
                price=course_data['price'],
               
                is_free=course_data['is_free'],
                status='published' if not course_data['is_free'] else 'draft',
            )

            # Add lessons to the course
            lessons = [
                {
                    "title": "Lesson 1",
                    "description": "Introduction to the course content and fundamentals.",
                    "duration": timedelta(minutes=30),
                },
                {
                    "title": "Lesson 2",
                    "description": "Deep dive into core concepts.",
                    "duration": timedelta(minutes=45),
                },
                {
                    "title": "Lesson 3",
                    "description": "Advanced topics and practical applications.",
                    "duration": timedelta(minutes=60),
                },
            ]

            for lesson in lessons:
                Lesson.objects.create(
                    course=course,
                    title=lesson['title'],
                    description=lesson['description'],
                    duration=lesson['duration'],
                )
        
        # Create all courses
        for course_data in free_courses_data + paid_courses_data:
            create_course(course_data)

        self.stdout.write(self.style.SUCCESS("Courses and lessons added successfully for instructor ajagtap1638@gmail.com"))
