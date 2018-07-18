""" A webscraper that scrapes essential info about any department's courses on
the Berkeley Academic Guide website: http://guide.berkeley.edu/ and generates
a summary table of all courses and their details, viewable in the browser. """

from bs4 import BeautifulSoup # Used for scraping Berkeley Academic Guide
from unicodedata import normalize # For keeping unicode characters intact
import urllib # Fetches Berkeley Academic Guide site
import pprint # Used to format and print scraped data nicely
from yattag import Doc, indent # Used to write a .html file pythonically
import webbrowser, os # For opening up the final .html summary file in the browser

# Stores a cache of all course codes and their summarized data
courseCache = {}

# Insert url to ANY Berkeley Academic Guide department here
url = "http://guide.berkeley.edu/courses/bio_eng/"

content = urllib.request.urlopen(url).read()
soup = BeautifulSoup(content, 'lxml')

# Finds every code block in the website that is a listing of a particular course
for listing in soup.find_all('div', class_='courseblock'):
    code = normalize('NFKD', listing.span.string)
    title = listing.find('span', class_='title')
    units = listing.find('span', class_='hours')
    description = listing.find('div', class_='coursebody').find('span', class_='descshow').contents
    terms = [s for (i, s) in list(enumerate(description)) if 'Terms' in s][0][15:].strip()
    """ Add preliminary info to courseCache. """
    courseCache[code] = {'Title': title.string,
                         'Units': units.string,
                         'Terms': terms}

    """ Parse all the additional details listed on site and extract essential info, namely:
        - prereqs, course level, grading, title, hours
        Add this info to courseCache """
    for details in listing.find_all('div', class_='course-section'):
        # data is a list of associated tags within a courseblock
        data = [text for text in details.stripped_strings]
        for d in data:
            index = data.index(d)
            if d in ['Prerequisites:', 'Grading:', \
                    'Grading/Final exam status:', 'Instructors:']:
                courseCache[code][d[:-1]] = data[index + 1].replace('<BR/>', ' ')
            elif d == 'Subject/Course Level:':
                value = data[index + 1]
                courseCache[code]['Level'] = value[value.index('/') + 1:]
            elif d == 'Hours & Format':
                courseCache[code][d] = data[index + 2]

pprint.pprint(courseCache) # Prints the dictionary contents to the terminal

html_file = open('test.html', 'w')

""" Generate .html file (using library yattag) to format scraped info as a summary table in the browser """
doc, tag, text = Doc().tagtext()
doc.asis('<DOCTYPE! html>')
with tag('html'):
    with tag('head'):
        with tag('title'): text('coursesummary')
        doc.asis('<link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">')
        doc.asis('<link href="style.css" type="text/css" rel="stylesheet">')
    with tag('body'):
        # Generate the table
        with tag('table', cellspacing='1'):
            # The header of the table
            with tag('thead'):
                with tag('th', scope="col"): text('Code')
                with tag('th', scope="col"): text('Title')
                with tag('th', scope="col"): text('Units')
                with tag('th', scope="col"): text('Terms')
                with tag('th', scope="col"): text('Prerequisites')
                with tag('th', scope="col"): text('Level')
                with tag('th', scope="col"): text('Grading')
                with tag('th', scope="col"): text('Hours and Format')
                with tag('th', scope="col"): text('Instructor(s)')
            with tag('tbody'):
                """ For each course in the courseCache, add the course's info as
                a row in the table """
                for code in courseCache:
                    with tag('tr'):
                        with tag('td'): text(code)
                        with tag('td'): text(courseCache[code]['Title'])
                        with tag('td'): text(courseCache[code]['Units'])
                        with tag('td'): text(courseCache[code]['Terms'])
                        if 'Prerequisites' in courseCache[code]:
                            with tag('td'): text(courseCache[code]['Prerequisites'])
                        else:
                            with tag('td'): text('n/a')
                        with tag('td'): text(courseCache[code]['Level'])
                        if 'Grading/Final exam status' in courseCache[code]:
                            with tag('td'): text(courseCache[code]['Grading/Final exam status'])
                        else:
                            with tag('td'): text(courseCache[code]['Grading'])
                        if 'Hours & Format' in courseCache[code]:
                            with tag('td'): text(courseCache[code]['Hours & Format'])
                        else:
                            with tag('td'): text('n/a')
                        if 'Instructors' in courseCache[code]:
                            with tag('td'): text(courseCache[code]['Instructors'])
                        else:
                            with tag('td'): text('n/a')

result = indent(doc.getvalue()) # Adds indents to help with readability in .html file
html_file.write(result) # Write the string generated above to the .html file; gets overwritten each time courseScraper.py is called
webbrowser.open('file://' + os.path.realpath('test.html')) # Open the file in the browser when courseScraper.py is called
