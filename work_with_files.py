import sqlite3
import xml.etree.ElementTree as Et
import datetime
import os
import random


def new_datebase():
    conn = sqlite3.connect("enterprise.db")
    cursor = conn.cursor()

    cursor.execute(f"""CREATE TABLE employee (name text, department text, position text, salary_per_hour int,
                    hours_in_day int)""")
    cursor.execute(f"""CREATE TABLE department (name text, caption text, employees text,
                    num_of_emp int)""")
    cursor.execute(f"""CREATE TABLE position (name text, caption text, employees text, num_of_pos int, 
                    department text)""")
    cursor.execute(f"""CREATE TABLE files (appointment text, name text, filename text)""")
    cursor.execute(f"""CREATE TABLE report_cards (name text, department text, position text, date text, hours int)""")
    cursor.execute(f"""CREATE TABLE result_salary (name text, department text, position text, salary int)""")


class WorkWithXML:
    def new_xml_file(self, filename: str):
        with open(filename, "w", encoding="utf-8") as file:
            file.write("<Order> </Order>")
        tree = Et.ElementTree(file=filename)
        root = Et.Element("Order")
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        return filename

    def new_order(self, appointment: str, name_emp: str, department: str, position: str):
        file = self.new_xml_file("file" + str(random.randint(10**3, 10**5)) + ".xml")
        tree = Et.ElementTree(file=file)
        root = tree.getroot()
        Et.SubElement(root, "appointment").text = appointment
        Et.SubElement(root, "name_of_employee").text = name_emp
        Et.SubElement(root, "department").text = department
        Et.SubElement(root, "position").text = position
        tree.write(file, encoding="utf-8", xml_declaration=True)
        return file

    def delete_file(self, filename: str):
        if filename.endswith(".xml"):
            os.remove(filename)
            return 0
        else:
            raise ValueError("the file must be in .xml format")


