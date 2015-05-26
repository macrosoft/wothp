import py_compile, zipfile, os

WOTVersion = "0.9.8"
language = 'ru' # 'ru' or 'en'

if os.path.exists("totalhp.zip"):
    os.remove("totalhp.zip")

py_compile.compile("src/__init__.py")
py_compile.compile("src/CameraNode.py")
py_compile.compile("src/totalhp.py")

fZip = zipfile.ZipFile("totalhp.zip", "w")
fZip.write("src/__init__.pyc", WOTVersion+"/scripts/client/mods/__init__.pyc")
fZip.write("src/totalhp.pyc", WOTVersion+"/scripts/client/mods/totalhp.pyc")
fZip.write("src/CameraNode.pyc", WOTVersion+"/scripts/client/CameraNode.pyc")
fZip.write("data/totalhp_"+language+".json", WOTVersion+"/scripts/client/mods/totalhp.json")
fZip.write("data/totalhp_bg.dds", WOTVersion+"/scripts/client/mods/totalhp_bg.dds")
fZip.close()
