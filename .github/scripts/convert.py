#!/usr/bin/env python3
import re

# Read the markdown file
with open('agent/md/indices/GPT20.md', 'r') as f:
    content = f.read()

# Simple markdown to HTML conversion
html_content = content
html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE) 
html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
html_content = re.sub(r'_(.+?)_', r'<em>\1</em>', html_content)

# Convert numbered lists
lines = html_content.split('\n')
new_lines = []
in_ol = False

for line in lines:
    if re.match(r'^\d+\.\s', line):
        if not in_ol:
            new_lines.append('<ol>')
            in_ol = True
        content = re.sub(r'^\d+\.\s(.+)', r'\1', line)
        new_lines.append(f'<li>{content}</li>')
    elif line.startswith('- '):
        new_lines.append(f'<li>{line[2:]}</li>')
    else:
        if in_ol and line.strip() == '':
            new_lines.append('</ol>')
            in_ol = False
        new_lines.append(line)

if in_ol:
    new_lines.append('</ol>')

html_content = '\n'.join(new_lines)

# Convert paragraphs
html_content = re.sub(r'\n\n+', '</p>\n<p>', html_content)
html_content = f'<p>{html_content}</p>'

# Clean up headers and lists in paragraphs
html_content = re.sub(r'<p>(<h[123]>)', r'\1', html_content)
html_content = re.sub(r'(</h[123]>)</p>', r'\1', html_content)
html_content = re.sub(r'<p>(</?ol>)', r'\1', html_content)
html_content = re.sub(r'(</?ol>)</p>', r'\1', html_content)
html_content = re.sub(r'<p>(<li>)', r'\1', html_content)
html_content = re.sub(r'(</li>)</p>', r'\1', html_content)

# Create full HTML
full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPT20 Stock Index</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            line-height: 1.6; 
            color: #333; 
        }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h3 {{ color: #7f8c8d; }}
        strong {{ color: #2980b9; }}
        ol li {{ margin-bottom: 10px; }}
        em {{ font-style: italic; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div id="content">
        {html_content}
    </div>
</body>
</html>'''

# Write to docs/index.html
with open('docs/index.html', 'w') as f:
    f.write(full_html)

print("HTML updated successfully")