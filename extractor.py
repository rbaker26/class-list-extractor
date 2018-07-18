#!/usr/bin/env python3
from bs4 import BeautifulSoup
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
def build_dict(url):
    # The page has a dangling /div
    # Python's html.parser doesn't handle this adequately, so we need html5lib
    soup = BeautifulSoup(urlopen(url).read(), "html5lib")

    # remove all icon tags
    for icons in soup.find_all(class_='material-icons'):
        icons.decompose()

    courses = []
    course_tables = soup.find_all(attrs={'class': 'class-list-course-list'})
    for course_table in course_tables:

        tickets = []

        # Clean up the prereq data
        prereq = course_table.find(class_='class-list-prereq')
        if prereq:
            prereq = prereq.text.strip()
            if prereq.startswith('Prerequisite: '):
                prereq = prereq.lstrip('Prerequisite: ')

        course_info = {
            'units' : course_table.find(attrs={'class': 'class-list-unit'}).text.strip()[7:],
            'prereq': prereq,
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
            
            # remove all small tags
            for smalls in section.find_all(class_='ins-method'):
                smalls.decompose()
            class_days = section.find(attrs={'title': 'DAY'})
            class_days = list(class_days)

            class_times = list(section.find(attrs={'title': 'TIME'}).children)
            
            # Seperate Lab and Lecture Rooms
            lec_room = section.find(class_='class-list-room-text')
            lab_room = lec_room.find(class_='extra-room')
            # None-check for lab attrabutes
            if lab_room:
                lab_room.extract()
                lab_room = lab_room.text.strip()

            # If lab is in the same room as lecture
            if lab_room == None and class_times[-1].strip():
                lab_room = lec_room.text.strip()


            lecture = {
                'day':class_days[0].strip(),
                'time':class_times[0].strip(),
                'room': lec_room.text.strip(),
            }
            lab = { 
                'day':class_days[-1].strip(),
                'time':class_times[-1].strip(),
                'room': lab_room,
            }
            ticket = {
                    'number': section.find(attrs={'class': 'class-list-info-ticket'}).text.strip(),
                    'status': section.find(attrs={'class': 'class-list-info-status'}).text.strip(),
                    'lecture': lecture,
                    'lab': lab,                   
                    'instructor': (section.find(attrs={'title': 'INSTRUCTOR'}).text.strip()),
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
