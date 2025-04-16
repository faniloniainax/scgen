from PIL import Image, ImageDraw, ImageFont
from scgen_xlconfig import *
import qrcode
import pandas as pd
import os
from typing import List

class Class:
    def __init__(self, stage: str, branch: str):
        self.stage = stage
        self.branch = branch

class Student:
    '''
        Classe qui représente les
        infos d'un étudiant de l'ENI.
    '''
    def __init__(self, row):
        self.id = ExtractCorrectID(str(row[ID_HEADER]).strip())
        self.phoneNumber = str(row[PHONE_NUMBER_HEADER]).strip()
        self.email = str(row[EMAIL_HEADER]).strip().lower()
        self.studentAddress = str(row[ADDRESS_HEADER]).strip()
        self.studentNICNumber = str(row[NIC_NUMBER_HEADER]).strip() 

        self.firstName, self.lastName = ExtractFullAndLastNames(row[FULL_NAME_HEADER])
        self.dob, self.pob = ExtractDateAndPlace(str(row[DOB_AND_POB_HEADER]))

        if not self.studentNICNumber == "" and not self.studentNICNumber == "nan":
            self.dNIC, self.pNIC = ExtractDateAndPlace(str(row[NIC_DAPOD_HEADER]))
        else:
            self.studentNICNumber = ""
            self.dNIC, self.pNIC = "", ""
    
    def __repr__(self):
        return f"Student({self.id}, {self.firstName}, {self.lastName}, {self.dob}, {self.pob}, {self.phoneNumber}, {self.email}, [{self.studentAddress}], {self.studentNICNumber}, {self.dNIC}, [{self.pNIC}])"

    def standardized(self) -> str:
        return f"Numéro {self.id} - {(self.firstName + ' ' + self.lastName).strip()} CIN {self.studentNICNumber}"

def ExtractFullAndLastNames(fullName: str) -> List[str]:
    '''
        Fonction qui retourne le nom et le prénom
        d'un étudiant à partir de son nom complet.
        Le nom est le premier mot, et le prénom
        est le reste du nom complet.
        Le prénom peut être visiblement vide.
    '''
    parts = fullName.split(" ")
    name = parts.pop(0)
    lastName = ""

    ## Retourner le nom, et un prénom vide.
    if len(parts) == 0:
        return [name, lastName]

    for lastNamePart in parts:
        lastName += lastNamePart.capitalize() + " "

    return [name, lastName.strip()]

def ExtractDateAndPlace(fullDAP: str) -> List[str]:
    '''
        Fonction qui retourne la date et le lieu
        à partir du format "dd/mm/yyyy à lieu".
    '''
    try:
        date, place = fullDAP.split("à", 1)
    except ValueError:
        return ["", ""]

    return [date.strip(), place.strip()]

def ExtractCorrectID(idPrototype: str) -> str:
    '''
        Fonction qui retourne l'ID d'un étudiant
        à partir de son "prototype" d'ID.
    '''
    ## Pour prévenir n'importe quelles bêtises
    ## des étudiants, les ID sont paddés à 4.
    numericId = idPrototype[0:4]
    rest = idPrototype[4:].strip().lower()

    if len(rest) == 0:
        return numericId
    
    ## Condition vraiment stupide, mais ça marche jusqu'ici:
    ## hf, -HF, -hf, H-f, h-f, H-F -> IG Fianarantsoa
    ## ht, -HT, -ht, H-t, h-t, H-T, -HTOL, -hTol, -HTol, H-Tol, h-tol -> IG Toliara
    if rest.find("h") != -1 and rest.find("f".casefold()) != -1:
        return numericId + "H-F"
    if rest.find("h") != -1 and rest.find("t".casefold()) != -1:
        return numericId + "H-TOL"
    
    return numericId

def GetPhotoPath(s: Student) -> str:
    '''
        Fonction qui s'occupe d'essayer
        d'importer la photo d'un étudiant,
        la photo doit être en JPEG.
    '''
    maybePath = os.path.join(PHOTO_FOLDER, s.id)

    if os.path.exists(maybePath + ".jpg"):
        return maybePath + ".jpg"
    
    return os.path.join(PHOTO_FOLDER, "null.jpg")

def WrapAddress(addr: str) -> str:
    '''
        Fonction qui *doit* s'occuper
        d'adapter les addresses longues
        à la disposition de la carte.
    '''
    return addr[0:13] + "\n" + addr[13::]

