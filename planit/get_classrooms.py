from .models import *




def get_classroom_summary(user_id, date):
    user_profile = User.objects.get(id=user_id)
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    final_list = []
    for single_classroom in classroom_profiles:
        class_list_matches, created = classroomList.objects.get_or_create(lesson_classroom=single_classroom, academic_year=date)
        class_name = single_classroom.classroom_title
        student_list = class_list_matches.students.all()
        student_count = student_list.count()
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


