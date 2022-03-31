from zipfile import ZipFile
from reportlab.pdfgen import canvas
from PIL import Image
from dateutil.parser import parse
from functools import reduce

import sys
import xml.etree.ElementTree as ET
  
file_name = sys.argv[1]

def generatePdf(title, items):
    dt = parse(items[0][2])
    file_date = dt.strftime('%d/%m/%Y')

    pdf_file = f'{title}.pdf'
    can = canvas.Canvas(pdf_file)
    can.setTitle(title)
    can.drawCentredString(300, 770, title)
    can.drawCentredString(500, 770, f'Autor: {items[0][1]}')
    can.drawCentredString(500, 755, file_date)
    can.drawCentredString(300, 755, "Índice")

    for index, item in enumerate(items):
        can.drawString(20, (715-(index*15)), item[0])
        can.drawRightString(550, (715-(index*15)), str(index+2))
    can.showPage()
    for index, item in enumerate(items):
        can.drawString(20, 770, item[0])
        can.drawString(20, 730, f'Prioridade: {item[6]}')
        for idx, c in enumerate(item[3]):
            can.drawString(20, 715-(idx*15), c)
        can.drawInlineImage(item[4], 20,650-item[5])
        can.showPage()
    can.save()
  

def proccessPdf(file_name):
    new_items = []
    with ZipFile(file_name, 'r') as zip:
        items = zip.infolist()
        for item in items:
            file = len(item.filename.split("."))>1
            if file==True and item.filename.split(".")[1]=="bcf":
                tree =  ET.ElementTree(ET.fromstring(zip.read(item)))
                root = tree.getroot()
                topic = root.find("./Topic/Title").text
                author = root.find("./Topic/AssignedTo").text
                modified_date = root.find("./Topic/ModifiedDate").text
                comments = []
                for c in root.findall("./Comment/Comment"):
                    if c.text:
                        comments.append(c.text)
                priority = root.find("./Topic/Priority").text

                image_file = zip.open(root.find('./Topic').attrib['Guid']+'/snapshot.png')
                img = Image.open(image_file)
                img.thumbnail([400, 400],Image.ANTIALIAS)
                
                new_items.append([topic, author, modified_date, comments, img, img.height, priority])
    return new_items

items = proccessPdf(file_name)
generatePdf(file_name.split('.')[0], items)