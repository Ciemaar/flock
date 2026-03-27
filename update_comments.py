import os
import glob

def add_comments(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []

    for i, line in enumerate(lines):
        if line.strip() == 'except ImportError:':
            # Check context before
            if i > 0 and 'try:' in lines[i-1] or 'try:' in lines[i-2]:
                module_name = ''
                if 'import' in lines[i-1]:
                    module_name = lines[i-1].strip().replace('import ', '').replace('from ', '').split(' ')[0]
                elif 'import' in lines[i-2]:
                    module_name = lines[i-2].strip().replace('import ', '').replace('from ', '').split(' ')[0]

                # Check if comment already exists on the next line
                if i + 1 < len(lines) and 'MicroPython' in lines[i+1]:
                    new_lines.append(line)
                    continue

                if not line.endswith('# MicroPython compatibility'):
                    new_lines.append(line + f'  # MicroPython compatibility fallback for missing {module_name}')
                    continue
        new_lines.append(line)

    with open(filepath, 'w') as f:
        f.write('\n'.join(new_lines))

for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            add_comments(os.path.join(root, file))

print("Comments added.")
