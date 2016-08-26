'''
This part takes care of scrubbing data out of rate my professor and set it up
as a CSV file which can then be used for data analysis purposes
'''
import urllib2
import json
import unicodecsv as csv

id = 45
dept = 'Computer+Science'
rows = 200
start = 0
SchoolName = 'Arizona+State+University'
Professor_url = "http://search.mtvnservices.com/typeahead/suggest/?solrformat=true\
&rows=10&callback=noCB&q=*%3A*+AND+schoolid_s%3A{id}+AND+teacherdepartment_s\
%3A%22{dept}%22&defType=edismax&qf=teacherfullname_t%5E1000+\
autosuggest&bf=pow(total_number_of_ratings_i%2C2.1)&sort=total_number_of_\
ratings_i+desc&siteName=rmp&rows={rows}&start={start}&fl=pk_id+teacherfirstname_t+\
teacherlastname_t+total_number_of_ratings_i+averageratingscore_rf+schoolid_s&\
prefix=schoolname_t%3A%22{SchoolName}%22"

rating_url = 'http://www.ratemyprofessors.com/paginate/professors/ratings?\
tid={id}&page={page}'


def getRequest(url):
    return urllib2.urlopen(url).read()


def createPYObj(data):
    return json.loads(data)


def writeToCSV(data, fileName):
    keys = data[0].keys()
    # See if file name can be parameterised
    with open(fileName, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def pullUniversityInfo():
    returnedRowCount = 200
    returnData = []
    startLocal = start
    while(returnedRowCount == rows):
        data = getRequest(Professor_url.format(id=id, dept=dept, rows=rows,
                                               start=startLocal,
                                               SchoolName=SchoolName)
                          ).replace('noCB(', '').replace(');', '')
        startLocal += rows
        data = createPYObj(data)
        returnedRowCount = data['response']['numFound']
        returnData.extend(data['response']['docs'])
    return returnData


def pullRatingInformation(professors):
    data = []
    for prof in professors:
        page = 0
        remaining = 1
        while remaining != 0:
            temp = createPYObj(getRequest(rating_url.format(
                                                        id=prof['pk_id'],
                                                        page=page)))
            for obj in temp['ratings']:
                obj['TeacherID'] = prof['pk_id']
            data.extend(temp['ratings'])
            remaining = temp['remaining']
            page += 1
    return data


if __name__ == "__main__":
    # Fetch data about all the professors
    professorNames = pullUniversityInfo()
    ratings = pullRatingInformation(professorNames)
    writeToCSV(professorNames, 'professors.csv')
    writeToCSV(ratings, 'ratings.csv')
