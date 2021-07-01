import _datetime
from datetime import datetime
from .models import *


def get_active_week(current_week, week_of): 
    if 'Current' in week_of:
        active_week = current_week
    else:
        try:
            active_week = int(week_of)
        except:
            active_week = current_week
    
    return(active_week)

def get_week_info(week_of): 
    #checks if the week is a current week 
    # returns current week, active week, previous week and next week 
    current_week = date.today().isocalendar()[1] 
    active_week = get_active_week(current_week, week_of)

    previous_week = active_week - 1
    next_week = active_week + 1

    week_info = {'current_week': current_week, 'active_week': active_week, 'previous_week': previous_week, 'next_week': next_week}
    return(week_info)