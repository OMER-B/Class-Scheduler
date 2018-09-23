from utils import Course, Week, hours, days, semesters, database, file
import sqlite3
import sys, webbrowser, os


def create_database():
    # create a database connection
    conn = create_connection(database)
    if conn is not None:
        # create projects table
        cn = conn.cursor()
        return cn
    else:
        print("Error! cannot create the database connection.")


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except:
        print("Error!")

    return None


def query(cn):
    sys.stdout = open(file, 'w')  # Change stdout to file
    for s in semesters:
        week = Week()
        for d in days:
            for h in hours:
                cn.execute(
                    "SELECT DISTINCT * from courses WHERE start <= ? AND finish > ? and semester = ? and day = ? and groupe < 10",
                    (h, h, s, d))
                for r in cn:
                    course = Course().fromSQL(r)
                    day = week.getDayAt(d)
                    hour = day.getHourAt(h)
                    hour.addCourse(course)

        week.toHTML("HTML")
    webbrowser.open('file://' + os.path.realpath(file))  # open file


def main():
    cn = create_database()
    query(cn)


if __name__ == '__main__':
    main()
