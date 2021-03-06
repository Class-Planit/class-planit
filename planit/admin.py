from django.contrib import admin
from .models import *
# Register your models here.

class wikiTopicAdmin(admin.ModelAdmin):
    model = wikiTopic
    list_filter = ['is_selected']

class topicQuestionitemAdmin(admin.ModelAdmin):
    model = topicQuestionitem
    search_fields = ['Question']

class topicInformationAdmin(admin.ModelAdmin):
    model = wikiTopic
    search_fields = ['item']

class textBookBackgroundAdmin(admin.ModelAdmin):
    model = textBookBackground
    search_fields = ['line_text']


class topicDescriptionAdmin(admin.ModelAdmin):
    model = topicDescription
    search_fields = ['description']
    list_filter = ['is_admin']


class LearningDemonstrationTemplateAdmin(admin.ModelAdmin):
    model = LearningDemonstrationTemplate
    search_fields = ['content']
    list_filter = ['topic_type']

class lessonTemplatesAdmin(admin.ModelAdmin):
    model = lessonTemplates
    search_fields = ['wording']
    list_filter = ['components']


class selectedActivityAdmin(admin.ModelAdmin):
    model = selectedActivity
    search_fields = ['lesson_text']



admin.site.register(singleRec)
admin.site.register(reccomendedTopics)
admin.site.register(lessonStandardRecommendation)
admin.site.register(User)
admin.site.register(school_user)
admin.site.register(lessonImageUpload)
admin.site.register(lessonPDFText)
admin.site.register(lessonPDFImage)
admin.site.register(worksheetFull)
admin.site.register(textBookTitle)
admin.site.register(LearningDemonstrationTemplate, LearningDemonstrationTemplateAdmin)
admin.site.register(LearningDemonstration)
admin.site.register(matchedTopics)
admin.site.register(standardSet)
admin.site.register(gradeLevel)
admin.site.register(academicYear)
admin.site.register(studentProfiles)
admin.site.register(classroom)
admin.site.register(classroomLists)
admin.site.register(standardSubjects)
admin.site.register(lessonObjective)
admin.site.register(singleStandard)
admin.site.register(vocabularyWord)
admin.site.register(lessonFull)
admin.site.register(teacherLessonTemplates)
admin.site.register(lessonSectionTemplate)
admin.site.register(lessonSection)
admin.site.register(googleSearchResult)
admin.site.register(keywordResults)
admin.site.register(wikiTopic, wikiTopicAdmin)
admin.site.register(googleRelatedQuestions)
admin.site.register(lessonTemplates, lessonTemplatesAdmin)
admin.site.register(lessonProduct)
admin.site.register(topicInformation, topicInformationAdmin)
admin.site.register(topicTypes)
admin.site.register(textBookBackground, textBookBackgroundAdmin)
admin.site.register(shortStorySection)
admin.site.register(shortStory)
admin.site.register(youtubeSearchResult)
admin.site.register(lessonText)
admin.site.register(questionType)
admin.site.register(topicQuestionitem, topicQuestionitemAdmin)
admin.site.register(mainQuestion)
admin.site.register(topicDescription, topicDescriptionAdmin)
admin.site.register(selectedActivity, selectedActivityAdmin)
admin.site.register(teacherQuestionnaire)
admin.site.register(userNickname)
admin.site.register(worksheetTheme)
admin.site.register(userImageUpload)
admin.site.register(studentQuestionAnswer)
admin.site.register(studentWorksheetAnswerFull)
admin.site.register(worksheetClassAssignment)
admin.site.register(studentPraiseTheme)
admin.site.register(studentPraise)
admin.site.register(studentInvitation)
admin.site.register(teacherInvitations)
admin.site.register(waitlistUserInfo)
admin.site.register(alertMessage)