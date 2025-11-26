groupmates = [
    {
        "name": "Александр",
        "surname": "Иванов", 
        "exams": ["Информатика", "ЭЭИС", "Web"],
        "marks": [4, 3, 5]
    },
    {
        "name": "Иван",
        "surname": "Петров",
        "exams": ["История", "АИГ", "КТП"], 
        "marks": [4, 4, 4]
    },
    {
        "name": "Кирилл", 
        "surname": "Смирнов",
        "exams": ["Философия", "ИС", "КТП"],
        "marks": [5, 5, 5]
    }
]

def print_students(students):
    print(u"Имя".ljust(15), u"Фамилия".ljust(10), 
          u"Экзамены".ljust(30), u"Оценки".ljust(20))
    for student in students:
        print(student["name"].ljust(15), 
              student["surname"].ljust(10), 
              str(student["exams"]).ljust(30), 
              str(student["marks"]).ljust(20))

# Функция фильтрации по среднему баллу
def filter_students_by_average(students, min_average):
    filtered_students = []
    for student in students:
        average = sum(student["marks"]) / len(student["marks"])
        if average >= min_average:
            filtered_students.append(student)
    return filtered_students

# Основная программа
if __name__ == "__main__":
    print("Все студенты:")
    print_students(groupmates)
    
    print("\nФильтрация по среднему баллу:")
    try:
        min_avg = float(input("Введите минимальный средний балл: "))
        filtered = filter_students_by_average(groupmates, min_avg)
        if filtered:
            print_students(filtered)
        else:
            print("Нет студентов с таким средним баллом")
    except ValueError:
        print("Ошибка: введите число")