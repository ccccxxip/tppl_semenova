import os
import sys
import subprocess
import tempfile
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import tokenize, main


# идентификаторы

# один символ
def test_simple_ident():
    assert tokenize("x", "f") == [("IDENT", "x", 1, 1)]

# обычное слово
def test_long_ident():
    assert tokenize("hello", "f") == [("IDENT", "hello", 1, 1)]

# цифры внутри имени
def test_ident_with_digits():
    assert tokenize("var1", "f") == [("IDENT", "var1", 1, 1)]

# подчеркивание в середине
def test_ident_with_underscore():
    assert tokenize("my_var", "f") == [("IDENT", "my_var", 1, 1)]

# начинается с подчеркивания
def test_ident_starts_with_underscore():
    assert tokenize("_x", "f") == [("IDENT", "_x", 1, 1)]

# несколько идентификаторов через пробел
def test_multiple_idents():
    result = tokenize("a b c", "f")
    assert result == [
        ("IDENT", "a", 1, 1),
        ("IDENT", "b", 1, 3),
        ("IDENT", "c", 1, 5),
    ]


# ключевые слова

# if
def test_keyword_if():
    assert tokenize("if", "f") == [("KEYWORD", "if", 1, 1)]

# else
def test_keyword_else():
    assert tokenize("else", "f") == [("KEYWORD", "else", 1, 1)]

# while
def test_keyword_while():
    assert tokenize("while", "f") == [("KEYWORD", "while", 1, 1)]

# return
def test_keyword_return():
    assert tokenize("return", "f") == [("KEYWORD", "return", 1, 1)]

# for
def test_keyword_for():
    assert tokenize("for", "f") == [("KEYWORD", "for", 1, 1)]

# def
def test_keyword_def():
    assert tokenize("def", "f") == [("KEYWORD", "def", 1, 1)]

# слово начинается на if, но это идентификатор
def test_keyword_prefix_is_ident():
    assert tokenize("iffy", "f") == [("IDENT", "iffy", 1, 1)]

# все 6 ключевых слов за раз
def test_all_keywords():
    result = tokenize("if else while return for def", "f")
    assert [t[1] for t in result] == ["if", "else", "while", "return", "for", "def"]
    assert all(t[0] == "KEYWORD" for t in result)


# целые числа

# 0
def test_int_zero():
    assert tokenize("0", "f") == [("INT", "0", 1, 1)]

# двузначное число
def test_int_multi():
    assert tokenize("42", "f") == [("INT", "42", 1, 1)]

# большое число
def test_int_big():
    assert tokenize("123456", "f") == [("INT", "123456", 1, 1)]


# вещественные числа

# float с точкой
def test_float_simple():
    assert tokenize("3.14", "f") == [("FLOAT", "3.14", 1, 1)]

# точка в начале (.5)
def test_float_dot_start():
    assert tokenize(".5", "f") == [("FLOAT", ".5", 1, 1)]

# точка в конце (5.)
def test_float_dot_end():
    assert tokenize("5.", "f") == [("FLOAT", "5.", 1, 1)]

# ноль с точкой (0.0)
def test_float_zero():
    assert tokenize("0.0", "f") == [("FLOAT", "0.0", 1, 1)]

# вторая точка не берется в число
def test_float_double_dot():
    result = tokenize("1.2.3", "f")
    assert result[0] == ("FLOAT", "1.2", 1, 1)


# строки

# строка
def test_string_simple():
    assert tokenize('"hello"', "f") == [("STRING", '"hello"', 1, 1)]

# пустая строка
def test_string_empty():
    assert tokenize('""', "f") == [("STRING", '""', 1, 1)]

# строка с пробелами внутри
def test_string_with_spaces():
    assert tokenize('"a b c"', "f") == [("STRING", '"a b c"', 1, 1)]

# ошибка: кавычка не закрыта
def test_string_unterminated():
    with pytest.raises(SystemExit):
        tokenize('"hello', "f")

# ошибка: перенос строки внутри кавычек
def test_string_unterminated_newline():
    with pytest.raises(SystemExit):
        tokenize('"hello\nworld"', "f")


# операторы

# +
def test_op_plus():
    assert tokenize("+", "f") == [("OP", "+", 1, 1)]

# -
def test_op_minus():
    assert tokenize("-", "f") == [("OP", "-", 1, 1)]

# *
def test_op_mul():
    assert tokenize("*", "f") == [("OP", "*", 1, 1)]

# /
def test_op_div():
    assert tokenize("/", "f") == [("OP", "/", 1, 1)]

# присваивание
def test_op_assign():
    assert tokenize("=", "f") == [("OP", "=", 1, 1)]

# <
def test_op_lt():
    assert tokenize("<", "f") == [("OP", "<", 1, 1)]

# >
def test_op_gt():
    assert tokenize(">", "f") == [("OP", ">", 1, 1)]

# сравнение на равенство
def test_op_eq():
    assert tokenize("==", "f") == [("OP", "==", 1, 1)]

# <=
def test_op_le():
    assert tokenize("<=", "f") == [("OP", "<=", 1, 1)]

# >=
def test_op_ge():
    assert tokenize(">=", "f") == [("OP", ">=", 1, 1)]


# разделители

# проверка всех разделителей
def test_sep_all():
    result = tokenize("( ) { } , ;", "f")
    assert [t[1] for t in result] == ["(", ")", "{", "}", ",", ";"]
    assert all(t[0] == "SEP" for t in result)


