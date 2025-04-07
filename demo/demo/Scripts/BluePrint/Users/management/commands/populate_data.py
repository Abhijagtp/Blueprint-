
from django.core.management.base import BaseCommand
from Users.models import Degree, Specialization, Industry

class Command(BaseCommand):
    help = 'Populates degrees, specializations, and industries'

    def handle(self, *args, **kwargs):
        degrees_data = {
            'B.Tech': [
                'Computer Science and Engineering', 'Mechanical Engineering', 'Electrical Engineering',
                'Civil Engineering', 'Information Technology', 'Aerospace Engineering', 'Chemical Engineering',
                'Electronics and Communication Engineering', 'Biotechnology', 'Automobile Engineering'
            ],
            'M.Tech': [
                'Data Science', 'Artificial Intelligence', 'VLSI Design', 'Structural Engineering',
                'Thermal Engineering', 'Power Systems', 'Environmental Engineering', 'Robotics'
            ],
            'B.Sc': [
                'Physics', 'Chemistry', 'Mathematics', 'Biology', 'Computer Science', 'Environmental Science',
                'Geology', 'Statistics'
            ],
            'M.Sc': [
                'Data Science', 'Biotechnology', 'Physics', 'Chemistry', 'Mathematics', 'Environmental Science',
                'Microbiology'
            ],
            'B.Com': [
                'Accounting', 'Finance', 'Taxation', 'Banking', 'Business Economics', 'Corporate Secretaryship'
            ],
            'BBA': [
                'Marketing', 'Finance', 'Human Resources', 'Entrepreneurship', 'International Business'
            ],
            'MBA': [
                'Finance', 'Marketing', 'Human Resource Management', 'Operations Management', 'Business Analytics',
                'International Business', 'Supply Chain Management'
            ],
            'MBBS': [
                'General Medicine', 'Surgery', 'Pediatrics', 'Orthopedics', 'Gynecology', 'Cardiology', 'Neurology'
            ],
            'BDS': [
                'Orthodontics', 'Periodontics', 'Oral Surgery', 'Prosthodontics'
            ],
            'B.Pharm': [
                'Pharmaceutics', 'Pharmacology', 'Pharmaceutical Chemistry', 'Pharmacognosy'
            ],
            'B.A': [
                'English Literature', 'History', 'Economics', 'Psychology', 'Sociology', 'Political Science', 'Geography'
            ],
            'M.A': [
                'English Literature', 'Economics', 'Psychology', 'Sociology', 'Political Science', 'History'
            ],
            'LLB': [
                'Criminal Law', 'Corporate Law', 'Constitutional Law', 'Intellectual Property Law', 'Environmental Law'
            ],
            'B.Arch': [
                'Urban Planning', 'Interior Design', 'Landscape Architecture', 'Sustainable Architecture'
            ],
            'B.Ed': [
                'Elementary Education', 'Special Education', 'Science Education', 'Mathematics Education', 'Language Education'
            ],
            'BCA': [
                'Software Development', 'Web Development', 'Database Management', 'Networking'
            ],
            'BHM': [
                'Food and Beverage Service', 'Front Office Management', 'Housekeeping', 'Culinary Arts'
            ]
        }

        industries = [
            'Agriculture, Forestry and Fishing', 'Mining and Quarrying', 'Manufacturing',
            'Electricity, Gas, Steam and Air Conditioning Supply', 'Water Supply; Sewerage, Waste Management',
            'Construction', 'Wholesale and Retail Trade', 'Transportation and Storage',
            'Accommodation and Food Service Activities', 'Information and Communication',
            'Financial and Insurance Activities', 'Real Estate Activities',
            'Professional, Scientific and Technical Activities', 'Administrative and Support Service Activities',
            'Public Administration and Defence', 'Education', 'Human Health and Social Work Activities',
            'Arts, Entertainment and Recreation', 'Other Service Activities'
        ]

        # Populate Degrees and Specializations
        for degree_name, specs in degrees_data.items():
            degree, _ = Degree.objects.get_or_create(name=degree_name)
            for spec in specs:
                Specialization.objects.get_or_create(degree=degree, name=spec)

        # Populate Industries
        for industry_name in industries:
            Industry.objects.get_or_create(name=industry_name)

        self.stdout.write(self.style.SUCCESS('Data populated successfully'))