import random
import re
import string

from selenium import webdriver

import utils
from utils import Course, database
import sqlite3
import sys

def fill_database(current_courses, cn):
    for c in current_courses:
        for i, dummy in enumerate(c.hour):
            cn.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                       (c.code, c.name, c.group, c.lecturers[0], c.type, c.semester, c.day[i], c.start[i],
                        c.finish[i], c.duration[i], c.building[i], c.room[i]))


def get_exams():
    conn = create_connection(utils.get_db())
    cn = conn.cursor()
    cn.execute("DROP TABLE IF EXISTS exams;")
    sql_create_projects_table = """CREATE TABLE IF NOT EXISTS exams (
                                        code text KEY,
                                        name text,
                                        moedADate text,
                                        moedAHour text,
                                        moedBDate text,
                                        moedBHour text);
                                        """
    cn.execute(sql_create_projects_table)

    cn.execute("SELECT DISTINCT code, name from courses")
    driver = webdriver.Chrome()
    list = cn.fetchall()
    for result in list:
        driver.get("https://shoham.biu.ac.il/BiuCoursesViewer/MainPage.aspx")
        elem = driver.find_element_by_id("ContentPlaceHolder1_txLessonCode")
        elem.clear()
        elem.send_keys(result[0])
        elem = driver.find_element_by_id("ContentPlaceHolder1_btnSearch").click()
        elem = driver.find_element_by_id("ContentPlaceHolder1_gvLessons_lnkDetails_0").click()
        trs = driver.find_elements_by_xpath("//tr[@align=\"center\"]")
        moeds = [None] * 2
        date = [None] * 2
        hour = [None] * 2
        curr_moed = []
        for i, moed in enumerate(trs):
            curr_moed = moed.text.split(" ")
            date[i] = curr_moed[2]
            hour[i] = (curr_moed[3])
        cn.execute("INSERT INTO exams VALUES (?, ?, ?, ?, ?, ?);",
                   (result[0], result[1], date[0], hour[0], date[1], hour[1]))
    conn.commit()
    driver.close()


def create_database(current_courses):
    sql_create_projects_table = """ CREATE TABLE if not exists courses (
                                        code text KEY,
                                        name text,
                                        groupe text KEY,
                                        lecturer text,
                                        type text,
                                        semester text,
                                        day text KEY,
                                        start INTEGER KEY,
                                        finish INTEGER,
                                        duration INTEGER,
                                        building INTEGER,
                                        room INTEGER
                                    ); """

    # create a database connection
    conn = create_connection(utils.get_db())
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
    except:
        print("some error in create_connection()")

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
        for i, row in enumerate(trs):
            trs = driver.find_elements_by_xpath("//tr[@align=\"center\"]")
            row = trs[i]
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
            elem = driver.find_elements_by_xpath(
                ".//a[contains(@id, 'ContentPlaceHolder1_gvLessons_lnkDetails')]")[i].click()
            trs_inner = driver.find_element_by_xpath("//td[@id='ContentPlaceHolder1_tdBuilding']")
            for line in trs_inner.text.split('\n'):
                current_course.building.append(''.join(ch for ch in line if ch.isdigit()))
            trs_inner = driver.find_element_by_xpath("//td[@id='ContentPlaceHolder1_tdRoom']")
            for line in trs_inner.text.split('\n'):
                current_course.room.append(''.join(ch for ch in line if ch.isdigit()))
            if (len(current_course.room) == 1):
                current_course.room.append(current_course.room[0])
            if (len(current_course.building) == 1):
                current_course.building.append(current_course.building[0])
            current_course.get_duration()
            current_courses.append(current_course)
            driver.back()
    driver.close()
    create_database(current_courses)


def main():
    generate_courses(sys.argv[1:])
    # get_exams()


if __name__ == '__main__':
    main()
