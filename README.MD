# Генерация отчета по средним значениям:


- python main.py --file logs_files/example1.log logs_files/example2.log --report average
Генерация отчета с фильтрацией по дате:

- python main.py --file logs_files/example1.log logs_files/example2.log --report average --date 2025-06-21

Добавление новых отчетов
Чтобы добавить новый тип отчета:

* Создайте новый класс, унаследованный от Report.
* Определите в нем список колонок (HEADERS) 
* реализуйте метод generate_report().
* В функции main() добавьте обработку нового типа в условие выбора отчета.
* Обновите аргументы командной строки, добавив новый вариант в choices.