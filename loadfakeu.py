import os
import sys
import psycopg2 as pc


#######################################################################
#   Stuff we still need to do:
#   #FIXME: actually figure out how large everything is lol.
#   #FIXME: maybe change time into the actual time datatype
#   #TODO: inserting the seating tuple as well
#   #FIXME: Fix parsing so that it actually scans the integers and as integers instead of everything as strings
#   #TODO:  Test this shit on larger datasets to see how fast it runs
#   #FIXME: insert multiple tuples at a time rather than one at a time
#   #TODO: restructure code to remove repetition
########################################################################


def create_tables(cur):
    ''' initializes the tables. I think every table should have the CID since the CID seems to connect our entities together. We can change l8er though'''

    #FIXME: actually figure out how large everything is lol.
    cur.execute("CREATE TABLE course_tbl (\
                CID CHAR(20),\
                TERM CHAR(20),\
                SUBJ CHAR(20),\
                CRSE VARCHAR(20),\
                SEC VARCHAR(20),\
                UNITS VARCHAR(20)\
    );")

    #FIXME: maybe change time into the actual time datatype
    cur.execute("CREATE TABLE meetings_tbl (\
                CID CHAR(20),\
                INSTRUCTORS VARCHAR(50),\
                TYPE VARCHAR(20),\
                DAYS VARCHAR(20),\
                TIMEE VARCHAR(50),\
                BUILDING VARCHAR(20),\
                ROOM VARCHAR(20)\
    );")

    cur.execute("CREATE TABLE seating_tbl (\
                CID VARCHAR(20),\
                SEAT VARCHAR(20),\
                SID VARCHAR(20),\
                SURNAME VARCHAR(30),\
                PREFNAME VARCHAR(30),\
                LEVEL VARCHAR(20),\
                UNITS VARCHAR(20),\
                CLASS VARCHAR(2),\
                MAJOR VARCHAR(4),\
                GRADE VARCHAR(2),\
                STATUS VARCHAR(2),\
                EMAIL VARCHAR(30)\
    );")

def load(dir_name):
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
    TERM = course_tuple[1]
    SUBJ = course_tuple[2]
    CSRE = course_tuple[3]
    SEC = course_tuple[4]
    UNITS = course_tuple[5]

    cur.execute("INSERT INTO course_tbl( CID,TERM,SUBJ,CRSE,SEC,UNITS)"\
                 "VALUES (\'" + CID + '\',\'' + TERM + '\',\'' + SUBJ + '\',\'' +  CSRE + '\',\'' + SEC + '\',\''  + UNITS +"\');")

    cur.execute("INSERT INTO meetings_tbl( CID,INSTRUCTORS,TYPE,DAYS,TIMEE,BUILDING,ROOM)"\
                 "VALUES (\'"+ CID + '\',\'' + meeting_tuple[0] + '\',\'' + meeting_tuple[1] + '\',\'' + meeting_tuple[2] + \
                  '\',\'' +  meeting_tuple[3] + '\',\'' + meeting_tuple[4] + '\',\''  + meeting_tuple[5] +"\');")

    #TODO: inserting the seating tuple as well


def parse_course(stream, num_attributes):
    ''' returns all information on the courses'''
    line = stream.readline()
    tuple = []

    if( len(line) == 3 ): # -> the line contains just '""'
        for num in range(0, num_attributes): # -> return a tuple full of nulls
            tuple.append("NULL")
        return tuple
    else:
        line = line.strip()
        tuple = line.split(',')
        tuple = tuple[0:num_attributes ] # -> there are more columns than attributes for some reason
        tuple = replace_empty_with_null(tuple)
        stream.readline() # -> if there is a non-empty tuple in the file, then the next line read is an empty 'space' buffer
                          # -> so we will just ignore it and move onto the next category

    return tuple


def parse_file(csv_file, cur):
    '''parses the overall file and adds all the infomation into our tables '''
    count = 0 #remove me later

    stream = open("./testing/" + csv_file, 'r')  #FIXME: allow user to specify path
    stream.readline() # -> first line in file is always an empty tuple so we can just discard it

    for course_info in stream:
        if(count == 3):# -> use this to control how many iterations you want to run. good for debugging.

            ##this is just to test if everything is put into the database correctly
            cur.execute("SELECT * from course_tbl")
            all = cur.fetchall()

            for x in all:
                print(x)

            sys.exit(1)
            ###

        #FIXME: Fix parsing so that it actually scans the integers and as integers instead of everything as strings
        course_tuple = parse_course(stream,6)
        meeting_tuple = parse_meetings(stream,6)
        seating_tuple = parse_seating(stream,11)
        insert_into_table(course_tuple, meeting_tuple, seating_tuple,cur);

        count+=1 #remove me later


def parse_meetings(stream, num_attributes):
    ''' returns information about the meetings'''

    attr_names = stream.readline()

    line = stream.readline()
    tuple = []

    if( len(line) == 3): # -> the line contains just '""'
        for num in range(0, num_attributes): # -> return a tuple full of nulls
            tuple.append("NULL")
        return tuple
    else:
        line = line.strip()
        tuple = line.split(',')

        if(tuple[0] != '\"\"'):
            tuple[0] = (tuple[0] + "," + tuple[1]) #reconstruct the name
            tuple.pop(1) #remove the extra attrbiute
            tuple = tuple[0:num_attributes]

        tuple = replace_empty_with_null(tuple)
        stream.readline() # -> if there is a non-empty tuple in the file, then the next line read is an empty 'space' buffer
                          # -> so we will just ignore it and move onto the next category

    return tuple

def parse_seating(stream, num_attributes):
    ''' returns a list of list containing each students information '''
    attr_names = stream.readline()
    tuple = []
    line = stream.readline()

    while(len(line) > 3 ):
        line = line.strip()
        line = line.split(',')
        tuple.append(line)
        line = stream.readline()

    return tuple

def replace_empty_with_null(tuple):
    ''' finds and replaces all empty attributes with null'''
    refined_tuple = []
    for index in range(0, len(tuple)):
        if(tuple[index] == "\"\"" or tuple[index] == ''):
            refined_tuple.append("NULL")
        else:
            refined_tuple.append(tuple[index])
    return refined_tuple

### Main()
if (len(sys.argv)==2):
    load(sys.argv[1])
else:
    load(os.getcwd())
