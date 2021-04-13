# ported from ultroid userbot to USERGE-X by @Kakashi_HTK/@ashwinstr

import os
import shutil
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter

from userge import userge, Message, Config


if not os.path.exists("pdf/"):
    os.makedirs("pdf/")

@userge.on_cmd(
    "pdf",
    about={
        "header": "send page as image",
        "description": "Extract page from pdf and send it as image",
        "usage": "{tr}pdf [page number]",
    },
)
async def pdf_page(message: Message):
    """Upload pdf page as image"""
    reply = message.reply_to_message
    input = message.filtered_input_str
    if not reply or not reply.document:
        await message.edit("Please reply to a pdf...")
        return
    edt = await message.edit("Processing...")
    if not input:
        path = os.path.join("pdf/", "temp.pdf")
        await userge.download_media(reply, path)
        pdf_f = "pdf/temp.pdf"
        pdf_f.replace(".pdf", "")
        pdf = PdfFileReader(pdf_f)
        for page in range(pdf.numPages):
            write = PdfFileWriter()
            write.addPage(pdf.getPage(page))
            with open(os.path.join("pdf/page{}.png".format(page + 1), "wb")) as file:
                write.write(file)
        os.remove(pdf_f)
        lst = os.listdir("pdf/")
        for one in lst:
            lst_one = [f"pdf/{one}"]
            await userge.send_document(message.chat.id, lst_one)
        shutil.rmtree("pdf/")
        await edt.delete()
    if input:
        page = int(input) - 1
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
        await userge.send_document(message.chat.id, "temp.png", reply_to_message_id=reply.message_id)
        os.remove("temp.png")
        await edt.delete()
