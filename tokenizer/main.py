import sys

# ключевые слова
KEYWORDS = ["if", "else", "while", "return", "for", "def"]


def tokenize(text, filename):
    tokens = []
    i = 0  # текущая позиция в тексте
    line = 1  # текущая строка
    col = 1  # текущая колонка

    while i < len(text):
        ch = text[i]

        # перевод строки
        if ch == '\n':
            line += 1
            col = 1
            i += 1
            continue

        # пропускаем пробелы и табы
        if ch in ' \t\r':
            i += 1
            col += 1
            continue

        # комментарий до конца строки
        if ch == '#':
            while i < len(text) and text[i] != '\n':
                i += 1
            continue

        # строковый литерал
        if ch == '"':
            start_col = col  # запоминаем начало токена
            i += 1
            col += 1
            s = ''
            while i < len(text) and text[i] != '"' and text[i] != '\n':
                s += text[i]
                i += 1
                col += 1
            # если строка не закрылась
            if i >= len(text) or text[i] == '\n':
                print(f"{filename}:{line}:{start_col}: lexical: незакрытый строковый литерал", file=sys.stderr)
                sys.exit(1)
            i += 1  # пропускаем закрывающую кавычку
            col += 1
            tokens.append(("STRING", '"' + s + '"', line, start_col))
            continue

        # числа (целые и вещественные)
        if ch.isdigit() or (ch == '.' and i + 1 < len(text) and text[i + 1].isdigit()):
            start_col = col
            num = ''
            has_dot = False
            while i < len(text) and (text[i].isdigit() or text[i] == '.'):
                if text[i] == '.':
                    if has_dot:
                        break
                    has_dot = True
                num += text[i]
                i += 1
                col += 1
            if has_dot:
                tokens.append(("FLOAT", num, line, start_col))
            else:
                tokens.append(("INT", num, line, start_col))
            continue

        # идентификаторы и ключевые слова
        if ch.isalpha() or ch == '_':
            start_col = col
            word = ''
            while i < len(text) and (text[i].isalnum() or text[i] == '_'):
                word += text[i]
                i += 1
                col += 1
            if word in KEYWORDS:
                tokens.append(("KEYWORD", word, line, start_col))
            else:
                tokens.append(("IDENT", word, line, start_col))
            continue

        # двухсимвольные операторы (первые)
        if i + 1 < len(text) and text[i:i+2] in ['==', '<=', '>=']:
            tokens.append(("OP", text[i:i+2], line, col))
            i += 2
            col += 2
            continue

        # односимвольные операторы
        if ch in '+-*/=<>':
            tokens.append(("OP", ch, line, col))
            i += 1
            col += 1
            continue

        # разделители
        if ch in '(){},;':
            tokens.append(("SEP", ch, line, col))
            i += 1
            col += 1
            continue

        # неизвестный символ —> ошибка
        print(f"{filename}:{line}:{col}: lexical: неожиданный символ '{ch}'", file=sys.stderr)
        sys.exit(1)

    return tokens


def main():
    if len(sys.argv) != 2:
        print("Использование: python main.py <имя_файла>", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]

    # читаем файл
    try:
        f = open(filename, "r", encoding="utf-8")
        text = f.read()
        f.close()
    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Ошибка: не удалось прочитать файл '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

    tokens = tokenize(text, filename)
    for t in tokens:
        print(f"({t[0]}, {t[1]}, {t[2]}:{t[3]})")


if __name__ == "__main__":  # pragma: no cover
    main()
