
action_url = 'www.app-classplanit.co/student-dashboard/%s/%s/0' % (lesson_id, worksheet_id)
message = 'You have a new Assignment'
new_alert = "<h5>You have a new Assignment</h5><br><p><a href='%s'>Click Here to View</a>" % (alert.message, alert.date, action_url, alert.is_seen, )


action_url = 'www.app-classplanit.co/student-stickers/%s/%s/' % (student_id, sticker_id)
message = 'You have a new Sticker'
new_alert = "<h5>%s</h5><br><p><a href='%s'>Click Here to View</a>" % (alert.message, alert.date, action_url, alert.is_seen )