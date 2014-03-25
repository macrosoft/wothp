import py_compile, zipfile, os

WOTVersion = "0.8.11"

if os.path.exists("totalhp.zip"):
    os.remove("totalhp.zip")

py_compile.compile("src/__init__.py")
py_compile.compile("src/CameraNode.py")
py_compile.compile("src/totalhp.py")

fZip = zipfile.ZipFile("totalhp.zip", "w")
fZip.write("src/__init__.pyc", WOTVersion+"/scripts/client/mods/__init__.pyc")
fZip.write("src/totalhp.pyc", WOTVersion+"/scripts/client/mods/totalhp.pyc")
fZip.write("src/CameraNode.pyc", WOTVersion+"/scripts/client/CameraNode.pyc")
fZip.close()
