# ported from ultroid userbot to USERGE-X by @Kakashi_HTK/@ashwinstr

import os
import shutil

from PyPDF2 import PdfFileReader, PdfFileWriter

from userge import Message, userge

if not os.path.exists("pdf/"):
    os.makedirs("pdf/")


@userge.on_cmd(
    "pdf_img",
    about={
        "header": "send page as image",
        "description": "Extract page from pdf and send it as image",
        "usage": "{tr}pdf_img [reply to pdf] [page number (optional)]",
    },
)
async def pdf_img_(message: Message):
    """Upload pdf page as image"""
    reply = message.reply_to_message
    input_ = message.filtered_input_str
    if not reply or not reply.document or reply.document.mime_type != "application/pdf":
        await message.edit("Please reply to a pdf...", del_in=5)
        return
    edt = await message.edit("Processing...")
    if not input_:
        path = os.path.join("pdf/", "temp.pdf")
        await userge.download_media(reply, path)
        pdf_f = "pdf/temp.pdf"
        pdf_f.replace(".pdf", "")
        pdf = PdfFileReader(pdf_f)
        for page in range(pdf.numPages):
            write = PdfFileWriter()
            write.addPage(pdf.getPage(page))
            with open(os.path.join(f"pdf/page{page + 1}.png"), "wb") as file:
                write.write(file)
        os.remove(pdf_f)
        lst = os.listdir("pdf/")
        for one in lst:
            lst_one = f"pdf/{one}"
            await userge.send_photo(message.chat.id, lst_one)
        shutil.rmtree("pdf/")
        await edt.delete()
    if input_:
        page = int(input_) - 1
        path = os.path.join("pdf/", "temp.pdf")
        await userge.download_media(reply, path)
        pdf_f = "pdf/temp.pdf"
        pdf_f.replace(".pdf", "")
        pdf = PdfFileReader(pdf_f)
        write = PdfFileWriter()
        write.addPage(pdf.getPage(page))
        with open(os.path.join("temp.png"), "wb") as file:
            write.write(file)
        os.remove(pdf_f)
        await userge.send_photo(
            message.chat.id, "temp.png", reply_to_message_id=reply.message_id
        )
        os.remove("temp.png")
        await edt.delete()


@userge.on_cmd(
    "pdf_text",
    about={
        "header": "text extract",
        "description": "extract text from pdf file",
        "usage": "{tr}pdf_text [reply to pdf] [page number OR (from - to) page number (optional)]",
    },
)
async def pdf_text_(message: Message):
    input_ = message.input_str
    reply = message.reply_to_message
    if not (reply or reply.document or reply.document.mime_type == "application/pdf"):
        await message.edit("Please reply to pdf file...", del_in=5)
        return
    edt = await message.edit("Processing...")
    if not input_:
        file = await userge.download_media(reply)
        read = PdfFileReader(file)
        text = f"{file.split('.')[0]}.txt"
        with open(text, "w") as t:
            for page_num in range(read.numPages):
                pageCon = file.getPage(page_num)
                txt = pageCon.extractText()
                t.write(f"Page number {page_num + 1}<br>")
                t.write("".center(100, "-"))
                t.write(txt)
        await userge.send_document(
            message.chat.id,
            text,
            reply_to_message_id=reply.message_id,
        )
        os.remove(file)
        os.remove(text)
        await edt.delete()
        return
    if "-" in input_:
        from_, to_ = input_.split("-")
        from_ = from_.strip()
        to_ = to_.strip()
        file = await userge.download_media(reply)
        read = PdfFileReader(file)
        str_ = ""
        for i in range(int(from_) - 1, int(to_)):
            str += read.getPage(i).extractText()
        text = f"{file.split('.')[0]} page {input_}.txt"
        with open(text, "w") as t:
            t.write(str)
        await userge.send_document(
            message.chat.id,
            text,
            reply_to_message_id=reply.message_id,
        )
        os.remove(text)
        os.remove(file)
    else:
        page = int(input_) - 1
        file = await userge.download_media(reply)
        read = PdfFileReader(file)
        str_ = read.getPage(page).extractText()
        text = f"{file.split('.')[0]} Page-{input_}.txt"
        with open(text, "w") as t:
            t.write(str_)
        await userge.send_document(
            message.chat.id,
            text,
            reply_to_message_id=reply.message_id,
        )
        os.remove(text)
        os.remove(file)
    await edt.delete()
