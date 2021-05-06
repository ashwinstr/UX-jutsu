# ported from ultroid userbot to USERGE-X by @Kakashi_HTK/@ashwinstr

import os
import shutil

import cv2
import imutils
import numpy as np
import PIL
from imutils.perspective import four_point_transform
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from skimage.filters import threshold_local

from userge import Config, Message, userge

if not os.path.exists(f"{Config.DOWN_PATH}/pdf_merge/"):
    os.makedirs(f"{Config.DOWN_PATH}/pdf_merge/")


@userge.on_cmd(
    "pdf_img",
    about={
        "header": "send page as image",
        "description": "Extract page from pdf and send it as image",
        "usage": "{tr}pdf_img [reply to pdf] [page number (optional)]",
    },
)
async def img_pdf(message: Message):
    """Upload pdf page as image"""
    reply = message.reply_to_message
    input_ = message.filtered_input_str
    if not reply or not reply.document or reply.document.mime_type != "application/pdf":
        await message.edit("Please reply to a pdf...", del_in=5)
        return
    edt = await message.edit("Processing...")
    if not input_:
        path = os.path.join(f"{Config.DOWN_PATH}/pdf/", "temp.pdf")
        await userge.download_media(reply, path)
        pdf_f = f"{Config.DOWN_PATH}/pdf/temp.pdf"
        pdf_f.replace(".pdf", "")
        pdf = PdfFileReader(pdf_f)
        for page in range(pdf.numPages):
            write = PdfFileWriter()
            write.addPage(pdf.getPage(page))
            with open(
                os.path.join(f"{Config.DOWN_PATH}/pdf/page{page + 1}.png"), "wb"
            ) as file:
                write.write(file)
        os.remove(pdf_f)
        lst = os.listdir(f"{Config.DOWN_PATH}/pdf/")
        for one in lst:
            lst_one = f"{Config.DOWN_PATH}/pdf/{one}"
            await userge.send_photo(message.chat.id, lst_one)
        shutil.rmtree(f"{Config.DOWN_PATH}/pdf/")
        await edt.delete()
    if input_:
        page = int(input_) - 1
        path = os.path.join(f"{Config.DOWN_PATH}/pdf/", "temp.pdf")
        await userge.download_media(reply, path)
        pdf_f = f"{Config.DOWN_PATH}/pdf/temp.pdf"
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
async def text_pdf(message: Message):
    """extract text from pdf"""
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


@userge.on_cmd(
    "pdf_scan",
    about={
        "header": "image to pdf",
        "description": "convert and send image as pdf file",
        "usage": "{tr}pdf_scan [reply to image]",
    },
)
async def scan_pdf(message: Message):
    """image to pdf conversion"""
    reply = message.reply_to_message
    if not reply or not reply.media:
        await message.edit("Please reply to an image...", del_in=5)
        return
    media = await reply.download()
    if not media.endswith((".jpg", ".jpeg", ".png", ".webp")):
        await message.edit("Please reply to an image...", del_in=5)
        os.remove(media)
        return
    await message.edit("Processing...")
    image = cv2.imread(media)
    original_image = image.copy()
    ratio = image.shape[0] / 500.0
    image = imutils.resize(image, height=500)
    image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image_y = np.zeros(image_yuv.shape[0:2], np.uint8)
    image_y[:, :] = image_yuv[:, :, 0]
    image_blurred = cv2.GaussianBlur(image_y, (3, 3), 0)
    edges = cv2.Canny(image_blurred, 50, 200, apertureSize=3)
    contours, hierarchy = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    polygons = []
    for cnt in contours:
        hull = cv2.convexHull(cnt)
        polygons.append(cv2.approxPolyDP(hull, 0.01 * cv2.arcLength(hull, True), False))
        sortedPoly = sorted(polygons, key=cv2.contourArea, reverse=True)
        cv2.drawContours(image, sortedPoly[0], -1, (0, 0, 255), 5)
        simplified_cnt = sortedPoly[0]
    if len(simplified_cnt) == 4:
        cropped_image = four_point_transform(
            original_image,
            simplified_cnt.reshape(4, 2) * ratio,
        )
        gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        T = threshold_local(gray_image, 11, offset=10, method="gaussian")
        ok = (gray_image > T).astype("uint8") * 225
    if len(simplified_cnt) != 4:
        ok = cv2.detailEnhance(original_image, sigma_s=10, sigma_r=0.15)
    cv2.imwrite("png.png", ok)
    image1 = PIL.Image.open("png.png")
    im1 = image1.convert("RGB")
    scann = media.split("/")[3]
    scann = f"Scanned {scann.split('.')[0]}.pdf"
    im1.save(scann)
    await userge.send_document(
        message.chat.id, scann, reply_to_message_id=reply.message_id
    )
    await message.delete()
    os.remove(media)
    os.remove("png.png")
    os.remove(scann)


