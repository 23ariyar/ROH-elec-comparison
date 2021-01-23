import os
import shutil

files_to_rem = ["politician.db", "practice.txt"]

for file in files_to_rem:
    if os.path.exists(file): os.remove(file)
    else: print(file + " does not exist")

shutil.rmtree('images')
os.mkdir('images')