class WorkWithDB:
    def __init__(self):
        self.conn = sqlite3.connect("enterprise.db")
        self.cursor = self.conn.cursor()
        self.conn.row_factory = sqlite3.Row
        self._work_with_xml = WorkWithXML()

    def add_employee(self, name: str, department: str, position: str, salary: int, hours_in_day: int) -> str:
        self.cursor.execute(f"""INSERT INTO employee VALUES (?,?,?,?,?)""",
                            (name, department, position, salary, hours_in_day))
        self.conn.commit()
        filename = self._work_with_xml.new_order("Прийняття робітника", name, department, position)
        self.add_file("Прийняття робітника", name, filename)
        return f"Робітника: {name} успішно зараховано на посаду: {position} в підрозділі: {department} !"

    def add_department(self, name: str, caption: str, employees_name: list, num_of_emp: int) -> str:
        emp_names = ""
        for i in employees_name:
            emp_names += i + " "
        self.cursor.execute(f"""INSERT INTO department VALUES (?,?,?,?)""", (name, caption, emp_names, num_of_emp))
        self.conn.commit()
        return f"Підрозділ: {name} успішно створено !"

    def add_position(self, name: str, caption: str, employees: list, num_of_pos: int, department: str) -> str:
        names = ""
        for i in employees:
            names += i + " "
        self.cursor.execute(f"""INSERT INTO position VALUES (?,?,?,?,?)""",
                            (name, caption, names, num_of_pos, department))
        self.conn.commit()
        return f"Посаду: {name}, в підрозділі {department} успішно додано!"

    def add_report_card(self, name: str, department: str, position: str, date: str, hours: int) -> str:
        self.cursor.execute(f"""INSERT INTO report_cards VALUES (?,?,?,?,?)""",
                            (name, department, position, date, hours))
        self.conn.commit()
        return f"Інформацію про роботу парцівника: {name} за дату: {date} додано!"

    def add_file(self, appointment: str, name, filename: str) -> None:
        self.cursor.execute(f"""INSERT INTO files VALUES (?,?,?)""", (appointment, name, filename))
        self.conn.commit()

    def add_result_card(self, name: str, department: str, position: str) -> str:
        month = datetime.date.month
        sql = f"""SELECT * FROM employee WHERE name = ? and department = ? and position = ?"""
        salary_per_hour = self.cursor.execute(sql, (name, department, position)).fetchone()[3]
        sql2 = f"""SELECT * FROM report_cards WHERE name = ? and department = ? and position = ?"""
        hours = self.cursor.execute(sql2, (name, department, position)).fetchall()
        hours_to_pay = 0
        for i in hours:
            if i[3].split("-") == month:
                hours_to_pay += int(i[4])
        salary = hours_to_pay * int(salary_per_hour)
        self.cursor.execute(f"""INSERT INTO result_salary VALUES (?,?,?,?)""", (name, department, position, salary))
        self.conn.commit()
        return f"Зарплату робітника: {name} успішно розраховано: {salary} грн"

    def update_employee(self, name: str, department: str, position: str, salary: int, hours_in_day: int) -> str:
        sql = f"""UPDATE employee 
        SET department = ?, position = ?, salary_per_hour = ?, hours_in_day = ? 
        WHERE name = ?"""
        self.cursor.execute(sql, (department, position, salary, hours_in_day, name))
        self.conn.commit()
        filename = self._work_with_xml.new_order("Переведення на посаду", name, department, position)
        self.add_file("Переведення на посаду", name, filename)
        return f"Інформацію про робітника: {name} успішно поновлено!"

    def update_department(self, name: str, caption: str, employees_name: list, num_of_emp: int) -> str:
        emp_names = ""
        for i in employees_name:
            emp_names += i + " "
        sql = f"""UPDATE department SET caption = ?, employees = ?, num_of_emp = ? WHERE name = ?"""
        self.cursor.execute(sql, (caption, emp_names, num_of_emp, name))
        self.conn.commit()
        return f"Інформацію про підрозділ: {name} успішно поновлено!"

    def update_position(self, name: str, caption: str, employees: list, num_of_pos: int, department: str) -> str:
        names = ""
        for i in employees:
            names += i + " "
        sql = f"""UPDATE position SET caption = ?, employees = ?, num_of_pos = ?, department = ? WHERE name = ?"""
        self.cursor.execute(sql, (caption, names, num_of_pos, department, name))
        self.conn.commit()
        return f"Інформацію про посаду: {name} успішно поновлено!"

    def update_report_card(self, name: str, department: str, position: str, date: str, hours: int) -> str:
        sql = f"""UPDATE report_cards SET  department = ?, position = ?, date = ?, hours = ? WHERE name = ?"""
        self.cursor.execute(sql, (department, position, date, hours, name))
        self.conn.commit()
        return f"інформацію про робітника: {name} успішно поновлено!"

    def update_result_card(self, name: str, department: str, position: str) -> str:
        month = datetime.date.month
        sql = f"""SELECT * FROM employee WHERE name = ? and department = ? and position = ?"""
        salary_per_hour = self.cursor.execute(sql, (name, department, position)).fetchone()[3]
        sql2 = f"""SELECT * FROM report_cards WHERE name = ? and department = ? and position = ?"""
        hours = self.cursor.execute(sql2, (name, department, position)).fetchall()
        hours_to_pay = 0
        for i in hours:
            if i[3].split("-") == month:
                hours_to_pay += int(i[4])
        salary = hours_to_pay * int(salary_per_hour)
        sql3 = f"""UPDATE result_salary SET salary = ?, department = ?, position = ? WHERE name = ? """
        self.cursor.execute(sql3, (salary, department, position, name))
        self.conn.commit()
        return f"Зарплату робітника: {name} успішно пере розраховано: {salary} грн"

    def get_info_about_department(self, name: str) -> tuple:
        info = self.cursor.execute(f"""SELECT * FROM department WHERE name = ?""", (name,)).fetchone()
        return info

    def get_info_about_employee(self, name: str) -> tuple:
        info = self.cursor.execute(f"""SELECT * FROM employee WHERE name = ?""", (name,)).fetchone()
        return info

    def get_info_about_position(self, name: str) -> tuple:
        info = self.cursor.execute(f"""SELECT * FROM position WHERE name = ?""", (name,)).fetchone()
        return info

    def get_info_about_report_cards(self, name: str) -> list:
        info = self.cursor.execute(f"""SELECT * FROM report_cards WHERE name = ?""", (name,)).fetchall()
        return info

    def get_info_about_result_card(self, name: str) -> tuple:
        info = self.cursor.execute(f"""SELECT * FROM result_salary WHERE name = ?""", (name,)).fetchone()
        return info

    def get_info_about_file(self, appointment: str, name: str) -> tuple:
        info = self.cursor.execute(f"""SELECT * FROM files WHERE appointment = ? and name = ?""",
                                   (appointment, name)).fetchone()
        return info

    def get_all_employees_names(self) -> list:
        info = self.cursor.execute(f"""SELECT * FROM employee""").fetchall()
        return [i[0] for i in info]

    def get_all_employees_names_by_dep(self, department: str) -> list:
        info = self.cursor.execute(f"""SELECT * FROM employee WHERE department = ?""", (department,)).fetchall()
        return [i[0] for i in info]

    def get_all_departments_names(self) -> list:
        info = self.cursor.execute(f"""SELECT * FROM department""").fetchall()
        return [i[0] for i in info]

    def get_all_position_names(self) -> list:
        info = self.cursor.execute(f"""SELECT * FROM position""").fetchall()
        return [i[0] for i in info]

    def get_all_files(self) -> list:
        filenames = self.cursor.execute(f"""SELECT * FROM files""")
        return [i[2] for i in filenames]

    def delete_employee(self, name: str) -> str:
        info_about_emp = self.get_info_about_employee(name)
        self.cursor.execute(f"""DELETE FROM employee WHERE name = ?""", (name,))
        self.cursor.execute(f"""DELETE FROM report_cards WHERE name = ?""", (name,))
        self.cursor.execute(f"""DELETE FROM files WHERE name = ?""", (name,))
        self.cursor.execute(f"""DELETE FROM result_salary WHERE name = ?""", (name,))
        self.conn.commit()
        info_about_dep = self.get_info_about_department(info_about_emp[1])
        employees_names = self.get_all_employees_names()
        self.update_department(info_about_dep[0], info_about_dep[1], employees_names, len(employees_names))
        info_about_pos = self.get_info_about_position(info_about_emp[2])
        self.update_position(info_about_pos[0], info_about_pos[1], employees_names, len(employees_names),
                             info_about_dep[0])
        filename = self._work_with_xml.new_order("Звільнення", name, info_about_dep[0], info_about_pos[0])
        self.add_file("Звільнення", name, filename)
        return f"Робітника: {name} успішно видалено!"

    def delete_position(self, name: str, department: str) -> str:
        info_about_emp = self.cursor.execute(f"""SELECT * FROM employee WHERE department = ? and position = ?""",
                                             (department, name)).fetchall()
        for i in info_about_emp:
            self.delete_employee(i[0])
        self.cursor.execute(f"""DELETE FROM position WHERE name = ? and department = ?""", (name, department))
        self.conn.commit()
        return f"Посаду: {name} з підрозділу: {department} успішно видалено!"

    def delete_department(self, name: str) -> str:
        self.cursor.execute(f"""DELETE FROM department WHERE name = ?""", (name,))
        self.cursor.execute(f"""DELETE FROM employee WHERE department = ?""", (name,))
        self.cursor.execute(f"""DELETE FROM position WHERE department = ?""", (name,))
        self.cursor.execute(f"""DELETE FROM report_cards WHERE department = ?""", (name,))
        self.cursor.execute(f"""DELETE FROM result_salary WHERE department = ?""", (name,))
        self.conn.commit()
        return f"Підрозділ: {name} успішно видалено!"

    def delete_file(self, appointment: str, name: str) -> str:
        self.cursor.execute(f"""DELETE FROM files WHERE appointment = ? and name = ?""", (appointment, name))
        self.conn.commit()
        return f"Наказ на: {appointment} для: {name} видалено успішно!"


if __name__ == '__main__':
    new_datebase()
