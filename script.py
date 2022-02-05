from genericpath import exists
import io
import shutil
import os
import patoolib
import PySimpleGUI as sg
from PIL import Image

CURRENT_NAME_PREFIX = "Current Name: "
NEW_NAME_PREFIX = "New Name: "

shows = []
pathToNameMappings = {}


def imageData(path):
    image = Image.open(path)
    image.thumbnail((600, 380))
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    return bio.getvalue()


EXTRACTED_DIR = "./comic_extracted"
COMPRESSING_DIR = "./comic_to_be_compressed"
# frame1 = [[sg.Radio('Delete Final Page', 1, key='-DELETE-FINAL-PAGE-', default=True)],
#           [sg.Radio('Rename Pages', 1, key='-RENAME-PAGES-')]]

# col1 = [[sg.Button('Run')],
#         [sg.Button('End')]]

image_frame = []

layout = [
    [
        sg.Text("File selection", size=(15, 1), justification="right"),
        sg.InputText(
            "Comic file",
            enable_events=True,
        ),
        sg.FileBrowse(
            "Add file", key="-COMICFILE-", file_types=(("Comic file", "*.cbz *.cbr"),)
        ),
    ],
    # [sg.Frame("Processing content", frame1), sg.Column(col1)],
    [
        sg.Button("Back", key="Back"),
        sg.Button("Forward", key="Forward"),
        sg.Button("Delete", key="Delete"),
        sg.Button("Save", key="Save"),
    ],
    [
        sg.Image(
            data='',
            size=(600, 380),
            enable_events=True,
            background_color="white",
            key="-IMAGE-",
        )
    ],
    [
        sg.Text(
            CURRENT_NAME_PREFIX,
            font="Courier 12",
            text_color="black",
            key="-IMGCURRNAME-",
        )
    ],
    [
        [
            sg.Text("New Image Prefix: ", font="Courier 12", text_color="black"),
            sg.InputText(default_text=f"", key="-NEWIMAGEPREFIX-")
        ]
    ],
    [
        sg.Column(
            [
                [
                    sg.Text(NEW_NAME_PREFIX, font="Courier 12", text_color="black", key='-IMGNEWNAMEPREFIX-'),
                    sg.InputText(default_text=f"1", key="-IMGNEWNAME-"),
                    sg.Text(
                        "",
                        font="Courier 12",
                        text_color="black",
                        key="-IMGNEWSUFFIX-",
                    ),
                ]
            ], key='-IMAGERELATED-'
        )
    ]
]

# window = sg.Window("Excel combination", layout)
window = sg.Window(
    "My new window",
    layout,
    size=(600, 550),
    no_titlebar=False,
    # grab_anywhere=True,
    # keep_on_top=True,
    background_color="white",
    alpha_channel=1,
    # margins=(1, 1),
)


new_files = []
new_file_names = []
offset = 0

show = ''

while True:  # Event Loop
    event, values = window.read()
    if event in (None, "End","Exit", "Cancel"):
        break

    if event == "Run":
        print("Execute processing")
        if values["-DELETE-FINAL-PAGE-"]:
            print("Combine multiple sheets into one file")
        elif values["-RENAME-PAGES-"]:
            print("Combine multiple sheets into one sheet")

        sg.popup("Processing ended normally")
        window.FindElement("-MULTILINE-").Update("")
    elif event == "Forward":
        print("Forwarding")
        offset = min(len(shows) - 1, offset + 1)
        if len(shows) > 0:
            show = shows[offset]

    elif event == "Back":
        print("Moving Back")
        offset = max(0, offset - 1)
        if len(shows) > 0:
            show = shows[offset]

    elif event == "Delete":
        # print("Deleting image")
        if len(shows) > 0:
            os.remove(shows[offset])
            del shows[offset]
        offset = min(offset, len(shows)-1)

    elif event == "Save":
        if len(shows) == 0:
            sg.Popup("No image left to save")
            break
        # print("Saving images: ", shows)
        if os.path.exists(COMPRESSING_DIR):
            shutil.rmtree(COMPRESSING_DIR)
        os.mkdir(COMPRESSING_DIR)
        newImagePrefix = values['-NEWIMAGEPREFIX-'].strip()
        lastInt = None
        for im in shows:
            fileName = pathToNameMappings[im]
            existingMapping = fileName
            try:
                prefix = existingMapping.split(".")[0]
                prefixInt = int(prefix)
                if lastInt is None:
                    prefixInt = 0
                else:
                    prefixInt = lastInt + 1
                lastInt = prefixInt
                scnt = str(prefixInt)
                if len(scnt) < 3:
                    scnt = ("0"*(3-len(scnt))) + scnt
                fileName = f"{scnt}.{s.split('.')[-1]}"
            except:
                if lastInt is None:
                    lastInt = 0
                else:
                    lastInt = lastInt + 1
                continue
            shutil.copyfile(im, f"{COMPRESSING_DIR}/{newImagePrefix} {fileName}")
            os.remove(im)
        shutil.make_archive("UpdatedFile", 'zip', COMPRESSING_DIR)
        os.rename("UpdatedFile.zip", "UpdatedFile.cbz")
        sg.Popup("Images done successfully")
        break

    elif values["-COMICFILE-"] != "":
        comic_file_path = values["-COMICFILE-"]
        # print("Selected File: ", comic_file_path)
        import zipfile
        import rarfile
        if comic_file_path.endswith(".cbz"):
            f = zipfile.ZipFile(comic_file_path, "r")
        elif comic_file_path.endswith(".cbr"):
            f = rarfile.RarFile(comic_file_path, "r")
        for f in shows:
            try:
                os.remove(f)
            except:
                continue
        shows = []
        for name in f.namelist():
            try:
                zf = f.open(name)
                content = f.read(name)
                fname = name.split("/")[-1]
                if fname.strip() == "" or fname.endswith(".db"):
                    continue
                fimg = open(fname, "wb")
                fimg.write(content)
                fimg.close()
                im=Image.open(fname)
                shows.append(fname)
            except:
                import traceback
                traceback.print_exc()
                if os.path.exists(name):
                    if os.path.isdir(name):
                        shutil.rmtree(name)
                    else:
                        os.remove(name)
                continue
        f.close()
        cnt = 0
        for s in shows:
            scnt = str(cnt)
            if len(scnt) < 3:
                scnt = ("0"*(3-len(scnt))) + scnt
            pathToNameMappings[s] = f"{scnt}.{s.split('.')[-1]}"
            cnt = cnt + 1

    if len(shows) > 0:
        show = shows[offset]
        offset = min(offset, len(shows)-1)
        window["-IMAGE-"].update(imageData(show))
        window["-IMGCURRNAME-"].update(CURRENT_NAME_PREFIX + os.path.basename(show))
        fileExtension = os.path.basename(show).split(".")[-1]
        offset_in_fname = str(offset)
        if len(offset_in_fname) < 3:
            offset_in_fname = ("0"*(3-len(offset_in_fname))) + offset_in_fname
        window["-IMGNEWNAME-"].update(f"{offset_in_fname}")
        window["-IMGNEWSUFFIX-"].update(f".{fileExtension}")
        pathToNameMappings[show] = f"{values['-IMGNEWNAME-']}.{fileExtension}"
    else:
        window["-IMAGE-"].update("")
        window["-IMGCURRNAME-"].update("")
        window["-IMGNEWNAME-"].update("")
        window["-IMGNEWSUFFIX-"].update("")
        window["-IMGNEWNAMEPREFIX-"].update("")

window.close()
