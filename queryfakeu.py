import os
import sys
import psycopg2 as pc
import re

#######################################################################
#   Stuff we still need to do:
########################################################################

def load():
    ''' loads the program '''

    connection = pc.connect(database = "FakeUData")
    cur = connection.cursor()

    for files in os.listdir("."):
        if(files.endswith(".txt")):
            execute_queries(files, cur)

def execute_queries(files,cur):

    query_3a(cur)

    '''
    query = ""
    with open(files, 'r') as q_file:
        for line in q_file:
            query+=line
    query = query.replace('\n','')
    query = query.replace('\t','')
    print(query)
    cur.copy_expert(query, sys.stdout)

    '''

def query_3a(cur):

    term = []
    count_shit = []
    total_count_shit = []


    for i in range(0,20):
        print("UNITS: ", i)
        cur.execute("SELECT COUNT(foo.UNITS) , TERM FROM (SELECT UNITS,TERM FROM seating_tbl WHERE UNITS =" + str(i) + ") AS foo\
          GROUP BY foo.TERM\
          ORDER BY foo.TERM"
        )

        x = cur.fetchall()

        for el in x:
            count_shit.append(el[0])
            term.append(el[1])

        cur.execute("SELECT COUNT(UNITS), TERM from seating_tbl\
          GROUP BY TERM\
          ORDER BY TERM"
        )

        x2 = cur.fetchall()

        for el in x2:
            total_count_shit.append(el[0])

        for index in range(0,len(count_shit)):
            percentage = float(count_shit[index]) / float(total_count_shit[index])
            print(term[index], percentage)

        term = []
        count_shit = []
        total_count_shit = []



### Main()
if (len(sys.argv)==2):
    os.chdir(sys.argv[1])
load()
