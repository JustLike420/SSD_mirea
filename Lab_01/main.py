import json
import os
import psutil
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class Student:
    firstname: str
    lastname: str
    middlename: str
    age: str

    def __str__(self):
        return f"Студент: {self.firstname} {self.lastname} {self.middlename}, Возраст: {self.age}"


@dataclass
class Group:
    name: str
    students: list[Student] = field(default_factory=list)

    def show(self):
        print("Группа: " + self.name)
        for student in self.students:
            print(student)

    def __str__(self):
        return "Группа: " + self.name


def is_file_exist(func):
    def wrapper(*args, **kwargs):
        file_name = args[1]
        if not os.path.exists(file_name):
            print("Файл не найден", file_name)
            return None
        return func(*args, **kwargs)
    return wrapper


class DiskManager:
    def __init__(self):
        self.disks = psutil.disk_partitions()

    def get_info(self):
        for disk in self.disks:
            print(f"Имя диска: {disk.device}")
            print(f"Метка тома: {disk.mountpoint}")
            try:
                partition_usage = psutil.disk_usage(disk.mountpoint)
                print(f"Размер: {partition_usage.total / (1024 ** 3):.2f} GB")
                print(f"Свободное место: {partition_usage.free / (1024 ** 3):.2f} GB")
                print(f"Тип файловой системы: {disk.fstype}\n")
            except Exception as e:
                print(f"Ошибка при получении информации: {str(e)}\n")


class FileManager:
    @is_file_exist
    def read_file(self, path):
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
        return text

    def write(self, path, text: str):
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)

    def create(self, path, text=""):
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        print("Файл создан")

    @is_file_exist
    def delete(self, path):
        os.remove(path)


class ArchiveManager(FileManager):
    def create_with_file(self, path, filename):
        with zipfile.ZipFile(path, "w") as file:
            file.write(filename)
        zip_file_info = os.stat(path)
        print(f"Размер архива '{path}': {zip_file_info.st_size} байт")

    @is_file_exist
    def extract_file(self, path, filename):
        with zipfile.ZipFile(path, "a") as file:
            try:
                file.extract(filename)
            except Exception as e:
                print(e)

        self.read_file(filename)


class JsonManager(FileManager):
    def save(self, filename, data):
        data = json.dumps(data, default=lambda o: o.__dict__, indent=4)
        self.write(filename, data)

    def read(self, filename):
        with open(filename, "r") as file:
            json_data = file.read()
            loaded_groups = json.loads(json_data)
            if loaded_groups:
                for group in loaded_groups:
                    print(f"Группа: {group['name']}")
                    for student in group["students"]:
                        print(
                            f"  Студент: {student['firstname']} {student['lastname']} {student['middlename']}, Возраст: {student['age']}"
                        )


class XmlManager(FileManager):
    def save(self, filename, data):
        root = ET.Element("Groups")

        for group in data:
            group_elem = ET.SubElement(root, "Group")
            name_elem = ET.SubElement(group_elem, "name")
            name_elem.text = group.name

            students_elem = ET.SubElement(group_elem, "students")
            for student in group.students:
                student_elem = ET.SubElement(students_elem, "Student")
                first_name_elem = ET.SubElement(student_elem, "firstname")
                first_name_elem.text = student.firstname
                last_name_elem = ET.SubElement(student_elem, "lastname")
                last_name_elem.text = student.lastname
                middle_name_elem = ET.SubElement(student_elem, "middlename")
                middle_name_elem.text = student.middlename
                age_elem = ET.SubElement(student_elem, "age")
                age_elem.text = student.age

        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8")

    def read(self, filename):
        try:
            tree = ET.ElementTree(file=filename)
            root = tree.getroot()

            if root.tag == "Groups":
                for group_elem in root.findall("Group"):
                    group = Group(group_elem.find("name").text)

                    students_elem = group_elem.find("students")
                    if students_elem is not None:
                        for student_elem in students_elem.findall("Student"):
                            student = Student(
                                student_elem.find("firstname").text,
                                student_elem.find("lastname").text,
                                student_elem.find("middlename").text,
                                student_elem.find("age").text,
                            )
                            group.students.append(student)

                    print(f"Группа: {group.name}")
                    for student in group.students:
                        print(
                            f"  Студент: {student.firstname} {student.lastname} {student.middlename}, Возраст: {student.age}"
                        )
            else:
                print("Ошибка при загрузке данных из файла XML.")
        except FileNotFoundError:
            print(f"Файл '{filename}' не найден.")
        except ET.ParseError:
            print(f"Ошибка при разборе данных из файла '{filename}'.")


def get_file_name(message="Введите название файла: ", extension=""):
    filename = input(message)
    if filename == "":
        return "file" + "." + extension
    if "." + extension not in filename and extension != "":
        return filename + "." + extension
    return filename


