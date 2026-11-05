# Детерминированный конечный автомат

# Класс состояния автомата
class State:
    def __init__(self, name):
        self.name = name
        self.is_start = False
        self.is_final = False


# Класс перехода между состояниями
class Transition:
    def __init__(self, source, symbol, destination):
        self.source = source
        self.symbol = symbol
        self.destination = destination

# Класс детерминированного конечного автомата
class DFA:
    def __init__(self, abc):

        # Множество уникальных значений алфавита
        self.abc = set(abc)

        self.states = []
        self.transitions = []
        self.start_state = None
        self.final_states = []

    # Поиск состояния по имени 
    def find_state(self, name):

        # Бежим по списку объектов
        for state in self.states:  

            # Если имя текущего объекта совпало с тем, что мы ищем
            # Сразу возвращаем этот объект
            if state.name == name: 
                return state      

        # Если прошли весь цикл и ничего не нашли        
        return None                


    # Добавление состояния
    def add_state(self, name):
        if self.find_state(name) is not None:
            return False

        self.states.append(State(name))
        return True

    # Удаление состояния и связанных с ним переходов (стрелок)
    def remove_state(self, name):
        state = self.find_state(name)

        # Если состояния нет, нам нечего удалять
        if state is None:
            return False

        # Временный список переходов
        new_transitions = []

        # Оставляем «в живых» только те переходы, 
        # которые вообще никак не касаются удаляемого состояния
        for tr in self.transitions:
            if tr.source != state and tr.destination != state:
                new_transitions.append(tr) 

        # Заменяем старый список очищенным
        self.transitions = new_transitions 

        # Если было начальным: удаляем начальное состояние (теперь его больше нет)
        if self.start_state == state:
            self.start_state = None

        # Если было конечным: удаляем конечное состояние из списка конечных
        if state in self.final_states:
            self.final_states.remove(state)

        # Удаляем само состояние в принципе
        self.states.remove(state)
        return True

    # Установка начального состояния
    def add_start(self, name):
        state = self.find_state(name)

        # Если такого состояния вообще нет,
        # то нечего назначать начальным
        # Прежде состояние нужно добавить
        if state is None:
            return False

        # Стираем прежнюю точку старта (по сути для все состояний затираем этот флаг)
        for item in self.states:
            item.is_start = False

        state.is_start = True
        self.start_state = state
        return True

    # Удаление начального состояния
    def remove_start(self):

        # Если начального состояния и не было, выходим из метода
        if self.start_state is None:
            return False

        self.start_state.is_start = False
        self.start_state = None
        return True

    # Добавление заключительного состояния
    def add_final(self, name):
        state = self.find_state(name)

        # Если состояния с таким именем нет в автомате
        if state is None:
            return False

        state.is_final = True

        # Защита от дубликатов в списке
        if state not in self.final_states:
            self.final_states.append(state)

        return True

    # Удаление заключительного состояния
    def remove_final(self, name):
        state = self.find_state(name)

        if state is None:
            return False

        # Если состояния нет в списке финальных
        if state not in self.final_states:
            return False

        self.final_states.remove(state)
        state.is_final = False
        return True

    # Добавление перехода
    def add_transition(self, src_name, symbol, dst_name):
        source = self.find_state(src_name)
        destination = self.find_state(dst_name)

        # Проверяем существование состояний
        if source is None or destination is None:
            return False

        # Проверяем принадлежность символа алфавиту
        if symbol not in self.abc:
            return False

        # Проверяем детерминированность!:

        # из одного состояния по одному символу
        # допускается не более одного перехода
        for tr in self.transitions:

            # Если есть переход, который выходит из того же состояния:
            # и по тому же самому символу,
            # запрещаем разветвление
            if tr.source == source and tr.symbol == symbol:
                return False

        # Если всё хорошо, добавляем новый переход
        self.transitions.append(
            Transition(source, symbol, destination)
        )
        return True

    # Удаление конкретного перехода
    def remove_transition(self, src_name, symbol, dst_name):
        source = self.find_state(src_name)
        destination = self.find_state(dst_name)

        # Перебираем переходы и ищем нужный (по конкретным параметрам)
        for tr in self.transitions:
            if (
                tr.source == source
                and tr.symbol == symbol
                and tr.destination == destination
            ):
                self.transitions.remove(tr)
                return True

        return False

    # Проверка детерминированности автомата
    # Параметров, по сути, нет, за исключением self (т.е. самогО объекта ДКА)
    def is_deterministic(self):

        # seen — то, что уже видели (множество уникальных элементов)
        seen = set()

        for tr in self.transitions:

            # Все состояния и переходы должны существовать
            if tr.source not in self.states:
                return False

            if tr.destination not in self.states:
                return False

            # Символ перехода должен принадлежать алфавиту
            if tr.symbol not in self.abc:
                return False

            # Кортеж: для каждой пары "состояние + символ"
            # может существовать только один переход (условие ДКА)

            # Например: ("q0", "а")
            key = (tr.source, tr.symbol)

            # Поиск дубликатов
            if key in seen:
                return False

            # Если же ключ уникален
            seen.add(key)

        return True

    # Проверка полноты переходов

    # Полнота означает, что из каждого кружка (состояния) 
    # должно выходить ровно столько стрелок, 
    # сколько букв в нашем алфавите
    def is_complete(self):

        # Автомат не может быть полным ДКА, если он недетерменированный
        if not self.is_deterministic():
            return False

        # Собираем все реально существующие переходы (кортежи) в множество:
        tr_list = set()
        for tr in self.transitions:
            tr_list.add((tr.source, tr.symbol))

        # Проверяем, что для КАЖДОЙ пары есть стрелка:
        for state in self.states:
            for symbol in self.abc:

                # Ищем конкретную пару:
                current_pair = (state, symbol)

                # Если такой пары нет среди наших переходов, автомат не полный
                if current_pair not in tr_list:
                    return False

        return True

    # Переход в следующее состояние по одному символу
    def next_state(self, current, symbol):

        # Проверка состояния и алфавита на наличие в списках:
        if current not in self.states:
            return None

        if symbol not in self.abc:
            return None

        # Ищем нужное состояние и переходим в него, по сути возвращаем
        for tr in self.transitions:
            if tr.source == current and tr.symbol == symbol:
                return tr.destination

        # Переход отсутствует (значит: автомат не полный)
        return None

    # Проверка входной строки без подробного вывода
    def accept(self, symbols):

        # Без начального состояния мы не можем начинать обработку
        if self.start_state is None:
            return False

        current = self.start_state

        # Перебор строки
        for symbol in symbols:
            current = self.next_state(current, symbol)

            # Если из текущего состояния нет перехода дальше
            if current is None:
                return False

        # Если мы в конечном состоянии, строка принята, иначе НЕ принята
        return current in self.final_states


