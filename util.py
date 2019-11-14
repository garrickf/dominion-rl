def get_integer(prompt):
    typed = input(prompt)
    if typed.isdigit():
        return int(typed)
    elif typed == '':
        return None