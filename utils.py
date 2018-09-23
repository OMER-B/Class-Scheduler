semesters = ["סמסטר א'", "סמסטר ב'"]
days = ["ו'", "ה'", "ד'", "ג'", "ב'", "א'"]  # ["א'", "ב'", "ג'", "ד'", "ה'", "ו'"]
hours = [i for i in range(8, 20)]
colors = ["#fcfcfc", "#f7f7f7"]
database = "my.db"
file = 'file.html'

class Course:
    def __init__(self):
        self.code = ''
        self.name = ''
        self.group = ''
        self.lecturers = []
        self.type = ''
        self.semester = ''
        self.day = []
        self.hour = []
        self.duration = []
        self.start = []
        self.finish = []

    def get_duration(self):
        if (len(self.hour) != len(self.day)):
            self.day.append(self.day[0])
        try:
            for i, h in enumerate(self.hour):
                start, end = h.split(' - ')
                self.start.append(int(start.split(':')[0]))
                self.finish.append(int(end.split(':')[0]))
                self.duration.append(self.finish[i] - self.start[i])
        except:
            self.duration.append("")
            self.start.append("")
            self.finish.append("")

    def toHtml(self):
        return "<span style=\"font-size: 13px;\">" + self.code + "-" + self.group + "</span>" \
               + "<br />" \
               + "<span style=\"font-weight:bold; font-size:16px;\">" + self.name + " - " + self.type + "</span>" \
               + "<br />" \
               + "<span style =\"font-size: 13px;\">" + self.lecturers.__str__() + "</span>"

    def fromSQL(self, sql):
        self.code = sql[0]
        self.name = sql[1]
        self.group = sql[2]
        self.lecturers = sql[3]
        self.type = sql[4]
        self.semester = sql[5]
        self.day = sql[6]
        self.start = sql[7]
        self.finish = sql[8]
        self.duration = sql[9]
        return self

    def getColor(self):
        return self.name.__hash__()


class Hour:
    def __init__(self):
        self.courses = []

    def addCourse(self, course):
        self.courses.append(course)

    id = 0

    def toHTML(self):
        str = "<tr>"
        for c in self.courses:
            str += "<td style=\"background-color:#" + hex(c.getColor())[3:9] \
                   + "; text-align:center; border-radius: 5px;\" id=\"" \
                   + Hour.id.__str__() \
                   + "\" onclick=\"myFunction(this.id)\" ondblclick=\"myFunction2(this.id)\">" \
                   + c.toHtml() \
                   + "</td>"
            Hour.id = Hour.id + 1
        str += "</tr>"
        return str


class Day:
    def __init__(self):
        self.hours = [Hour() for hour in range(25)]

    def getHourAt(self, hour):
        return self.hours[hour]

    def dayToNum(day):
        if day == "א'":
            return 1
        elif day == "ב'":
            return 2
        elif day == "ג'":
            return 3
        elif day == "ד'":
            return 4
        elif day == "ה'":
            return 5
        elif day == "ו'":
            return 6
        else:
            return 0


class Week:
    def __init__(self):
        self.days = [Day() for x in range(7)]

    def getDayAt(self, day):
        return self.days[Day.dayToNum(day)]

    def toHTML(self, num):
        print("<html>")
        print(HTMLScripts())
        print ("<body>"
               "<table style=\"text-align: right; font-family: calibri;\">")
        for i, hour in enumerate(hours):
            if (i == 0):
                print("<tr>")
                print("<td>")
                print("</td>")
                for day in days:
                    print("<td align=\"center\" style=\"font-weight: bold;\">")
                    print("יום " + day)
                    print("</td>")
                print("</tr>")
                print("<tr>")

            for j, day in enumerate(days):
                if (j == 0):
                    print("<td>")
                    print(str(hour) + ":00")
                    print("</td>")
                print("<td style=\"background-color:" + colors[i % 2 == 0] + ";\" align=\"right\">")
                print("<table style=\"text-align: right; height: 120px;\" width=\"100%\">")
                print(self.getDayAt(day).getHourAt(hour).toHTML())
                print("</table>")
                print("</td>")
            print("</tr>")

        print("</table></body></html>")


def HTMLScripts():
    return "<script>" \
           "function myFunction(id) {" \
           "    if (document.getElementById(id).style.opacity === \"0.3\"){" \
           "        document.getElementById(id).style.opacity = \"1\";" \
           "    } else {" \
           "        document.getElementById(id).style.opacity = \"0.3\"" \
           "    }" \
           "}" \
           "</script>" \
           "<script>" \
           "function myFunction2(id) {" \
           "    document.getElementById(id).style.display=\"none\"" \
           "}" \
           "</script>"
