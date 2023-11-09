# ©Meek_0 [2022]

"""Module to morse code"""

from userge import Message, userge

morse = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    ", ": "--..--",
    ".": ".-.-.-",
    "?": "..--..",
    "/": "-..-.",
    "-": "-....-",
    "(": "-.--.",
    ")": "-.--.-",
    "=": "-...-",
    "&": ".-...",
    "+": ".-.-.",
    "@": ".--.-.",
    "!": "-.-.--",
    '"': ".-..-.",
    "'": ".----.",
    ":": "---...",
    " ": "/",
}


def encrypt(message):
    message = message.upper()
    message.split()
    encrypt_message = ""
    for i in message:
        try:
            encrypt_message += morse[i] + " "
        except BaseException:
            return "Invalid characters in input !"
    return encrypt_message


def decrypt(message):
    decrypt_message = ""
    for i in message.split():
        try:
            decrypt_message += list(morse.keys())[list(morse.values()).index(i)]
        except BaseException:
            return "Invalid characters in input !"

    return decrypt_message


@userge.on_cmd(
    "morse",
    about={
        "header": "Morse Code",
        "description": "Encrypting and Decrypting text in morse code !\n\tUse -e for Encryption !\n\tUse -d for Decryption !\n\tHere -es will replace word spaces with / sign",
        "usage": "{tr}morse [-e | -d | -es | -ds] [text | reply]\nExample: .morse -e I love Coding",
    },
    del_pre=True,
)
async def _style_text(message: Message):
    """Morse Code"""
    reply = message.reply_to_message
    try:
        args = reply.text
    except BaseException:
        args = str((message.input_str).split(maxsplit=1)[1].strip())

    args2 = message.filtered_input_str or reply.text
    if not args:
        await message.err("**Stop it ! Get some help from `.help morse`**", del_in=5)
        return
    await message.edit("`Doing some Morse ...`")
    if message.flags:
        job = list(message.flags.keys())[0]
        if job == "e":
            enc = encrypt(args).replace("/", "")
            output = f"**<u>__Encoded in Morse:__</u>** \n\n\n`{enc}` "

        elif job == "d":
            dec = decrypt(args.replace("  ", " / "))
            output = f"**<u>__Decoded from Morse:__</u>** \n\n\n`{dec}`"
        elif job == "es":
            output = f"**<u>__Encoded in Morse:__</u>** \n\n\n`{encrypt(args2)}`"
        elif job == "ds":
            output = f"**<u>__Decoded from Morse:__</u>** \n\n\n`{decrypt(args2)}`"
        else:
            await message.err(
                f"`\n<i><b><u>Flag is Invalid !</u></b></i>\n\nMake sure to input` -e | -es `OR` -d | -ds `only` !",
                del_in=5,
            )
            return
        await message.edit(output)
    else:
        await message.err(
            f"\n`<i><b><u>Stop it !</u></b></i>\n\nGet some help from` .help morse",
            del_in=5,
        )
        return
