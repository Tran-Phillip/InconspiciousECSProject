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

    #query_3a(cur)
    #query_3b(cur)
    #query_3c(cur)
    #query_3d(cur)
    query_3e(cur)
    #query_3f(cur)
    #query_3g(cur)
    #query_3h(cur)
def query_3a(cur):

    term = []
    total_percent = []
    total_count = []


    # cur.execute("SELECT COUNT(DISTINCT SID) FROM seating_tbl GROUP BY TERM")
    # total_count = cur.fetchall()
    # print(total_count) #count of unique student in each quarter
    for i in range(0,21):
        print("UNITS: ",str(i))
        cur.execute("SELECT TERM,CAST(C AS FLOAT) / CAST(C1 AS FLOAT) AS PR FROM \
                    ((SELECT COUNT(t.SID) AS C,TERM FROM\
                        (select DISTINCT(SID),TERM FROM seating_tbl GROUP BY SID,TERM HAVING SUM(UNITS) =" +str(i) +") AS T\
                        GROUP BY TERM ORDER BY TERM) \
                    ) AS T1\
                    NATURAL JOIN\
                    (SELECT COUNT(DISTINCT SID) AS C1, TERM FROM seating_tbl GROUP BY TERM) AS T2\
                    GROUP BY TERM, C, C1 ORDER BY TERM\
                    ")


        res = cur.fetchall()
        for x in res:
            print(x)

# this looks like it's giving proper data but the issue is that it doesn't input 0 if there's nobody that year so the alignment gets screwed up... not sure what the best way to fix this is....


#99% sure that total is not done efficiently... also this missing about 1600 records which I believe are students that had a SID defined but not units or something like that and some are definitely just people who are >20 units
#        print(total_percent)


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

    for units in range(1,21): #range was off and this should be broken since 3a was done wrong but I don't exactly see where it's doing anything with the terms...
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

def query_3d(cur):
    print("Highest Pass Rates!")


    cur.execute("SELECT CID,TERM, PR FROM \
                (SELECT CID, TERM, (CAST(T AS FLOAT) / CAST(T2 AS FLOAT)) PR FROM\
                    (SELECT CID,TERM, COUNT(SID) AS T FROM seating_tbl\
                    WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-')\
                     GROUP BY CID,TERM HAVING COUNT(SID) > 1\
                     ORDER BY CID\
                     ) AS PASSING_COUNT\
                     NATURAL JOIN\
                     (SELECT CID, TERM, COUNT(SID) AS T2 FROM seating_tbl\
                     GROUP BY CID,TERM HAVING COUNT(SID) > 1\
                     ORDER BY CID\
                 ) AS NON_PASSING_COUNT) AS FU WHERE PR = (SELECT MAX(PR) FROM \
                    (SELECT CID, TERM, (CAST(T AS FLOAT) / CAST(T2 AS FLOAT)) PR FROM\
                        (SELECT CID,TERM, COUNT(SID) AS T FROM seating_tbl\
                        WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-')\
                         GROUP BY CID,TERM HAVING COUNT(SID) > 1\
                         ORDER BY CID\
                         ) AS PASSING_COUNT\
                         NATURAL JOIN\
                         (SELECT CID, TERM, COUNT(SID) AS T2 FROM seating_tbl\
                         GROUP BY CID,TERM HAVING COUNT(SID) > 1\
                         ORDER BY CID\
                     ) AS NON_PASSING_COUNT) AS FU2\
                 )\
                 ")

    res = cur.fetchall()
    for el in res:
        print(el)

    print("Lowest Pass Rates!")
    cur.execute("SELECT CID,TERM, PR FROM \
                (SELECT CID, TERM, (CAST(T AS FLOAT) / CAST(T2 AS FLOAT)) PR FROM\
                    (SELECT CID,TERM, COUNT(SID) AS T FROM seating_tbl\
                    WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-','P')\
                     GROUP BY CID,TERM HAVING COUNT(SID) > 1\
                     ORDER BY CID\
                     ) AS PASSING_COUNT\
                     NATURAL JOIN\
                     (SELECT CID, TERM, COUNT(SID) AS T2 FROM seating_tbl\
                     WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'P', 'NP','NS')\
                     GROUP BY CID,TERM HAVING COUNT(SID) > 1\
                     ORDER BY CID\
                 ) AS NON_PASSING_COUNT) AS FU WHERE PR = (SELECT MIN(PR) FROM \
                    (SELECT CID, TERM, (CAST(T AS FLOAT) / CAST(T2 AS FLOAT)) PR FROM\
                        (SELECT CID,TERM, COUNT(SID) AS T FROM seating_tbl\
                        WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'P')\
                         GROUP BY CID,TERM HAVING COUNT(SID) > 1\
                         ORDER BY CID\
                         ) AS PASSING_COUNT\
                         NATURAL JOIN\
                         (SELECT CID, TERM, COUNT(SID) AS T2 FROM seating_tbl\
                         WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F','P','NP','NS')\
                         GROUP BY CID,TERM HAVING COUNT(SID) > 1\
                         ORDER BY CID\
                     ) AS NON_PASSING_COUNT) AS FU2\
                 )\
                 ")


    res = cur.fetchall()
    for el in res:
        print(el)
