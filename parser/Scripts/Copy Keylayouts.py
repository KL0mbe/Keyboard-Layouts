from pathlib import Path
import shutil

# needs to change to pull from apple as we dont use Ukelele anymore
path = Path("/Users/klombe/Downloads/Projects/Keyboard Layouts/Ukelele 3.6.1/Resources/Standard Keyboards/")


for file in path.rglob("*.keylayout"):
    shutil.copy2(file, "/Users/klombe/Downloads/Projects/Keyboard Layouts/parser/Apple Keyboard Layouts/")
    print(file)


