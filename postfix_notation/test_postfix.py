import pathlib
import runpy
import sys

import pytest

from main import clean, parse_number, apply_operator, calculate, main


MAIN_PATH = pathlib.Path(__file__).with_name("main.py")


# clean

# 3.0 превращается в 3
def test_clean_integer_float_becomes_int():
    # действие
    value = clean(3.0)

    # проверка: значение равно 3 и тип стал int
    assert value == 3
    assert isinstance(value, int)


# у дробного числа убирается дробная часть 0.30000000000000004
def test_clean_removes_float_tail():
    # подготовка
    value = 0.1 + 0.2
    # действие 
    result = clean(value)
    # проверка
    assert result == 0.3


# целое число не меняется
def test_clean_keeps_int():
    # действие
    value = clean(42)
    # проверка 
    assert value == 42


# parse_number: превращение токена в число

# прогон теста по списку разных корректных чисел 
# декоратор нужен для того, чтобы не писать 10 одинаковых тестов для разных чисел
# список входных данных (token) и ожидаемых ответов (expected)
@pytest.mark.parametrize("token, expected", [
    ("5", 5),
    ("-3", -3),
    ("0", 0),
    ("2.5", 2.5),
    ("2.0", 2),
])
# целые, дробные и отрицательные числа, распознаются
def test_parse_number_valid(token, expected):
    # действие
    value = parse_number(token)
    # проверка
    assert value == expected


# прогон теста по нечисловым строкам и спецзначениям float
@pytest.mark.parametrize("token", ["abc", "+", "-", "~", "/", "nan", "inf"])
# операторы, слова и nan/inf числами не считаются
def test_parse_number_not_a_number(token):
    # действие
    value = parse_number(token)
    # проверка 
    assert value is None


# apply_operator: операции

# прогон базовых операций и оператора ~ без нулей
@pytest.mark.parametrize("operator, x, y, expected", [
    ("+", 2, 3, 5),
    ("-", 2, 5, -3),
    ("*", 4, 3, 12),
    ("/", 7, 2, 3.5),
    ("~", 49, 2, 47),
    ("~", -3, 4, 7),
])
# каждая операция считает результат
def test_apply_operator(operator, x, y, expected):
    # подготовка: остальной стек пуст
    stack = []
    # действие
    result = apply_operator(operator, x, y, stack)
    # проверка
    assert result == expected


# если есть операнд 0, считаем квадрат суммы операндов и всего стека
def test_tilde_with_zero_sums_whole_stack_and_clears_it():
    # подготовка: операнды 0 и 4 уже достали, в стеке остался 3
    stack = [3]
    # действие
    result = apply_operator("~", 0, 4, stack)
    # проверка: результат 49, а стек чистый
    assert result == 49
    assert stack == []


# ноль может быть и вторым операндом
def test_tilde_with_zero_as_second_operand():
    # подготовка
    stack = [1, 2]
    # действие
    result = apply_operator("~", 3, 0, stack)
    # проверка: (1 + 2 + 3 + 0) ** 2
    assert result == 36


# если оба операнда не равны 0, остальной стек не трогается
def test_tilde_both_nonzero_keeps_stack():
    # подготовка
    stack = [10]
    # действие 
    apply_operator("~", 5, 8, stack)
    # проверка
    assert stack == [10]


# calculate: вычисление выражения

@pytest.mark.parametrize("expression, expected", [
    ("3 0 4 ~ 2 ~", 47),
    ("2 2 + 4 - 4 ~ 2 3 * +", 22),
    ("5", 5),
    ("3 4 +", 7),
    ("10 2 /", 5),
    ("1 3 /", 0.3333333333),
    ("1 2 + 3 *", 9),
    ("0 0 ~", 0),
])
# выражения вычисляются правильно
def test_calculate_expressions(expression, expected):
    # подготовка
    tokens = expression.split()
    # действие
    result = calculate(tokens)
    # проверка 
    assert result == expected


# после каждого токена печатается состояние стека 
# capsys: встроенный инструмент pytest
# Если передать его в аргументы теста, 
# он начинает втайне «записывать» всё, 
# что программа пытается вывести на экран через print()

def test_calculate_prints_stack_on_every_step(capsys):
    # подготовка
    tokens = ["3", "0", "4", "~", "2", "~"]
    # действие 
    calculate(tokens)
    # проверка: сверка построчно вывод в консоль

    # capsys.readouterr().out отдает весь перехваченный текст, 
    # мы разбиваем его по строкам (splitlines()) и сверяем с тем, 
    # что ожидаем увидеть
    assert capsys.readouterr().out.splitlines() == [
        "шаг 1: 3 в стеке [3]",
        "шаг 2: 0 в стеке [3, 0]",
        "шаг 3: 4 в стеке [3, 0, 4]",
        "шаг 4: ~ в стеке [49]",
        "шаг 5: 2 в стеке [49, 2]",
        "шаг 6: ~ в стеке [47]",
    ]