def query_3e(cur):
    cur.execute("SELECT CID,TERM,INSTRUCTORS,DAYS,TIMEE FROM\
                (select CID,TERM,INSTRUCTORS,DAYS,TIMEE FROM meetings_tbl) AS T1 \
                NATURAL JOIN\
                (SELECT CID,TERM,INSTRUCTORS,DAYS,TIMEE FROM meetings_tbl) AS T2 \
                WHERE T1.DAYS = T2.DAYS \
                 as A \
                ")
    x=cur.fetchall()
    print(x)
#AND T1.TIMEE = T2.TIMEE AND T1.INSTRUCTOR=T2.INSTRUCTOR
#                 select CID,TERM,INSTRUCTOR,DAYS,TIMES AS T2 FROM meetings_tbl \
def query_3f(cur):
    print("Best Majors FOR ABC")
    cur.execute("SELECT MAJOR, GPA FROM\
                (SELECT MAJOR, AVG(CONVERTED_GRADE) AS GPA FROM\
                (select CID,TERM,SUBJ FROM course_tbl WHERE SUBJ = 'ABC') AS Course_tbl\
                NATURAL JOIN\
                (select CID,TERM,MAJOR,GRADE,CONVERTED_GRADE FROM seating_tbl WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F','P','NP','NS')) As Seat_tbl\
                GROUP BY MAJOR ORDER BY MAJOR) AS tbl WHERE GPA = (SELECT MAX(GPA) FROM (SELECT MAJOR, AVG(CONVERTED_GRADE) AS GPA FROM\
                (select CID,TERM,SUBJ FROM course_tbl WHERE SUBJ = 'ABC') AS Course_tbl\
                NATURAL JOIN\
                (select CID,TERM,MAJOR,GRADE,CONVERTED_GRADE FROM seating_tbl WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F','P','NP','NS')) As Seat_tbl\
                GROUP BY MAJOR ORDER BY MAJOR) AS TEST)\
    ")
    res = cur.fetchall()
    for el in res:
        print(el)

    print("WORST Majors FOR ABC")
    cur.execute("SELECT MAJOR, GPA FROM\
                (SELECT MAJOR, AVG(CONVERTED_GRADE) AS GPA FROM\
                (select CID,TERM,SUBJ FROM course_tbl WHERE SUBJ = 'ABC') AS Course_tbl\
                NATURAL JOIN\
                (select CID,TERM,MAJOR,GRADE,CONVERTED_GRADE FROM seating_tbl WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F','P','NP','NS')) As Seat_tbl\
                GROUP BY MAJOR ORDER BY MAJOR) AS tbl WHERE GPA = (SELECT MIN(GPA) FROM (SELECT MAJOR, AVG(CONVERTED_GRADE) AS GPA FROM\
                (select CID,TERM,SUBJ FROM course_tbl WHERE SUBJ = 'ABC') AS Course_tbl\
                NATURAL JOIN\
                (select CID,TERM,MAJOR,GRADE,CONVERTED_GRADE FROM seating_tbl WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F','P','NP','NS')) As Seat_tbl\
                GROUP BY MAJOR ORDER BY MAJOR) AS TEST)\
    ")
    res = cur.fetchall()
    for el in res:
        print(el)

    print("Best Majors FOR DEF")
    cur.execute("SELECT MAJOR, GPA FROM\
                (SELECT MAJOR, AVG(CONVERTED_GRADE) AS GPA FROM\
                (select CID,TERM,SUBJ FROM course_tbl WHERE SUBJ = 'DEF') AS Course_tbl\
                NATURAL JOIN\
                (select CID,TERM,MAJOR,GRADE,CONVERTED_GRADE FROM seating_tbl WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F','P','NP','NS')) As Seat_tbl\
                GROUP BY MAJOR ORDER BY MAJOR) AS tbl WHERE GPA = (SELECT MAX(GPA) FROM (SELECT MAJOR, AVG(CONVERTED_GRADE) AS GPA FROM\
                (select CID,TERM,SUBJ FROM course_tbl WHERE SUBJ = 'DEF') AS Course_tbl\
                NATURAL JOIN\
                (select CID,TERM,MAJOR,GRADE,CONVERTED_GRADE FROM seating_tbl WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F','P','NP','NS')) As Seat_tbl\
                GROUP BY MAJOR ORDER BY MAJOR) AS TEST)\
    ")
    res = cur.fetchall()
    for el in res:
        print(el)

    print("WORST Majors FOR DEF")
    cur.execute("SELECT MAJOR, GPA FROM\
                (SELECT MAJOR, AVG(CONVERTED_GRADE) AS GPA FROM\
                (select CID,TERM,SUBJ FROM course_tbl WHERE SUBJ = 'DEF') AS Course_tbl\
                NATURAL JOIN\
                (select CID,TERM,MAJOR,GRADE,CONVERTED_GRADE FROM seating_tbl WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F','P','NP','NS')) As Seat_tbl\
                GROUP BY MAJOR ORDER BY MAJOR) AS tbl WHERE GPA = (SELECT MIN(GPA) FROM (SELECT MAJOR, AVG(CONVERTED_GRADE) AS GPA FROM\
                (select CID,TERM,SUBJ FROM course_tbl WHERE SUBJ = 'DEF') AS Course_tbl\
                NATURAL JOIN\
                (select CID,TERM,MAJOR,GRADE,CONVERTED_GRADE FROM seating_tbl WHERE GRADE IN ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F','P','NP','NS')) As Seat_tbl\
                GROUP BY MAJOR ORDER BY MAJOR) AS TEST)\
    ")
    res = cur.fetchall()
    for el in res:
        print(el)

