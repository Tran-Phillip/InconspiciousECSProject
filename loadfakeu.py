import os
import sys
import psycopg2 as pc
import re

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
                SEAT Integer,\
                SID Integer,\
                SURNAME VARCHAR(30),\
                PREFNAME VARCHAR(30),\
                LEVEL CHAR(2),\
                UNITS Integer,\
                CLASS VARCHAR(10),\
                MAJOR VARCHAR(4),\
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


    cur.execute("INSERT INTO course_tbl( CID,TERM,SUBJ,CRSE,SEC,UNITS)"\
                 "VALUES (" + CID + ',' + course_tuple[1] + ',\'' + course_tuple[2] + '\',' +  course_tuple[3] + \
                 ',' + course_tuple[4] + ',\''  + course_tuple[5] +"\');")

    cur.execute("INSERT INTO meetings_tbl( CID,INSTRUCTORS,TYPE,DAYS,TIMEE,BUILDING,ROOM)"\
                 "VALUES ("+ CID + ',\'' + meeting_tuple[0] + '\',\'' + meeting_tuple[1] + '\',\'' + meeting_tuple[2] + \
                  '\',\'' +  meeting_tuple[3] + '\',\'' + meeting_tuple[4] + '\',\''  + meeting_tuple[5] +"\');")

    for tuple in seating_tuple:
        cur.execute("INSERT INTO seating_tbl( CID, SEAT,SID, SURNAME, PREFNAME, LEVEL, UNITS,CLASS,MAJOR,GRADE,STATUS,EMAIL)"\
                     "VALUES ("+ CID + ',\'' + tuple[0] + '\',\'' + tuple[1] + '\',\'' + tuple[2] + \
                      '\',\'' +  tuple[3] + '\',\'' + tuple[4] + '\',\''  + tuple[5] +\
                      '\',\'' +  tuple[6] + '\',\'' + tuple[7] + '\',\''  + tuple[8] +\
                      '\',\'' +  tuple[9] + '\',\'' +\
                      "\');")

def make_equal(tuple, num_attributes):


    while(len(tuple) != 9):
        tuple.insert(0,'\'\'')

    return tuple

def parse_course(stream, num_attributes):
    ''' returns all information on the courses'''
    line = iter(stream).next()
    tuple = []

    if( len(line) == 3 ): # -> the line contains just '""'
        for num in range(0, num_attributes): # -> return a tuple full of nulls
            tuple.append("NULL")
        return tuple
    else:
        line = line.strip()
        tuple = re.split(r'[,\"]+', line)
        tuple = clean_up(tuple)

        tuple = replace_empty_with_null(tuple)

        tuple = tuple[0:num_attributes] # -> there are more columns than attributes for some reason

        iter(stream).next() # -> if there is a non-empty tuple in the file, then the next line read is an empty 'space' buffer
                          # -> so we will just ignore it and move onto the next category

    return tuple


def parse_file(csv_file, cur):
    '''parses the overall file and adds all the infomation into our tables '''
    count = 0 #remove me later

    stream = open(os.getcwd() + '/' + csv_file, 'r')  #FIXME: allow user to specify path
    iter(stream).next() # -> first line in file is always an empty tuple so we can just discard it

    for course_info in stream:
        course_tuple = parse_course(stream,6)
        meeting_tuple = parse_meetings(stream,6)
        seating_tuple = parse_seating(stream,11)

        insert_into_table(course_tuple, meeting_tuple, seating_tuple,cur);
        #print(course_tuple)


        count+=1 #remove me later

    cur.execute("SELECT * from meetings_tbl")
    all = cur.fetchall()
    for x in all:
        print(x)



def parse_meetings(stream, num_attributes):
    ''' returns information about the meetings'''

    attr_names = iter(stream).next()

    line = iter(stream).next()
    tuple = []

    if( len(line) == 3): # -> the line contains just '""'
        for num in range(0, num_attributes): # -> return a tuple full of nulls
            tuple.append("NULL")
        return tuple
    else:
        line = line.strip()
        #tuple = re.split(r'[,\"]+', line)
        tuple = line.split(',')

        if(tuple[0] != '\"\"'):
            tuple[0] = (tuple[0] + "," + tuple[1]) #reconstruct the name
            tuple.pop(1) #remove the extra attrbiute


        tuple = replace_empty_with_null(tuple)

        tuple = tuple[0:num_attributes]

        iter(stream).next() # -> if there is a non-empty tuple in the file, then the next line read is an empty 'space' buffer
                          # -> so we will just ignore it and move onto the next category

    return tuple

def parse_seating(stream, num_attributes):
    ''' returns a list of list containing each students information '''
    attr_names = iter(stream).next()
    tuple = [[]]
    line = iter(stream).next()

    while(len(line) > 3 ):
        line = line.strip()
        tuple2 = re.split(r'[,\"]+', line)
        tuple2 = clean_up(tuple2)
        tuple.append(tuple2)
        line = iter(stream).next()

    tuple.pop(0) # -> some reason first tuple is empty...?

    return tuple

def replace_empty_with_null(tuple):
    ''' finds and replaces all empty attributes with null'''
    refined_tuple = []
    for index in range(0, len(tuple)): #for some reason the regex split adds a '' to the begining and end of the tuple
                               # we will account for it here
        if(tuple[index] == "\"\"" or tuple[index] == ''):
            refined_tuple.append("NULL")
        else:
            refined_tuple.append(tuple[index])
    return refined_tuple


### Main()
if (len(sys.argv)==2):
    os.chdir(sys.argv[1])
load()
