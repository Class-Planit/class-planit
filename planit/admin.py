from django.contrib import admin
from .models import *
# Register your models here.

class wikiTopicAdmin(admin.ModelAdmin):
    model = wikiTopic
    list_filter = ['is_selected']

admin.site.register(User)
admin.site.register(standardSet)
admin.site.register(gradeLevel)
admin.site.register(academicYear)
admin.site.register(studentProfiles)
admin.site.register(classroom)
admin.site.register(standardSubjects)
admin.site.register(classroomSubjects)
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
admin.site.register(lessonTemplates)
admin.site.register(lessonProduct)
admin.site.register(topicInformation)
admin.site.register(topicTypes)
admin.site.register(textBookBackground)
admin.site.register(shortStorySection)
admin.site.register(shortStory)
admin.site.register(youtubeSearchResult)
admin.site.register(lessonText)


