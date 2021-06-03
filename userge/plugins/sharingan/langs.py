# created for USERGE-X by @Kakashi_HTK(telegram)/@ashwinstr(github)


def sort_lang(LANGUAGES):
    lang_list = []
    for code in LANGUAGES:
        lang_list.append(f"{LANGUAGES[code]} - {code}")
    lang_list = "{\n    " + ",\n   ".join(lang_list) + "\n}"
    return lang_list
