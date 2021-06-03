# created for USERGE-X by @Kakashi_HTK(telegram)/@ashwinstr(github)


from googletrans import LANGUAGES

from userge import userge

def sort_lang(LANGUAGES):
    lang_list = []
    for code in LANGUAGES:
        lang_list.append(f"{LANGUAGES[code]} - {code}")
    lang_list = ",\n".join(lang_list)
    return lang_list