@userge.on_cmd(
    "pdf_save",
    about={
        "header": "Save image/pdf(s)",
        "description": "Save image/pdf(s) to merge later",
        "usage": "{tr}pdf_save [reply to image/pdf]",
    },
)
async def save_pdf(message: Message):
    """save and merge image/pdf(s)"""
    reply = message.reply_to_message
    if not reply or not reply.media:
        await message.edit("Please reply to an image...", del_in=5)
        return
    merge_path = f"{Config.DOWN_PATH}/pdf_merge/"
    if not os.path.exists(merge_path):
        os.makedirs(merge_path)
    media = await reply.download()
    if media.endswith((".jpg", ".jpeg", ".png", ".webp")):
        await message.edit("Processing...")
        image = cv2.imread(media)
        original_image = image.copy()
        ratio = image.shape[0] / 500.0
        image = imutils.resize(image, height=500)
        image_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        image_y = np.zeros(image_yuv.shape[0:2], np.uint8)
        image_y[:, :] = image_yuv[:, :, 0]
        image_blurred = cv2.GaussianBlur(image_y, (3, 3), 0)
        edges = cv2.Canny(image_blurred, 50, 200, apertureSize=3)
        contours, hierarchy = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        polygons = []
        for cnt in contours:
            hull = cv2.convexHull(cnt)
            polygons.append(
                cv2.approxPolyDP(hull, 0.01 * cv2.arcLength(hull, True), False),
            )
            sortedPoly = sorted(polygons, key=cv2.contourArea, reverse=True)
            cv2.drawContours(image, sortedPoly[0], -1, (0, 0, 255), 5)
            simplified_cnt = sortedPoly[0]
        if len(simplified_cnt) == 4:
            cropped_image = four_point_transform(
                original_image,
                simplified_cnt.reshape(4, 2) * ratio,
            )
            gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
            T = threshold_local(gray_image, 11, offset=10, method="gaussian")
            ok = (gray_image > T).astype("uint8") * 255
        if len(simplified_cnt) != 4:
            ok = cv2.detailEnhance(original_image, sigma_s=10, sigma_r=0.15)
        cv2.imwrite("png.png", ok)
        image1 = PIL.Image.open("png.png")
        im1 = image1.convert("RGB")
        num = 1
        while True:
            abc = f"{merge_path}scan{num}.pdf"
            if os.path.exists(abc):
                num += 1
            else:
                break
        im1.save(abc)
        await message.edit(
            f"Done, now reply another image/pdf, if completed then use {Config.CMD_TRIGGER}pdf_send to merge and send all as pdf...",
        )
        os.remove("png.png")
    elif media.endswith(".pdf"):
        num = 1
        while True:
            abc = f"{merge_path}scan{num}.pdf"
            if os.path.exists(abc):
                num += 1
            else:
                break
        await userge.download_media(reply, abc)
        await message.edit(
            f"Done, now reply another image/pdf, if completed then use {Config.CMD_TRIGGER}pdf_send to merge and send all as pdf...",
        )
    else:
        await message.edit("`Reply to a image or pdf only...`", del_in=5)
    os.remove(media)


@userge.on_cmd(
    "pdf_send",
    about={
        "header": "merge and send pdf",
        "description": "Merge the downloaded image/pdf(s) and send as final pdf file",
        "usage": "{tr}pdf_send",
    },
)
async def send_pdf(message: Message):
    """merge and send pdf"""
    reply = message.reply_to_message.message_id if message.reply_to_message else None
    if not os.path.exists(f"{Config.DOWN_PATH}/pdf_merge/scan1.pdf"):
        await message.edit(
            "First select pages by replying {Config.CMD_TRIGGER}pdf_save to image/pdf(s) which you want to make multi-page pdf file...",
        )
        return
    msg = message.input_str
    await message.edit("Merging image/pdf(s)...", del_in=5)
    if msg:
        name_ = f"{msg}.pdf"
    else:
        name_ = "My_PDF.pdf"
    merger = PdfFileMerger()
    for item in os.listdir(f"{Config.DOWN_PATH}/pdf_merge/"):
        if item.endswith("pdf"):
            merger.append(f"{Config.DOWN_PATH}/pdf_merge/{item}")
    merger.write(name_)
    await userge.send_document(message.chat.id, name_, reply_to_message_id=reply)
    os.remove(name_)


@userge.on_cmd(
    "del_merge",
    about={
        "header": "clear pdf_merge folder",
        "description": "delete all pdf(s) in pdf_merge folder to start fresh",
        "usage": "{tr}del_merge",
    },
)
async def delete_merge(message: Message):
    """clear pdf_merge folder"""
    path_ = f"{Config.DOWN_PATH}/pdf_merge/"
    if not os.path.exists(path_):
        await message.edit("Already empty...", del_in=5)
        return
    shutil.rmtree(path_)
    os.makedirs(path_)
    await message.edit("Deleted all pdf(s) from pdf_merge...")