# Пошаговая проверка строки — отладчик
def trace_word(dfa, word):
    print(f"ПОШАГОВАЯ ПРОВЕРКА СТРОКИ: {word!r}")

    # Проверяем наличие начального состояния
    if dfa.start_state is None:
        print("ОШИБКА: начальное состояние не задано.")
        print("Проверка невозможна.")
        return False

    current = dfa.start_state
    print(f"Начальное состояние: {current.name}")

    # Последовательно обрабатываем каждый символ
    # Enumerate автоматически считает все шаги, записывая их в step
    for step, symbol in enumerate(word, start=1):
        print(f"\nШаг {step}")
        print(f"  Прочитан символ: {symbol!r}")
        print(f"  Текущее состояние: {current.name}")

        # Проверяем, входит ли символ в алфавит
        if symbol not in dfa.abc:
            print(
                f"  ОШИБКА: символ {symbol!r} "
                "не входит в алфавит автомата."
            )
            print("  Допустимые символы:", *sorted(dfa.abc), sep=", ")
            print("\nРЕЗУЛЬТАТ: СТРОКА ОТКЛОНЕНА")
            return False

        # Определяем следующее состояние
        next_state = dfa.next_state(current, symbol)

        if next_state is None:
            print("  Переход отсутствует.")
            print("  Автомат не может продолжить обработку.")
            print("\nРЕЗУЛЬТАТ: СТРОКА ОТКЛОНЕНА")
            return False

        print(
            f"  Выполнен переход: "
            f"{current.name} --{symbol}--> {next_state.name}"
        )

        current = next_state

    # Проверяем состояние после чтения всей строки
    print("Обработка строки завершена.")
    print(f"Конечное состояние: {current.name}")

    if current in dfa.final_states:
        print("Это заключительное состояние.")
        print("\nРЕЗУЛЬТАТ: СТРОКА ПРИНЯТА")
        return True

    print("Это НЕ заключительное состояние.")
    print("\nРЕЗУЛЬТАТ: СТРОКА ОТКЛОНЕНА")
    return False

# Вывод таблицы переходов
def show_transitions(dfa):
    print("ТАБЛИЦА ПЕРЕХОДОВ")

    # Если в автомате вообще нет состояний, выходить
    if not dfa.states:
        print("В автомате пока нет состояний.")
        return

    # Перебираем каждое состояние
    for state in dfa.states:
        
        if state == dfa.start_state:
            description = "начальное"
        elif state in dfa.final_states:
            description = "заключительное"
        else:
            description = "обычное"

        print(f"\nСостояние {state.name} ({description}):")

        # Перебираем все символы алфавита по порядку
        for symbol in sorted(dfa.abc):
            destination = dfa.next_state(state, symbol)
        
            # Если стрелки по этому символу нет
            if destination is None:
                print(f"  По символу {symbol!r}: переход отсутствует")
        
            # Если стрелка есть, выводим куда она ведет
            else:
                print(f"  По символу {symbol!r}: {state.name} -> {destination.name}")



