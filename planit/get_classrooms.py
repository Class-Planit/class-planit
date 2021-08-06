from .models import *



#Gets the class name, number of students, support teachers and classroom id
def get_classroom_summary(user_id, date):
    user_profile = User.objects.get(id=user_id)
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    final_list = []
    for single_classroom in classroom_profiles:
        class_list_matches, created = classroomLists.objects.get_or_create(lesson_classroom=single_classroom, year=date)
        class_name = single_classroom.classroom_title
        student_list = single_classroom.student.all()
        #student_count = student_list.count()

        student_count = len(student_list)
        shared_list = single_classroom.support_teachers.all()
        s_match = User.objects.filter(id__in=shared_list)
        shared_m = []
        for item in s_match:
            first_name = item.first_name
            last_name = item.last_name
            last_initial = last_name[0]
            s_name = '%s %s.' % (first_name, last_initial)
            shared_m.append(s_name)

        result = class_name, student_count, shared_m, single_classroom.id
        final_list.append(result)

    return(final_list)