def query_3g(cur):
    cur.execute("SELECT t.MAJOR, COUNT(t.MAJOR) FROM seating_tbl t, seating_tbl t2\
    WHERE t.SID = t2.SID AND t.MAJOR not like 'ABC%' AND t2.MAJOR like 'ABC%' AND t.TERM > t2.TERM\
    GROUP BY t.MAJOR ORDER BY COUNT(t.MAJOR)\
    ")
    res = cur.fetchall()
    print("Top 5 Majors who transfered to ABC: ")
    top_5 = [res[-5:]]


    cur.execute("SELECT t.SID FROM seating_tbl t, seating_tbl t2\
    WHERE t.SID = t2.SID AND t.MAJOR <> t2.MAJOR AND t.TERM > t2.TERM AND t.MAJOR > t2.MAJOR\
    ")
    res = cur.fetchall()
    total_transfer = len(res)

    for i in range(1,6):
        print(top_5[0][-1 * i][0], float(top_5[0][-1 * i][1] / float(total_transfer)))

def query_3h(cur):
    cur.execute("SELECT t2.MAJOR, COUNT(t2.MAJOR) FROM seating_tbl t, seating_tbl t2\
    WHERE t.SID = t2.SID AND t.MAJOR like 'ABC%' AND t2.MAJOR not like 'ABC%' AND t.TERM > t2.TERM\
    GROUP BY t2.MAJOR ORDER BY COUNT(t2.MAJOR)\
    ")
    res = cur.fetchall()


    print("Top 5 Majors who transfered FROM ABC: ")
    top_5 = [res[-5:]]

    cur.execute("SELECT t.SID FROM seating_tbl t, seating_tbl t2\
    WHERE t.SID = t2.SID AND t.MAJOR <> t2.MAJOR AND t.TERM > t2.TERM AND t.MAJOR > t2.MAJOR\
    ")
    res = cur.fetchall()
    total_transfer = len(res)

    for i in range(1,6):
        print(top_5[0][-1 * i][0], float(top_5[0][-1 * i][1] / float(total_transfer)))



### Main()
if (len(sys.argv)==2):
    os.chdir(sys.argv[1])
load()