def MakeCardFront(s: Student, c: Class):
    '''
        Fonction qui s'occupe de populer
        le "recto" de la carte d'étudiant.
    '''
    cardFront = Image.open(FRONT_TEMPLATE).convert("RGBA")
    drawer = ImageDraw.Draw(cardFront)

    nameFont = ImageFont.truetype(TEXT_FONT_PATH, 22)
    textFont = ImageFont.truetype(TEXT_FONT_PATH, 18)

    ## D'abord, la photo d'identité:
    identityPic = Image.open(GetPhotoPath(s)).resize(ID_PIC_SIZE)
    cardFront.paste(identityPic, ID_PIC_POS)

    ## Ensuite, le code QR pour les données:
    qrCode = qrcode.make(s.standardized()).resize(QR_SIZE)
    cardFront.paste(qrCode, QR_POS)

    ## Le nom complet de l'étudiant.
    drawer.text(FIRST_NAME_POS, s.firstName, font=nameFont, fill=BLACK_COLOR)
    drawer.text(LAST_NAME_POS, s.lastName, font=nameFont, fill=LAST_NAME_COLOR)

    ## Le numéro matricule, le niveau, et le parcours.
    drawer.text(ID_NUMBER_POS, s.id, font=textFont, fill=WHITE_COLOR)
    drawer.text(STAGE_POS, c.stage, font=textFont, fill=WHITE_COLOR)
    drawer.text(BRANCH_POS, c.branch, font=textFont, fill=WHITE_COLOR)

    ## La date et le lieu de naissance.
    drawer.text(DOB_POS, s.dob, font=textFont, fill=BLACK_COLOR)
    drawer.text(POB_POS, s.pob, font=textFont, fill=BLACK_COLOR)

    ## Le numéro de CIN, la date et lieu de délivrance.
    drawer.text(NIC_NUMBER_POS, s.studentNICNumber, font=textFont, fill=BLACK_COLOR)
    drawer.text(NIC_DATE_POS, s.dNIC, font=textFont, fill=BLACK_COLOR)
    drawer.text(NIC_PLACE_POS, s.pNIC, font=textFont, fill=BLACK_COLOR)

    ## Finalement, le numéro de téléphone, l'e-mail, et l'adresse exacte.
    drawer.text(PHONE_NUMBER_POS, s.phoneNumber, font=textFont, fill=BLACK_COLOR)
    drawer.text(EMAIL_POS, s.email, font=textFont, fill=BLACK_COLOR)
    drawer.text(ADDRESS_POS, WrapAddress(s.studentAddress), font=textFont, fill=BLACK_COLOR)

    return cardFront

def MakeCardBack(s: Student):
    '''
        Fonction qui s'occupe de populer
        le "verso" de la carte d'étudiant.
    '''
    cardBack  = Image.open(BACK_TEMPLATE).convert("RGBA")

    def DrawStamp(img, text: str, pos):
        stampImage = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
        stampDrawer = ImageDraw.Draw(stampImage)
        stampFont = ImageFont.truetype(STAMP_FONT_PATH, 26)

        stampDrawer.text((0, 0), text, font=stampFont, fill=STAMP_COLOR + (180,))
        rotatedStamp = stampImage.rotate(-10, expand=1)
        
        img.paste(rotatedStamp, pos, rotatedStamp)

    DrawStamp(cardBack, "20 FEV. 2024", SCHOOL_STAMP_POS)
    DrawStamp(cardBack, "05 MAR. 2025", MEDIC_STAMP_POS)

    return cardBack

def MakeStudentCard(s: Student, c: Class) -> None:
    '''
        Fonction qui se charge de créer une
        carte d'étudiant pour une variable donnée.
    '''

    try:
        cardFront = MakeCardFront(s, c)
        cardBack  = MakeCardBack(s)
    except FileNotFoundError as e:
        print(f"L'étudiant {s.standardized()} ne possède pas de photo.")
        return

    outDir = os.path.join(OUTPUT_DIRECTORY, f"{c.stage} {c.branch}")
    totalWidth = cardFront.width + cardBack.width
    maxHeight = max(cardFront.height, cardBack.height)

    newCard = Image.new("RGBA", (totalWidth, maxHeight), (255, 255, 255, 255))
    newCard.paste(cardFront, (0, 0))
    newCard.paste(cardBack, (cardFront.width, 0))

    os.makedirs(outDir, exist_ok=True)
    newCard.convert("RGB").save(os.path.join(outDir, f"{s.id}.jpg"))

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    excelFile = pd.read_excel(INPUT_EXCEL_FILE)
    excelFile.fillna(" ") # Les NaN sont des chaînes vides.

    for _, row in excelFile.iterrows():
        MakeStudentCard(Student(row), Class("L3", "GB"))