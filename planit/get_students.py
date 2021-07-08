from .models import *




def get_classroom_list_summary(user_id, date, class_id):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    single_classroom = classroomLists.objects.filter(lesson_classroom=classroom_profile, year=date).first()
    class_name = classroom_profile.classroom_title
    if single_classroom:
        student_list = single_classroom.students.all()
        for student in student_list:
            pass


def get_student_list(user_id, class_id):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    single_classroom = classroomLists.objects.filter(lesson_classroom=classroom_profile).first()

    all_students = classroom_profile.student.all()
    student_profile_matches = studentProfiles.objects.filter(id__in=all_students)
    
    student_list = []
    for student in student_profile_matches:
        #if student doesn't have a username, they are still pending
        if student.student_username:
            student_user = User.objects.get(id=student.student_username_id)
            student_invite = None
        else:
            student_user = None 
            student_invite = studentInvitation.objects.filter(first_name= student.first_name, last_name= student.last_name, for_classroom= classroom_profile).first()

        result = {'s_first': student.first_name, 's_last': student.last_name, 'g_level': student.current_grade_level, 'username': student_user,\
                  'student_invite': student_invite}
        student_list.append(result)

    student_list.sort(key=lambda x: x['s_last'])
    return(student_list)


def get_teacher_list(user_id, class_id):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    single_classroom = classroomLists.objects.filter(lesson_classroom=classroom_profile).first()

    teacher_list = []
    #contains all the teachers currently in the classroom
    all_teachers = classroom_profile.support_teachers.all()
    teacher_profile_matches = User.objects.filter(id__in=all_teachers)
    for teacher in teacher_profile_matches:
        teacher_invite = None
        result = {'t_first': teacher.first_name, 't_last': teacher.last_name, 'email': teacher.email, 'teacher_invite': teacher_invite}
        teacher_list.append(result)

    #contains all the teachers pending for the classroom
    all_invites = teacherInvitation.objects.filter(for_classroom= classroom_profile, is_pending= True)
    for invite in all_invites:
        result = {'t_first': invite.first_name, 't_last': invite.last_name, 'email': invite.email, 'teacher_invite': invite}
        teacher_list.append(result)
    
    teacher_list.sort(key=lambda x: x['t_last'])
    return(teacher_list)