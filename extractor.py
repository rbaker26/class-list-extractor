#!/usr/bin/env python3
from bs4 import BeautifulSoup
from gettext import find
from urllib.request import urlopen

# templateized so that the year and semester can easily be changed
url = 'https://mysite.socccd.edu/onlineschedule/ClassFind.asp?siteID=A&termID={year}{semester}&termtype=&mktcode=CO20&header=Computer+Science'

year = 2018
semester = 3 # fall
sem_map = {
        1: 'Spring',
        2: 'Summer',
        3: 'Fall',
        }

#*******************************************************************************************************************
def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start
#*******************************************************************************************************************



#*******************************************************************************************************************
def build_dict(url):
    # The page has a dangling /div
    # Python's html.parser doesn't handle this adequately, so we need html5lib
    soup = BeautifulSoup(urlopen(url).read(), "html5lib")

    courses = []
    course_tables = soup.find_all(attrs={'class': 'class-list-course-list'})
    for course_table in course_tables:
        tickets = []

        temp_prereq_str = course_table.find(attrs={'class': 'class-list-course-info'}).text.strip()
        if (len(temp_prereq_str) > 12):
            temp_prereq_split = temp_prereq_str.find('Prerequisite')
            temp_prereq_str = temp_prereq_str[temp_prereq_split+13:].strip()
        else:
            temp_prereq_str = 'null'


        course_info = {
            'units' : course_table.find(attrs={'class': 'class-list-unit'}).text.strip()[7:],
            'prereq': temp_prereq_str,
            }
        course = {
                'course_id': course_table.find(attrs={'class': 'course-id'}).text.strip(),
                'course_title' : course_table.find(attrs={'class': 'class-list-course-title'}).text.strip(),
                'course_info' : course_info,
                'course_description' : course_table.find(attrs={'class': 'class-list-course-desc'}).text.strip(),
                'tickets': tickets,
                }
        courses.append(course)
        for section in course_table.find_all(attrs={'class': 'class-list-info-method'}):
            # Temp strings to parse out the different times and days for lecture and lab
            temp_time_str = section.find(attrs={'title': 'TIME'}).text.strip()
            temp_day_str = section.find(attrs={'title': 'DAY'}).text.strip()

            # First split is for getting the lec_day
            # The second and third split will get the lab_day
            temp_day_str_split = temp_day_str.find('(')
            temp_day_str_split2 = temp_day_str.find(')')
            temp_day_str_split3 = find_nth(temp_day_str, '(', 2)

            # This will split the two concatinated times into seperate values
            temp_time_str_split = find_nth(str(temp_time_str), ':',2)

            ticket = {
                    'number': section.find(attrs={'class': 'class-list-info-ticket'}).text.strip(),
                    'status': section.find(attrs={'class': 'class-list-info-status'}).text.strip(),

                    'lec_day': str(temp_day_str)[:temp_day_str_split].strip(),
                    'lab_day': str(temp_day_str)[temp_day_str_split2+1:temp_day_str_split3].strip(),

                    # These splits will split the lecture and lab times into seperate vals
                    'lec_time': str(temp_time_str)[:temp_time_str_split+3],
                    'lab_time': str(temp_time_str)[temp_time_str_split+3:],
                    'room': section.find(attrs={'class': 'class-list-room-text'}).text.strip(),

                    # (string)[6:] is needed to strip the 'person' icon text out of the <span> tag
                    'instructor': (section.find(attrs={'title': 'INSTRUCTOR'}).text.strip())[6:],
                    }
            tickets.append(ticket)
    return courses
#*******************************************************************************************************************



#*******************************************************************************************************************
def ticket_list(courses):
    tickets = []
    for course in courses:
        for ticket in course['tickets']:
            tickets.append(ticket['number'])
    return tickets
#*******************************************************************************************************************



#*******************************************************************************************************************
if __name__ == '__main__':
    courses = build_dict(url.format(year=year, semester=semester))
    import json

    # templateized so that the year and semester can easily be changed with globals
    cFileName = 'courses{year}-{semester}.json'
    with open(cFileName.format(year=year, semester=semester), 'w') as file:
        json.dump(courses, file, sort_keys=True, indent=4)

    # templateized so that the year and semester can easily be changed with globals
    tickets = ticket_list(courses)
    tFilename = 'tickets{year}-{semester}.txt'
    with open(tFilename.format(year=year, semester=semester), 'w') as file:
        file.write('\n'.join(tickets))
#*******************************************************************************************************************
