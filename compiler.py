import py_compile, zipfile, os

WOTVersion = "0.9.15"
language = 'ru' # 'ru' or 'en'

if os.path.exists("totalhp.zip"):
    os.remove("totalhp.zip")
py_compile.compile("src/mod_totalhp.py")

fZip = zipfile.ZipFile("totalhp.zip", "w")
fZip.write("src/mod_totalhp.pyc", WOTVersion+"/scripts/client/gui/mods/mod_totalhp.pyc")
fZip.write("data/mod_totalhp_"+language+".json", WOTVersion+"/scripts/client/gui/mods/mod_totalhp.json")
fZip.write("data/totalhp_bg.dds", WOTVersion+"/scripts/client/gui/mods/totalhp_bg.dds")
fZip.write("data/default_medium.font", WOTVersion+"/system/fonts/default_medium.font")
fZip.write("data/default_smaller.font", WOTVersion+"/system/fonts/default_smaller.font")
fZip.write("data/HGSoeiKakugothicUB_12.dds", WOTVersion+"/system/fonts/HGSoeiKakugothicUB_12.dds")
fZip.write("data/HGSoeiKakugothicUB_20.dds", WOTVersion+"/system/fonts/HGSoeiKakugothicUB_20.dds")
fZip.close()