# пробелы и комментарии

# пробелы по бокам игнорируются
def test_skip_spaces():
    assert tokenize("   x   ", "f") == [("IDENT", "x", 1, 4)]

# /t игнорируется
def test_skip_tabs():
    assert tokenize("\tx", "f") == [("IDENT", "x", 1, 2)]

# комментарий после кода
def test_skip_comment():
    assert tokenize("x # comment", "f") == [("IDENT", "x", 1, 1)]

# только комментарий — токенов нет
def test_only_comment():
    assert tokenize("# comment", "f") == []

# комментарий, потом перенос строки и код
def test_comment_then_code():
    assert tokenize("# comment\nx", "f") == [("IDENT", "x", 2, 1)]

# пустая строка на входе
def test_empty():
    assert tokenize("", "f") == []

# строка только из пробелов и табов
def test_only_whitespace():
    assert tokenize("   \t  \n  ", "f") == []


# позиции

# тест координат
def test_example_positions():
    result = tokenize("x = y * 2 + z * 3", "f")
    assert result == [
        ("IDENT", "x", 1, 1),
        ("OP", "=", 1, 3),
        ("IDENT", "y", 1, 5),
        ("OP", "*", 1, 7),
        ("INT", "2", 1, 9),
        ("OP", "+", 1, 11),
        ("IDENT", "z", 1, 13),
        ("OP", "*", 1, 15),
        ("INT", "3", 1, 17),
    ]

# координаты на нескольких строках
def test_multiline():
    result = tokenize("x = 1\ny = 2", "f")
    assert result[0] == ("IDENT", "x", 1, 1)
    assert result[3] == ("IDENT", "y", 2, 1)


# ошибки

# ошибка: символ @
def test_error_unexpected(capsys):
    with pytest.raises(SystemExit):
        tokenize("a @ b", "input.txt")
    assert "input.txt:1:3: lexical: неожиданный символ '@'" in capsys.readouterr().err

# ошибка на второй строке
def test_error_second_line(capsys):
    with pytest.raises(SystemExit):
        tokenize("x\n@", "file.txt")
    assert "file.txt:2:1: lexical:" in capsys.readouterr().err


# сложные выражения

# объявление функции
def test_function_def():
    result = tokenize("def foo(x, y) {", "f")
    assert result[0] == ("KEYWORD", "def", 1, 1)
    assert result[1] == ("IDENT", "foo", 1, 5)

# условие if со сравнением
def test_if_with_comparison():
    result = tokenize("if (x >= 10) {", "f")
    types = [t[0] for t in result]
    assert types == ["KEYWORD", "SEP", "IDENT", "OP", "INT", "SEP", "SEP"]

# строковый литерал в выражении
def test_string_in_expr():
    result = tokenize('x = "hello"', "f")
    assert result[2] == ("STRING", '"hello"', 1, 5)

# многострочная прога
def test_multiline_program():
    result = tokenize("def main() {\n  x = 1\n  return x\n}", "f")
    assert result[0] == ("KEYWORD", "def", 1, 1)
    assert result[-1] == ("SEP", "}", 4, 1)


# CLI

# хелпер для запуска main.py через subprocess
def _run_main(source):
    main_py = os.path.join(os.path.dirname(__file__), "..", "main.py")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(source)
        path = f.name
    try:
        r = subprocess.run([sys.executable, main_py, path], capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr
    finally:
        os.unlink(path)

# CLI с валидным файлом
def test_cli_ok():
    rc, out, _ = _run_main("x = 1")
    assert rc == 0
    assert "(IDENT, x, 1:1)" in out

# CLI с ошибкой в файле
def test_cli_error():
    rc, _, err = _run_main("@")
    assert rc == 1
    assert "lexical" in err

# CLI без аргументов
def test_cli_no_args():
    main_py = os.path.join(os.path.dirname(__file__), "..", "main.py")
    r = subprocess.run([sys.executable, main_py], capture_output=True, text=True)
    assert r.returncode == 1

# CLI с несуществующим файлом
def test_cli_file_not_found():
    main_py = os.path.join(os.path.dirname(__file__), "..", "main.py")
    r = subprocess.run([sys.executable, main_py, "no_such_file.txt"], capture_output=True, text=True)
    assert r.returncode == 1


# тесты main

# вызов main без аргументов
def test_main_no_args(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    with pytest.raises(SystemExit):
        main()

# вызов main с несуществующим файлом
def test_main_file_not_found(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "pupupupu.txt"])
    with pytest.raises(SystemExit):
        main()

# вызов main - успех
def test_main_ok(monkeypatch, capsys, tmp_path):
    f = tmp_path / "input.txt"
    f.write_text("x = 1")
    monkeypatch.setattr(sys, "argv", ["main.py", str(f)])
    main()
    out = capsys.readouterr().out
    assert "(IDENT, x, 1:1)" in out
    assert "(OP, =, 1:3)" in out
    assert "(INT, 1, 1:5)" in out

# ошибка чтения файла
def test_main_io_error(monkeypatch, tmp_path):
    f = tmp_path / "input.txt"
    f.write_text("x = 1")
    monkeypatch.setattr(sys, "argv", ["main.py", str(f)])
    # симулируем сбой диска
    def fake_open(*args, **kwargs):
        raise IOError("disk error")
    monkeypatch.setattr("builtins.open", fake_open)
    with pytest.raises(SystemExit):
        main()
