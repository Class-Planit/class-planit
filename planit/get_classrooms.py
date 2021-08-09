from .models import *


#Gets the class name, number of students, support teachers and classroom id
def get_classroom_summary(user_id, date, current_date):
    user_profile = User.objects.get(id=user_id)
    class_string = "%s 's demo class" % (user_profile.username)
    stand_match = user_profile.standards_set
    
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    final_list = []
    if classroom_profiles:
        pass
    else:
        subject_match = standardSubjects.objects.filter(subject_title='Mathematics').first()
        grade_match = gradeLevel.objects.filter(grade='08').first()
        if grade_match:
            end_date = current_date + relativedelta(years=1)
            new_year, created = academicYear.objects.get_or_create(start_date=current_date, end_date=end_date, planning_teacher=user_profile)
            add_demo, created = classroom.objects.get_or_create(main_teacher=user_profile, single_grade=grade_match, academic_year=new_year, standards_set=stand_match, classroom_title=class_string)
            if subject_match:
                add_demo.subjects.add(subject_match)

    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
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


def get_levels_of_understanding(class_id, current_year, current_week, user_profile):
    current_classroom = classroom.objects.get(id=class_id)
    start_week = current_week - 4
    end_week = current_week
    assignment_matches = worksheetClassAssignment.objects.filter(assigned_classrooms=current_classroom, academic_year=current_year, week_of__range=[start_week, end_week])