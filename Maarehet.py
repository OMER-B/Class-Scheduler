import re

from selenium import webdriver
from utils import Course, database
import sqlite3
import sys


def fill_database(current_courses, cn):
    for c in current_courses:
        for i, dummy in enumerate(c.hour):
            cn.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                       (c.code, c.name, c.group, c.lecturers[0], c.type, c.semester, c.day[i], c.start[i],
                        c.finish[i], c.duration[i]))


def create_database(current_courses):
    sql_create_projects_table = """ CREATE TABLE courses (
                                        code text KEY,
                                        name text,
                                        groupe text KEY,
                                        lecturer text,
                                        type text,
                                        semester text,
                                        day text KEY,
                                        start INTEGER KEY,
                                        finish INTEGER,
                                        duration INTEGER
                                    ); """

    # create a database connection
    conn = create_connection(database)
    if conn is not None:
        # create projects table
        cn = conn.cursor()
        cn.execute(sql_create_projects_table)
        fill_database(current_courses, cn)
        conn.commit()

    else:
        print("Error! cannot create the database connection.")


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def generate_courses(courses):
    driver = webdriver.Chrome()
    current_courses = []
    for course in courses:
        driver.get("https://shoham.biu.ac.il/BiuCoursesViewer/MainPage.aspx")
        elem = driver.find_element_by_id("ContentPlaceHolder1_txLessonCode")
        elem.clear()
        elem.send_keys(course)
        elem = driver.find_element_by_id("ContentPlaceHolder1_btnSearch").click()
        trs = driver.find_elements_by_xpath("//tr[@align=\"center\"]")
        for row in trs:
            current_course = Course()
            # get the text from all the td's from each row
            for td in row.find_elements_by_xpath(".//td/span"):
                if (td.find_elements_by_xpath(
                        "..//span[contains(@id, 'ContentPlaceHolder1_gvLessons_lblLessonCode')]")):  # ID
                    current_course.code = td.text
                elif (td.find_elements_by_xpath(
                        "..//span[contains(@id, 'ContentPlaceHolder1_gvLessons_lblLessonname')]")):  # Name
                    current_course.name = td.text
                elif (td.find_elements_by_xpath(
                        "..//span[contains(@id, 'ContentPlaceHolder1_gvLessons_lblGroupCode')]")):  # Group
                    current_course.group = td.text
                elif (td.find_elements_by_xpath(
                        "..//span[contains(@id, 'ContentPlaceHolder1_gvLessons_lblTeacher')]")):  # Teacher
                    for line in td.text.split('\n'):
                        current_course.lecturers.append(line)
                elif (td.find_elements_by_xpath(
                        "..//span[contains(@id, 'ContentPlaceHolder1_gvLessons_lblSessionType')]")):  # Type
                    current_course.type = td.text
                elif (td.find_elements_by_xpath(
                        "..//span[contains(@id, 'ContentPlaceHolder1_gvLessons_lblSemester')]")):  # Semester
                    current_course.semester = td.text
                elif (td.find_elements_by_xpath(
                        "..//span[contains(@id, 'ContentPlaceHolder1_gvLessons_lblSesssionDay')]")):  # Days
                    for line in td.text.split('\n'):
                        current_course.day.append(line)
                elif (td.find_elements_by_xpath(
                        "..//span[contains(@id, 'ContentPlaceHolder1_gvLessons_lblSessionHours')]")):  # Hours
                    for line in td.text.split('\n'):
                        current_course.hour.append(line)

            current_course.get_duration()
            current_courses.append(current_course)
    driver.close()
    create_database(current_courses)


def main():
    generate_courses(sys.argv[1:])


if __name__ == '__main__':
    main()
