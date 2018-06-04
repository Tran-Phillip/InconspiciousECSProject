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
    query = ""
    with open(files, 'r') as q_file:
        for line in q_file:
            query+=line
    query = query.replace('\n','')
    query = query.replace('\t','')
    print(query)
    cur.copy_expert(query, sys.stdout)


### Main()
if (len(sys.argv)==2):
    os.chdir(sys.argv[1])
load()
