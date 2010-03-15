import re
import datetime

def humanize_timesince(start_time):
    delta = datetime.datetime.now() - start_time

    plural = lambda x: 's' if x != 1 else ''

    num_years = delta.days / 365
    if (num_years > 0):
        return "%d year%s" % (num_years, plural(num_years))

    num_weeks = delta.days / 7
    if (num_weeks > 0):
        return "%d week%s" % (num_weeks, plural(num_weeks))

    if (delta.days > 0):
        return "%d day%s" % (delta.days, plural(delta.days))

    num_hours = delta.seconds / 3600
    if (num_hours > 0):
        return "%d hour%s" % (num_hours, plural(num_hours))

    num_minutes = delta.seconds / 60
    if (num_minutes > 0):
        return "%d minute%s" % (num_minutes, plural(num_minutes))

    return "a few seconds"

__anchor_p = re.compile (r'.*(http://([^ $])+).*')
def anchor_web_links(message):
    return __anchor_p.sub(r'<a href="\1">\1</a>',message)
    