# Демонстрация добавления и удаления элементов
def demonstrate_operations(dfa):
    print("ПРОВЕРКА ОПЕРАЦИЙ С АВТОМАТОМ")

    # Добавление нового состояния
    print("\n1. Добавление состояния q3")
    print("Результат:", dfa.add_state("q3"))
    print("Повторное добавление q3:", dfa.add_state("q3")) # должна сработать защита от дубликатов

    print(
        "Состояние q3 существует:",
        dfa.find_state("q3") is not None
    )

    # Работа с заключительным состоянием
    print("\n2. Работа с заключительными состояниями")
    print("Добавление q1:", dfa.add_final("q1"))
    print("Удаление q1:", dfa.remove_final("q1"))

    # Удаляем настоящее заключительное состояние q2
    print("Удаление заключительного состояния q2:",
          dfa.remove_final("q2"))

    print(
        "q2 теперь заключительное:",
        dfa.find_state("q2").is_final
    )

    # Восстанавливаем исходную конфигурацию (q2 вновь финальное)
    print("Восстановление q2:", dfa.add_final("q2"))

    # Работа с начальным состоянием
    # Если оно существует, берём его имя, а иначе пишем, что оно не задано
    print("\n3. Работа с начальным состоянием")
    print(
        "Начальное состояние:",
        dfa.start_state.name if dfa.start_state else "не задано"
    )

    print("Удаление начального состояния:", dfa.remove_start())
    print(
        "Начальное состояние задано:",
        dfa.start_state is not None
    )

    print("Восстановление q0:", dfa.add_start("q0"))

    # Удаление и восстановление перехода
    print("\n4. Работа с переходами")

    print(
        "Удаление перехода q0 --b--> q0:",
        dfa.remove_transition("q0", "b", "q0")
    )

    print("Детерминированность:", dfa.is_deterministic())
    print("Полнота после удаления перехода:", dfa.is_complete())

    print(
        "Восстановление перехода q0 --b--> q0:",
        dfa.add_transition("q0", "b", "q0")
    )

    # Удаление добавленного состояния
    print("\n5. Удаление состояния q3")
    print("Результат:", dfa.remove_state("q3"))

    print("\nИсходная конфигурация автомата восстановлена.")
    print("Детерминированность:", dfa.is_deterministic())
    print("Полнота:", dfa.is_complete())

# MAIN
# Главная часть программы
if __name__ == "__main__":

    # Создаём автомат с алфавитом из двух символов
    dfa = DFA({'a', 'b'})

    # Создаём состояния
    for name in ("q0", "q1", "q2"):
        dfa.add_state(name)

    # Назначаем начальное и заключительное состояния
    dfa.add_start("q0")
    dfa.add_final("q2")

    # Настраиваем переходы автомата (строка "ab")
    dfa.add_transition("q0", "a", "q1")
    dfa.add_transition("q0", "b", "q0")

    dfa.add_transition("q1", "a", "q1")
    dfa.add_transition("q1", "b", "q2")

    dfa.add_transition("q2", "a", "q2")
    dfa.add_transition("q2", "b", "q2")

    # Вывод общей информации
    print("ДЕТЕРМИНИРОВАННЫЙ КОНЕЧНЫЙ АВТОМАТ")

    print("Алфавит:", ", ".join(sorted(dfa.abc)))
    print("Количество состояний:", len(dfa.states))

    print(
        "Начальное состояние:",
        dfa.start_state.name if dfa.start_state else "не задано"
    )

    print(
        "Заключительные состояния:",
        ", ".join(state.name for state in dfa.final_states)
    )

    print('Условие принятия: строка содержит подстроку "ab".')

    print(
        "Детерминированность:",
        "подтверждена" if dfa.is_deterministic() else "нарушена"
    )

    print(
        "Полнота переходов:",
        "подтверждена" if dfa.is_complete() else "не подтверждена"
    )

    # Показываем исходную таблицу переходов
    show_transitions(dfa)

    # Примеры проверки строк
    print("ПРИМЕРЫ ПРОВЕРКИ СТРОК")

    for word in ("aaab", "bba", "ababab", "aaaa", "acb", ""):
        trace_word(dfa, word)

    # Главное меню
    while True:
        print("\nГЛАВНОЕ МЕНЮ")
        print("1 — Проверить новую строку")
        print("2 — Показать таблицу переходов")
        print("3 — Продемонстрировать добавление и удаление элементов")
        print("4 — Проверить свойства автомата")
        print("5 — Завершить работу")

        choice = input("\nВыбери действие: ").strip()

        if choice == "1":
            word = input("Введи строку из символов a и b: ")
            trace_word(dfa, word)

        elif choice == "2":
            show_transitions(dfa)

        elif choice == "3":
            demonstrate_operations(dfa)

        elif choice == "4":
            print("\nПРОВЕРКА СВОЙСТВ АВТОМАТА")
            print(
                "Начальное состояние задано:",
                dfa.start_state is not None
            )
            print(
                "Детерминированность:",
                dfa.is_deterministic()
            )
            print(
                "Полнота переходов:",
                dfa.is_complete()
            )
            print("Количество состояний:", len(dfa.states))
            print("Количество переходов:", len(dfa.transitions))

        elif choice == "5":
            print("Работа программы завершена.")
            break

        else:
            print("Неизвестная команда. Выбери число от 1 до 5.")
