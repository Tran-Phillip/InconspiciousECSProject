import os
import sys
import psycopg2 as pc
import re

#######################################################################
#   Stuff we still need to do:
########################################################################

def convert_grades(grade):
    if(grade == 'A'):
        return 4.0
    elif(grade == 'A-'):
        return 3.7
    elif(grade == 'B+'):
        return 3.3
    elif(grade == 'B'):
        return 3.0
    elif(grade == 'B-'):
        return 2.7
    elif(grade == 'C+'):
        return 2.3
    elif(grade == 'C'):
        return 2.0
    elif(grade == 'C-'):
        return 1.7
    elif(grade == 'D+'):
        return 1.3
    elif(grade == 'D'):
        return 1.0
    elif(grade == 'D-'):
        return .7
    else:
        return 0

def load():
    ''' loads the program '''

    connection = pc.connect(database = "FakeUData")
    cur = connection.cursor()

    for files in os.listdir("."):
        if(files.endswith(".txt")):
            execute_queries(files, cur)

def execute_queries(files,cur):

    query_3a(cur)
    #query_3b(cur)
    #query_3c(cur)

def query_3a(cur):

    term = []
    total_percent = []
    total_count = []


    cur.execute("SELECT COUNT(DISTINCT SID) FROM seating_tbl GROUP BY TERM")
    total_count = cur.fetchall()
    print(total_count) #count of unique student in each quarter

    for i in range(0,21):
        cur.execute("\
SELECT TERM,COUNT(*) FROM(SELECT TERM,SID,SUM(UNITS) \
FROM seating_tbl \
GROUP BY TERM,SID,UNITS HAVING SUM(UNITS)="+str(i)+" \
ORDER BY TERM) AS FOO GROUP BY TERM")
        term.append(cur.fetchall())

    for i in range(0,len(term)):
        print("UNITS: ", i)
        print(term[i])	

# this looks like it's giving proper data but the issue is that it doesn't input 0 if there's nobody that year so the alignment gets screwed up... not sure what the best way to fix this is....


#99% sure that total is not done efficiently... also this missing about 1600 records which I believe are students that had a SID defined but not units or something like that and some are definitely just people who are >20 units
#        print(total_percent)

'''
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
'''


def query_3b(cur):
    grades_dir = {}
    count_dir = {}

    cur.execute("CREATE TABLE gpa_tbl(NAME VARCHAR(30), GPA REAL)")
    cur.execute("SELECT s.CID,s.SID,s.GRADE,m.INSTRUCTORS\
    from seating_tbl AS s\
    INNER JOIN meetings_tbl as m ON m.CID = s.CID AND m.TERM = s.TERM\
    WHERE s.GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F')\
    ")
    res = cur.fetchall()
    for el in res:
        if(el[3] == 'NULL'):
            continue
        if(el[3] in grades_dir):
            grades_dir[el[3]] += convert_grades(el[2])
            count_dir[el[3]] += 1
        else:
            grades_dir[el[3]] = convert_grades(el[2])
            count_dir[el[3]] = 1

    for key in grades_dir:
        cur.execute("INSERT INTO gpa_tbl( NAME, GPA)"\
                    "VALUES (\'" + key+ '\',\'' + str(round(grades_dir[key] / count_dir[key],3)) + "\')")
    cur.execute("SELECT NAME, GPA\
                FROM gpa_tbl\
                WHERE GPA = (SELECT MAX(GPA) FROM gpa_tbl)\
                ")

    res = cur.fetchall()
    print("Best Profs: ")
    for x in res:
        print(x)

    cur.execute("SELECT NAME, GPA\
                FROM gpa_tbl\
                WHERE GPA = (SELECT MIN(GPA) FROM gpa_tbl)\
                ")
    res2 = cur.fetchall()
    print("Worst Profs: ")
    for el in res2:
        print(el)


def query_3c(cur):

    for units in range(1,20):
        total_GPA = 0
        cur.execute("SELECT SID, PREFNAME, GRADE FROM seating_tbl\
                     WHERE UNITS ="+ str(units)+" AND GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F')")

        res = cur.fetchall()
        for x in res:
            total_GPA += convert_grades(x[2])
        cur.execute("SELECT COUNT(GRADE) FROM seating_tbl\
                                                WHERE UNITS ="+str(units)+" AND GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F')")
        count = cur.fetchall()

        if(count[0][0] == 0):
            print("Nobody taking " + str(units) +" units for a grade!")
            continue

        avg_gpa = total_GPA / count[0][0]
        print("The average GPA for " + str(units) + " units is: ", str(round(avg_gpa,2)))


### Main()
if (len(sys.argv)==2):
    os.chdir(sys.argv[1])
load()
