def dict_to_binary(arg: dict) -> str:
    count = arg.__len__()
    res = 0
    for key, value in arg.items():
        value = 1 if value else 0
        res += value << (count - key)
    return format(res, "{fill}{width}b".format(width=count, fill=0))


if __name__ == "__main__":
    print(dict_to_binary({1: "a", 2: "", 3: 50}))
    print(dict_to_binary({6: 1, 2: 1, 3: 50, 5: True, 4: False, 1: 9, 7: 1}))
    print(dict_to_binary({1: None, 2: 1, 3: 1}))
