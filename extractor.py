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

def build_dict(url):
    # The page has a dangling /div
    # Python's html.parser doesn't handle this adequately, so we need html5lib
    soup = BeautifulSoup(urlopen(url).read(), "html5lib")

    courses = []
    course_tables = soup.find_all(attrs={'class': 'class-list-course-list'})
    for course_table in course_tables:
        tickets = []
        course = {
                'course_id': course_table.find(attrs={'class': 'course-id'}).text.strip(),
                'course_title' : course_table.find(attrs={'class': 'class-list-course-title'}).text.strip(),
                #FIXME split up Units and Prerequisites
                'course_info' : course_table.find(attrs={'class': 'class-list-course-info'}).text.strip(),
                'course_description' : course_table.find(attrs={'class': 'class-list-course-desc'}).text.strip(),
                'tickets': tickets,
                }
        courses.append(course)
        for section in course_table.find_all(attrs={'class': 'class-list-info-method'}):
            ticket = {
                    'number': section.find(attrs={'class': 'class-list-info-ticket'}).text.strip(),
                    'status': section.find(attrs={'class': 'class-list-info-status'}).text.strip(),
                    #FIXME split up lecture/lab in the following three fields
                    # instead of strings, these should be dicts with
                    # {'lecture': ..., 'lab': ...}
                    'day': section.find(attrs={'title': 'DAY'}).text.strip(),
                    'time': section.find(attrs={'title': 'TIME'}).text.strip(),
                    'room': section.find(attrs={'class': 'class-list-room-text'}).text.strip(),
                    #FIXME remove the "person" icon text
                    'instructor': section.find(attrs={'title': 'INSTRUCTOR'}).text.strip(),
                    }
            tickets.append(ticket)

    return courses

def ticket_list(courses):
    tickets = []
    for course in courses:
        for ticket in course['tickets']:
            tickets.append(ticket['number'])
    return tickets

if __name__ == '__main__':
    courses = build_dict(url.format(year=year, semester=semester))
    import json
    with open('courses.json', 'w') as f:
        json.dump(courses, f, sort_keys=True, indent=4)
    tickets = ticket_list(courses)
    with open('tickets.txt', 'w') as f:
        f.write('\n'.join(tickets))