class Cmd:
    def file_cmd(self):
        file_manager = FileManager()
        while True:
            print(
                "~~~ Работа с файлами ~~~\n"
                "1. Создать файл\n"
                "2. Записать информацию в файл\n"
                "3. Прочитать файл\n"
                "4. Удалить файл\n"
            )
            choice = input("Выбор: ")
            if choice == "1":
                file_manager.create(get_file_name(extension="txt"))
                print("Файл создан")
            elif choice == "2":
                file_manager.write(
                    get_file_name(extension="txt"), input("Введите текст для записи: ")
                )
                print("Текст записан в файл")
            elif choice == "3":
                print('Содержимое файла:\n', file_manager.read_file(get_file_name(extension="txt")))
            elif choice == "4":
                file_manager.delete(get_file_name(extension="txt"))
                print("Файл удален")
            else:
                print('Некорректный выбор. Пожалуйста, введите номер действия из списка.')

    def archive_cmd(self):
        archive_manager = ArchiveManager()
        while True:
            print(
                "~~~ Работа с архивами ~~~\n"
                "1. Создать архив и добавить файл\n"
                "2. Разархивировать файл и вывести данные\n"
                "3. Удалить архив\n"
            )
            choice = input("Выбор: ")
            if choice == "1":
                filename = get_file_name()
                archive_name = get_file_name(
                    message="Введите название архива. Enter - пропустить",
                    extension="zip",
                )
                archive_manager.create_with_file(archive_name, filename)
                print("Архив создан")
            elif choice == "2":
                filename = get_file_name()
                archive_name = get_file_name(
                    message="Введите название архива. Enter - пропустить",
                    extension="zip",
                )
                if archive_name == "":
                    archive_name = "archive.zip"
                archive_manager.extract_file(archive_name, filename)
            elif choice == "3":
                archive_manager.delete(get_file_name(extension="zip"))
                print("Файл удален")
            else:
                print('Некорректный выбор. Пожалуйста, введите номер действия из списка.')

    def json_cmd(self):
        json_manager = JsonManager()
        groups = []
        while True:
            print(
                "~~~ Работа с JSON ~~~\n"
                "1. Создать файл\n"
                "2. Записать в файл\n"
                "3. Прочитать файл\n"
                "4. Удалить файл"
            )

            choice = input("Выбор: ")
            if choice == "1":
                json_manager.create(get_file_name(extension="json"), text="[]")

            elif choice == "2":
                filename = get_file_name(extension="json")
                while True:
                    print(
                        "~~~ Добавление данных ~~~\n"
                        "1. Добавить группу\n"
                        "2. Добавить студента\n"
                        "3. Сохранить"
                    )
                    choice = input("Выбор: ")
                    if choice == "1":
                        group = Group(input("Название: "), [])
                        groups.append(group)
                        print(f"Группа {group.name} добавлена")
                    elif choice == "2":
                        for i, group in enumerate(groups):
                            print(f"[{i}] {group}\n")
                        group_index = input("Выберите группу (index)")
                        student = Student(
                            input("Имя: "),
                            input("Фамилия: "),
                            input("Отчество: "),
                            input("Возраст: "),
                        )
                        groups[int(group_index)].students.append(student)
                        print(f"Студент {student.firstname} добавлен в группу {groups[int(group_index)].name}")
                    elif choice == "3":
                        json_manager.save(filename, groups)
                        print("Информацию сохранена в файл")
                        break
            elif choice == "3":
                json_manager.read(get_file_name(extension="json"))
            elif choice == "4":
                json_manager.delete(get_file_name(extension="json"))
                print("Файл удален")
            else:
                print('Некорректный выбор. Пожалуйста, введите номер действия из списка.')

    def xml_cmd(self):
        xml_manager = XmlManager()
        groups = []
        while True:
            print(
                "~~~ Работа с XML ~~~\n"
                "1. Создать файл\n"
                "2. Записать в файл\n"
                "3. Прочитать файл\n"
                "4. Удалить файл"
            )

            choice = input("Выбор: ")
            if choice == "1":
                xml_manager.create(get_file_name(extension="xml"))
                print("Файл создан")
            elif choice == "2":
                filename = get_file_name(extension="xml")
                while True:
                    print(
                        "~~~ Добавление данных ~~~\n"
                        "1. Добавить группу\n"
                        "2. Добавить студента\n"
                        "3. Сохранить"
                    )
                    choice = input("Выбор: ")
                    if choice == "1":
                        group = Group(input("Название: "), [])
                        groups.append(group)
                        print(f"Группа {group.name} добавлена")
                    elif choice == "2":
                        for i, group in enumerate(groups):
                            print(f"[{i}] {group}")
                        group_index = input("Выберите группу (index)")
                        student = Student(
                            input("Имя: "),
                            input("Фамилия: "),
                            input("Отчество: "),
                            input("Возраст: "),
                        )
                        groups[int(group_index)].students.append(student)
                        print(f"Студент {student.firstname} добавлен в группу {groups[int(group_index)].name}")
                    elif choice == "3":
                        xml_manager.save(filename, groups)
                        print("Информацию сохранена в файл")
                        break

            elif choice == "3":
                xml_manager.read(get_file_name(extension="xml"))
            elif choice == "4":
                xml_manager.delete(get_file_name(extension="xml"))
                print("Файл удален")
            else:
                print('Некорректный выбор. Пожалуйста, введите номер действия из списка.')

    def start(self):
        while True:
            print(
                " ~~~ Главное меню ~~~\n"
                "1. Вывести информацию о логических дисках\n"
                "2. Работа с файлами\n"
                "3. Работа с JSON файлами\n"
                "4. Работа с XML файлами\n"
                "5. Работа с архивом"
            )
            choice = input("Выбор: ")
            if choice == "1":
                DiskManager().get_info()
            elif choice == "2":
                self.file_cmd()
            elif choice == "3":
                self.json_cmd()
            elif choice == "4":
                self.xml_cmd()
            elif choice == "5":
                self.archive_cmd()
            else:
                print('Некорректный выбор. Пожалуйста, введите номер действия из списка.')


if __name__ == "__main__":
    Cmd().start()
