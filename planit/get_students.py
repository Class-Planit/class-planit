from .models import *




def get_classroom_list_summary(user_id, date, class_id):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    single_classroom = classroomList.objects.get(lesson_classroom=classroom_profile, academic_year=date)
    class_name = classroom_profile.classroom_title
    student_list = single_classroom.students.all()
    for student in student_list:
        pass