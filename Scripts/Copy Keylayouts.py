from pathlib import Path
import shutil

path = Path("/Users/klombe/Downloads/Projects/Keyboard Layouts/Ukelele 3.6.1/Resources/Standard Keyboards/")


for file in path.rglob("*.keylayout"):
    shutil.copy2(file, "/Users/klombe/Downloads/Projects/Keyboard Layouts/Apple Keyboard Layouts/")
    print(file)


