import os
import sys
import psycopg2 as pc
import re
import csv

#######################################################################
#   Stuff we still need to do:
#   #FIXME: maybe change time into the actual time datatype
#   #FIXME: Fix parsing so that it actually scans the integers and as integers instead of everything as strings
#   #TODO:  Test this shit on larger datasets to see how fast it runs
#   #FIXME: insert multiple tuples at a time rather than one at a time
#   #TODO: restructure code to remove repetition
########################################################################

def clean_up(tuple):
    '''removes extra '' at the begining and the end'''
    tuple.pop(0)
    tuple.pop(len(tuple) - 1)
    return tuple

def create_tables(cur):
    ''' initializes the tables. I think every table should have the CID since the CID seems to connect our entities together. We can change l8er though'''

    #FIXME: actually figure out how large everything is lol.
    cur.execute("CREATE TABLE course_tbl (\
                CID Integer,\
                TERM Integer,\
                SUBJ CHAR(4),\
                CRSE Integer,\
                SEC Integer,\
                UNITS VARCHAR(20)\
    );")

    #FIXME: maybe change time into the actual time datatype
    cur.execute("CREATE TABLE meetings_tbl (\
                CID Integer,\
                INSTRUCTORS VARCHAR(50),\
                TYPE VARCHAR(20),\
                DAYS VARCHAR(20),\
                TIMEE VARCHAR(50),\
                BUILDING VARCHAR(20),\
                ROOM VARCHAR(10)\
    );")

    cur.execute("CREATE TABLE seating_tbl (\
                CID Integer,\
                SEAT VARCHAR(20),\
                SID VARCHAR(20),\
                SURNAME VARCHAR(30),\
                PREFNAME VARCHAR(30),\
                LEVEL CHAR(4),\
                UNITS VARCHAR(20),\
                CLASS VARCHAR(10),\
                MAJOR VARCHAR(10),\
                GRADE VARCHAR(10),\
                STATUS VARCHAR(50),\
                EMAIL VARCHAR(30)\
    );")

def load():
    ''' loads the program '''

    connection = pc.connect(database = "FakeUData")
    cur = connection.cursor()
    create_tables(cur)


    for files in os.listdir("."):
        if(files.endswith(".csv")):
            parse_file(files, cur)

def insert_into_table(course_tuple, meeting_tuple, seating_tuple,cur): #FIXME: insert multiple tuples at a time rather than one at a time
    ''' inserts a set of tuples into their representive tables'''

    CID = course_tuple[0]
    if(len(course_tuple) == 5):
        course_tuple.insert(NULL, 5)

    cur.execute("INSERT INTO course_tbl( CID,TERM,SUBJ,CRSE,SEC,UNITS)"\
                 "VALUES (" + CID + ',' + course_tuple[1] + ',\'' + course_tuple[2] + '\',' +  course_tuple[3] + \
                 ',' + course_tuple[4] + ',\''  + course_tuple[5] +"\');")


def make_equal(tuple, num_attributes):


    while(len(tuple) != 9):
        tuple.insert(0,'\'\'')

    return tuple

def parse_course(csvreader):
    ''' returns all information on the courses'''
    tuple = next(csvreader)

    if(len(tuple) != 1): # not an empty tuple
        next(csvreader) #discard the newline

    return tuple


def parse_file(csv_file, cur):
    '''parses the overall file and adds all the infomation into our tables '''

    fields = []
    rows = []
    # reading csv file
    print(csv_file)
    with open(csv_file, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)

        # extracting field names through first row
        next(csvreader)
        # extracting each data row one by one
        for row in csvreader:
            course_tuple = parse_course(csvreader)
            meeting_tuple = parse_meetings(csvreader)
            seating_tuple = parse_seating(csvreader)
            insert_into_table(course_tuple, meeting_tuple, seating_tuple, cur)

            #print(course_tuple)


        # get total number of rows
        print("Total no. of rows: %d"%(csvreader.line_num))



def parse_meetings(csvreader):
    ''' returns information about the meetings'''
    meeting_tuple = []
    try:
        header = next(csvreader)
        tuple = next(csvreader)
    except:
        return meeting_tuple

    while(tuple[0] != "" or len(tuple) != 1):
        tuple = replace_empty_with_null(tuple)
        meeting_tuple.append(tuple)
        try:
            tuple = next(csvreader)
        except:
            return



    return meeting_tuple

def parse_seating(csvreader):
    '''returns a list of list with the seating info'''

    seating_tuple = []
    try:
        header = next(csvreader)
        tuple = next(csvreader)
    except:
        return seating_tuple

    while(tuple[0] != ""):
        seating_tuple.append(tuple)
        try:
            tuple = next(csvreader)
        except:
            return



    return seating_tuple

def replace_empty_with_null(tuple):
    ''' finds and replaces all empty attributes with null'''
    refined_tuple = []
    for index in range(0, len(tuple)): #for some reason the regex split adds a '' to the begining and end of the tuple
                               # we will account for it here
        if(tuple[index] == ''):
            refined_tuple.append("NULL")
        else:
            refined_tuple.append(tuple[index])
    return refined_tuple


### Main()
if (len(sys.argv)==2):
    os.chdir(sys.argv[1])
load()
