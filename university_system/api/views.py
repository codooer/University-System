from django.shortcuts import render
from django.contrib.auth.models import AnonymousUser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import exceptions
from grades.models import Grade,SemesterGrade,Semester,Year,MidtermGrade,QuizGrade,AssignmentGrade
from courses.models import Course
from quizzes.models import Quiz
from .serializers import MidtermGradeSerializer

@api_view(['GET'])
def gradeview(request,course_code):
    if isinstance(request.user,AnonymousUser):
        raise exceptions.NotAuthenticated
    try:
        course = Course.objects.get(course_code=course_code)
        grade = Grade.objects.get(student=request.user,course=course)
    except (Course.DoesNotExist,Grade.DoesNotExist):
        raise exceptions.NotFound
    grades = {
        'Final':grade.final,
        'Quizzes':grade.get_quiz_grades(),
        'Assignament':grade.get_assignament_grades(),
        'Midterm':grade.get_midterm_grades(),
        'Others':grade.other,
        'Total':grade.get_total_grades()
    }
    data = {
        'labels':grades.keys(),
        'data':grades.values(),
        'course':course
    }
    return Response(data=data)

def gradeView(request):
    return render(request,'grade/gradeview.html')

@api_view(['GET'])
def course_quizzes_grade_api(request,course_code):
    if isinstance(request.user,AnonymousUser):
        raise exceptions.NotAuthenticated
    try:
        course = Course.objects.get(course_code=course_code)
        quizzes = Quiz.objects.get_answered_quizzes(course=course,studnet=request.user)
        grades = {quiz.name:Quiz.objects.get_student_grade(quiz,request.user) for quiz in quizzes}
    except (Course.DoesNotExist,Quiz.DoesNotExist):
        raise exceptions.NotFound
    data = {#try to do it in one dict compre
        'labels':grades.keys(),
        'data':grades.values(),
    }
    return Response(data=data)

def course_quizzes_grade_view(request):
    return render(request,'grade/quizgrade.html')

@api_view(['GET'])
def semester_course_grade_api(request,year,semester):
    if isinstance(request.user,AnonymousUser):
        raise exceptions.NotAuthenticated
    try:
        year=Year.objects.get(year=year)
        semester = Semester.objects.get(semester=semester,year=year)
        grade = SemesterGrade.objects.get(student=request.user,year=year,semester=semester)
    except (Year.DoesNotExist,Semester.DoesNotExist,SemesterGrade.DoesNotExist):
        raise exceptions.NotFound
    grades,total = grade.calc_total()
    labels = [course.course.name for course in grades.keys()]
    data = {
        'labels':labels,
        'data':grades.values(),
        'total':total
    }
    return Response(data=data)
    
def semester_course_grade_view(request):
    return render(request,'grade/semester_grade.html')


@api_view(['GET'])
def midterm_grade_api(request,year,semester):
    year=Year.objects.get(year=year)
    semester = Semester.objects.get(semester=semester,year=year)
    midterm = MidtermGrade.objects.filter(year=year,semester=semester,student=request.user).all()
    grades = {mid.course.name:mid.mark for mid in midterm}
    data = {
        'labels':grades.keys(),
        'data' : grades.values(),
        'avg':sum(grades.values())/midterm.count()
    }
    return Response(data=data)

def midterm_grade(request):
    return render(request,'grade/midterm_grade.html')

@api_view(['GET'])
def year_midterm_api(request,year):
    year = Year.objects.get(year=year)
    midterm_grades = MidtermGrade.objects.filter(year=year,student=request.user).all()
    print(midterm_grades)
    serializer = MidtermGradeSerializer(instance=midterm_grades,many=True)
    print(serializer)
    return Response(serializer.data)