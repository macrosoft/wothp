import py_compile, zipfile, os

WOTVersion = "0.9.12"
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
fZip.write("data/default_medium.font", WOTVersion+"/system/fonts/default_medium.font")
fZip.write("data/default_smaller.font", WOTVersion+"/system/fonts/default_smaller.font")
fZip.write("data/HGSoeiKakugothicUB_12.dds", WOTVersion+"/system/fonts/HGSoeiKakugothicUB_12.dds")
fZip.write("data/HGSoeiKakugothicUB_20.dds", WOTVersion+"/system/fonts/HGSoeiKakugothicUB_20.dds")
fZip.close()
