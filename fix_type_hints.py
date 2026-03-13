import os
import re

for root, _, files in os.walk("src"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r") as f:
                content = f.read()

            content = re.sub(r'-> Any:', r':', content)
            content = re.sub(r': Any\b', r'', content)

            with open(path, "w") as f:
                f.write(content)
