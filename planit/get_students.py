from .models import *




def get_classroom_summary(user_id, date, class_id):
    user_profile = User.objects.get(id=user_id)
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    class_list_matches = classroomList.objects.get(lesson_classroom=single_classroom, academic_year=date)
    class_name = single_classroom.classroom_title
    student_list = class_list_matches.students.all()
    for student in student_list:
        