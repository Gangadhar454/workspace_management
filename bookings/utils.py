def is_valid_time_slot(start_time, end_time):
    start_hour = start_time.hour
    end_hour = end_time.hour
    return (9 <= start_hour < 18 and 
            end_hour == start_hour + 1 and 
            start_time.minute == 0 and 
            end_time.minute == 0 and
            start_time.date() == end_time.date())