# пустое выражение дает ошибку
def test_calculate_empty_expression_raises():
    # действие и проверка: ловим исключение ValueError
    with pytest.raises(ValueError) as error:
        calculate([])
    assert "пустое" in str(error.value)


# деление на ноль дает ошибку с номером шага
def test_calculate_division_by_zero_raises():
    # подготовка
    tokens = ["4", "0", "/"]

    # действие и проверка
    with pytest.raises(ValueError) as error:
        calculate(tokens)
    assert "шаг 3" in str(error.value)
    assert "деление на ноль" in str(error.value)


# оператору не хватает операндов
def test_calculate_not_enough_operands_raises():
    # подготовка: для + есть одно значение
    tokens = ["5", "+"]

    # действие и проверка
    with pytest.raises(ValueError) as error:
        calculate(tokens)
    assert "шаг 2" in str(error.value)
    assert "нужно два значения" in str(error.value)


# неизвестный токен дает ошибку с подсказкой про кавычки
def test_calculate_unknown_token_raises_with_hint():
    # подготовка
    tokens = ["2", "abc", "+"]

    # действие и проверка 
    with pytest.raises(ValueError) as error:
        calculate(tokens)
    assert "неизвестный токен 'abc'" in str(error.value)
    assert "кавычки" in str(error.value)


# если в конце в стеке больше одного значения, не хватает операторов
def test_calculate_leftover_values_raises():
    # подготовка
    tokens = ["1", "2"]
    # действие и проверка
    with pytest.raises(ValueError) as error:
        calculate(tokens)
    assert "не хватает операторов" in str(error.value)


# main: запуск программы

# итог печатается в формате "выражение = результат"
def test_main_prints_result_in_required_format(capsys):
    # подготовка
    args = ["3 0 4 ~ 2 ~"]
    # действие
    code = main(args)
    # проверка: код 0 и последняя строка вывода совпадает с форматом
    assert code == 0
    assert capsys.readouterr().out.splitlines()[-1] == "3 0 4 ~ 2 ~ = 47"


# токены можно передать отдельными аргументами
def test_main_accepts_separate_arguments(capsys):
    # подготовка
    args = ["3", "4", "+"]
    # действие
    code = main(args)
    # проверка
    assert code == 0
    assert capsys.readouterr().out.splitlines()[-1] == "3 4 + = 7"


# при ошибке прога показывает шаги, пишет понятное сообщение и возвращает 1
def test_main_error_returns_1(capsys):
    # подготовка
    args = ["4 0 /"]
    # действие
    code = main(args)
    # проверка: шаги в обычном выводе (out), а ошибка в потоке ошибок (err)
    captured = capsys.readouterr()
    assert code == 1
    assert "шаг 2: 0 в стеке [4, 0]" in captured.out
    assert "Ошибка: шаг 3: деление на ноль" in captured.err


# слишком большое число дает сообщение, а не падение программы
def test_main_too_large_number_returns_1(capsys):
    # подготовка: супер большое целое делим на 1, результат не помещается в float
    args = ["1" + "0" * 400, "1", "/"]
    # действие
    code = main(args)
    # проверка 
    assert code == 1
    assert "супер большое число" in capsys.readouterr().err


# без аргументов программа объясняет, как ею пользоваться, и возвращает 1
def test_main_without_arguments_prints_usage(capsys):
    # действие
    code = main([])
    # проверка
    assert code == 1
    assert "Использование" in capsys.readouterr().out


# ключи -h и --help выводят справку и возвращают 0
@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_main_help(capsys, flag):
    # действие
    code = main([flag])
    # проверка
    assert code == 0
    assert "Использование" in capsys.readouterr().out


# без явных аргументов main берет их из командной строки (monkeypatch временно подменяет sys.argv)
def test_main_reads_sys_argv_by_default(capsys, monkeypatch):
    # подготовка: подменяем sys.argv
    monkeypatch.setattr(sys, "argv", ["main.py", "2", "3", "+"])
    # действие
    code = main()
    # проверка
    assert code == 0

    # capsys перехватывает всё, что программа печатала через print()
    # берем весь вывод (.out), разбиваем на строки, 
    # смотрим что строка последняя содердит ответ правильный
    assert capsys.readouterr().out.splitlines()[-1] == "2 3 + = 5"


# запуск файла(main.py) как программы завершается с кодом 0 

# для того чтобы убедиться что блок if __name__ == "__main__": 
# работает корректно  
def test_script_run_as_program(capsys, monkeypatch):
    # подготовка
    monkeypatch.setattr(sys, "argv", ["main.py", "3 0 4 ~ 2 ~"])
    # действие и проверка: запускаем скрипт через runpy и ловим sys.exit

    # ловим попытку заавершения и записываем ее в переменную exit_info
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(MAIN_PATH), run_name="__main__")
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.splitlines()[-1] == "3 0 4 ~ 2 ~ = 47"