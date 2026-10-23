import math
import sys

# кортеж со всеми поддерживаемыми операторами стековой машины
OPERATORS = ("+", "-", "*", "/", "~", "!")

# справка по запуску программы, выводится при пустом вводе или флаге --help
USAGE = """Использование: python main.py "<выражение>" """

# подсказка для пользователя, если терминал раскрыл символ * (список файлов) или ~ (домашняя папка)
HINT = 'Подсказка: возьмите выражение в кавычки, иначе оболочка заменит * и ~'

# убирает лишнее в дробных числах: 3.0 -> 3 и погрешности float 
def clean(value):
    # проверяем, является ли число float
    if isinstance(value, float):
        # округляем до 10 знаков после запятой
        value = round(value, 10)
        # если после запятой остался только ноль, превращаем в целое число int
        if value.is_integer():
            value = int(value)
    return value

# превращает строковый токен в число. если токен не число (оператор), возвращает None
def parse_number(token):
    # пробуем распознать токен как целое число (int)
    try:
        return int(token)
    except ValueError:
        pass  # если не вышло, переход к проверке на дробное число

    #пробуем распознать токен как float
    try:
        value = float(token)
    except ValueError:
        # если токен не int, не float ("+" или "abc"), возвращаем None
        return None

    # проверяем, что число конечное (отсекаем "inf", "-inf" и "nan")) isfinite - проверка на нормальное конечное число 
    return clean(value) if math.isfinite(value) else None

# применяет оператор к операндам: x - первый, y - второй элемент в стеке
# остальные значения стека передаются для оператора ~, тк он может их суммировать и очистить стек
def apply_operator(operator, x, y, stack):
    # стандартные бинарные операции
    if operator == "+":
        return x + y
    if operator == "-":
        return x - y
    if operator == "*":
        return x * y
    if operator == "/":
        return x / y
    if operator == "!":
        return x ** y

    # логика спец оператора ~:
    # если оба операнда != 0, возвр модуль их разности |x - y|
    if x != 0 and y != 0:
        return abs(x - y)

    # если хотя бы один операнд = 0
    # посчитать сумму обоих операндов (x, y) и всех оставшихся элементов в стеке
    total = x + y + sum(stack)
    # чистка стека, тк все элементы были использованы в сумме
    stack.clear()
    # **2 и вернуть результат (он будет положен в стек в функции calculate)
    return total * total

# вычисляет выражение по списку токенов и печчать состояние стека после каждого шага
# выражение некорректное -> выброс ValueError
def calculate(tokens):
    # список токенов пуст -> cообш об ошибке
    if not tokens:
        raise ValueError("выражение пустое")

    stack = []  # инит пустой стек для хранения чисел

    # проход по всем токенам, нумеруя шаги с 1
    for step, token in enumerate(tokens, start=1):
        # попытка распарсить токен как число
        number = parse_number(token)

        if number is not None:
            # если это число — кладем на вершину стека
            stack.append(number)
        elif token in OPERATORS:
            # если это известный оператор — проверяем, хватает в стеке операндов (мин 2)
            if len(stack) < 2:
                raise ValueError(f"шаг {step}: для '{token}' нужно два значения, а в стеке их {len(stack)}: {stack}")

            # извлекаем два верхних элемента из стека:
            # первым достается правый (y), второй — левый (x)
            y = stack.pop()
            x = stack.pop()

            # защита от деления на ноль
            if token == "/" and y == 0:
                raise ValueError(f"шаг {step}: деление на ноль ({x} / 0)")

            # вычисляем результат операции, очищаем от лишних дробных частей и кладем в стек
            stack.append(clean(apply_operator(token, x, y, stack)))
        else:
            # если токен не число не оператор -> ошибка с подсказкой про кавычки
            raise ValueError(f"шаг {step}: неизвестный токен '{token}'. {HINT}")

        # вывод текущего состояние стека на каждом шаге
        print(f"шаг {step}: {token} в стеке {stack}")

    # по окончании всех вычислений в стеке должен остаться один элемент — ответ
    if len(stack) != 1:
        raise ValueError(f"в стеке осталось не одно значение, а {len(stack)}: {stack}. не хватает операторов")

    return stack[0]

# читает выражение из аргументов, печатает шаги и результат. возвр 0 успех, 1 ошибка
def main(argv=None):
    # если аргументы не переданы явно (из тестов), берем из командной строки
    args = sys.argv[1:] if argv is None else argv
    # склейка всех аргументов через пробел и снова разбиваем по пробелам
    # это позволяет запускать программу и так `python main.py "2 3 +"`  
    # и так `python main.py 2 3 +`
    tokens = " ".join(args).split()

    # если аргументов нет или запросили справку (-h / --help)
    if not tokens or tokens[0] in ("-h", "--help"):
        print(USAGE)
        # если явно попросили --help, возвр код успеха 0; если забыли аргументы — код ошибки 1
        return 0 if tokens else 1

    try:
        # запуск вычисление выражения
        result = calculate(tokens)
    except ValueError as error:
        # перехватываем логические ошибки выражения и выводим их в поток ошибок
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    except OverflowError:
        # перехватываем переполнение (при делении больших целых чисел, не влезающих во float)
        print("Ошибка: супер большое число", file=sys.stderr)
        return 1

    # вывод результата
    print(f"{' '.join(tokens)} = {result}")
    return 0


# точка входа напрямую из терминала
if __name__ == "__main__":
    sys.exit(main())
