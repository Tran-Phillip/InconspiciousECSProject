import os
import sys
import psycopg2 as pc
import re
import csv

#######################################################################
#   Stuff we still need to do:
#   #TODO: restructure code to remove repetition
#   #FIXME: What is our primary key here?
########################################################################

def clean_up(tuple):
    '''removes extra '' at the begining and the end'''
    tuple.pop(0)
    tuple.pop(len(tuple) - 1)
    return tuple

def create_tables(cur):
    ''' initializes the tables. I think every table should have the CID since the CID seems to connect our entities together. We can change l8er though'''

    cur.execute("CREATE TABLE course_tbl (\
                CID Integer NOT NULL,\
                TERM Integer,\
                SUBJ CHAR(4),\
                CRSE Integer,\
                SEC Integer,\
                UNITS VARCHAR(20),\
                PRIMARY KEY (CID, TERM,CRSE,SEC)\
    );")

    #FIXME: What is our primary key here?
    cur.execute("CREATE TABLE meetings_tbl (\
                CID Integer,\
                TERM Integer,\
                INSTRUCTORS VARCHAR(50),\
                TYPE VARCHAR(30),\
                DAYS VARCHAR(30),\
                TIMEE VARCHAR(50),\
                BUILDING VARCHAR(50),\
                ROOM VARCHAR(10)\
    );")

    cur.execute("CREATE TABLE seating_tbl (\
                CID Integer,\
                TERM Integer,\
                SEAT VARCHAR(20),\
                SID VARCHAR(20),\
                SURNAME VARCHAR(30),\
                PREFNAME VARCHAR(30),\
                LEVEL CHAR(4),\
                UNITS real,\
                CLASS VARCHAR(10),\
                MAJOR VARCHAR(10),\
                GRADE VARCHAR(10),\
                STATUS VARCHAR(50),\
                EMAIL VARCHAR(50),\
                PRIMARY KEY(CID, TERM, SID)\
    );")

def load():
    ''' loads the program '''

    connection = pc.connect(database = "FakeUData")
    cur = connection.cursor()
    create_tables(cur)


    for files in os.listdir("."):
        if(files.endswith(".csv")):
            parse_file(files, cur)

    cur.execute("COMMIT;")

def insert_into_table(course_tuple, meeting_tuple, seating_tuple,cur): #FIXME: insert multiple tuples at a time rather than one at a time
    ''' inserts a set of tuples into their representive tables'''

    CID = course_tuple[0]
    TERM = course_tuple[1]
    if(CID == ""):
        CID = 'NULL'
    if(len(course_tuple) == 5):
        course_tuple.insert(NULL, 5)

    if(course_tuple[0] == '' and len(course_tuple) == 1): #-> empty tuple
        pass
    else:
        cur.execute("INSERT INTO course_tbl( CID,TERM,SUBJ,CRSE,SEC,UNITS)"\
                     "VALUES (" + CID + ',' + TERM + ',\'' + course_tuple[2] + '\',' +  course_tuple[3] + \
                     ',' + course_tuple[4] + ',\''  + course_tuple[5] +"\');")

    for tuple in meeting_tuple:
        cur.execute("INSERT INTO meetings_tbl(CID, TERM, INSTRUCTORS,TYPE,DAYS,TIMEE,BUILDING,ROOM)"\
                     "VALUES (" + CID + "," +  TERM +',\'' + tuple[0] + '\',\'' + tuple[1] + '\',\'' +  tuple[2] + \
                     '\',\'' + tuple[3] + '\',\''  + tuple[4] + "\'" + ',\'' + tuple[5]  +"\');")

    if(not seating_tuple):
        return

    for tuple in seating_tuple:
        cur.execute("INSERT INTO seating_tbl(CID, TERM,SEAT,SID,SURNAME,PREFNAME,LEVEL,UNITS,CLASS,MAJOR,GRADE,STATUS,EMAIL)"\
                    "VALUES (" + CID + "," + TERM + ',\'' + tuple[0] + '\',\'' + tuple[1] + '\',\'' +  tuple[2] + \
                    '\',\'' + tuple[3] + '\',\''  + tuple[4] + "\'" + ',\'' + tuple[5] + '\',\'' \
                     + tuple[6] + '\',\''  + tuple[7] + "\'" + ',\'' + tuple[8] + '\',\'' + tuple[9] + '\',\''  + tuple[10]\
                     + "\') ;")
#ON DUPLICATE DO NOTHING
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
        if('\'' in tuple[0]):
            tuple[0] = tuple[0].replace('\'','_')
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
        if('\'' in tuple[2]):
            tuple[2] = tuple[2].replace('\'', '_')
        if('\'' in tuple[10]):
            tuple[10] = tuple[10].replace('\'', '_')
        if(tuple[5]==""):
            tuple[5]='0'
        seating_tuple.append(tuple)
        try:
            tuple = next(csvreader)
        except:
            return



    return seating_tuple

def replace_empty_with_null(tuple):
    ''' finds and replaces all empty attributes with null'''
    refined_tuple = []
    for index in range(0, len(tuple)):

        if(tuple[index] == ''):
            refined_tuple.append("NULL")
        else:
            refined_tuple.append(tuple[index])
    return refined_tuple


### Main()
if (len(sys.argv)==2):
    os.chdir(sys.argv[1])
load()
