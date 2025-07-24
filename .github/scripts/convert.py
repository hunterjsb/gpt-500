#!/usr/bin/env python3
import re

# Read the markdown file
with open('agent/md/indices/GPT20.md', 'r') as f:
    content = f.read()

# Process line by line to properly handle lists
lines = content.split('\n')
new_lines = []
in_ol = False
in_ul = False

for i, line in enumerate(lines):
    # Headers
    if line.startswith('# '):
        if in_ol:
            new_lines.append('</ol>')
            in_ol = False
        if in_ul:
            new_lines.append('</ul>')
            in_ul = False
        new_lines.append(f'<h1>{line[2:]}</h1>')
    elif line.startswith('## '):
        if in_ol:
            new_lines.append('</ol>')
            in_ol = False
        if in_ul:
            new_lines.append('</ul>')
            in_ul = False
        new_lines.append(f'<h2>{line[3:]}</h2>')
    elif line.startswith('### '):
        if in_ol:
            new_lines.append('</ol>')
            in_ol = False
        if in_ul:
            new_lines.append('</ul>')
            in_ul = False
        new_lines.append(f'<h3>{line[4:]}</h3>')
    # Numbered list items
    elif re.match(r'^\d+\.\s', line):
        if in_ul:
            new_lines.append('</ul>')
            in_ul = False
        if not in_ol:
            new_lines.append('<ol>')
            in_ol = True
        content = re.sub(r'^\d+\.\s(.+)', r'\1', line)
        # Handle multi-line list items
        next_line = lines[i+1] if i+1 < len(lines) else ''
        if next_line.strip() and not next_line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.', '15.', '16.', '17.', '18.', '19.', '20.')) and not next_line.startswith(('#', '-')):
            new_lines.append(f'<li>{content}<br>{next_line.strip()}</li>')
            lines[i+1] = ''  # Skip the next line since we've included it
        else:
            new_lines.append(f'<li>{content}</li>')
    # Bullet list items
    elif line.startswith('- '):
        if in_ol:
            new_lines.append('</ol>')
            in_ol = False
        if not in_ul:
            new_lines.append('<ul>')
            in_ul = True
        new_lines.append(f'<li>{line[2:]}</li>')
    # Empty lines - close lists if needed
    elif line.strip() == '':
        if in_ol:
            new_lines.append('</ol>')
            in_ol = False
        if in_ul:
            new_lines.append('</ul>')
            in_ul = False
        new_lines.append('')
    # Regular content
    else:
        # Don't close lists for continuation lines that start with spaces
        if not line.startswith('   '):
            if in_ol:
                new_lines.append('</ol>')
                in_ol = False
            if in_ul:
                new_lines.append('</ul>')
                in_ul = False
        if line.strip():
            new_lines.append(line)

# Close any remaining lists
if in_ol:
    new_lines.append('</ol>')
if in_ul:
    new_lines.append('</ul>')

html_content = '\n'.join(new_lines)

# Apply text formatting
html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
html_content = re.sub(r'_(.+?)_', r'<em>\1</em>', html_content)

# Convert paragraphs (avoid wrapping headers and lists)
paragraphs = html_content.split('\n\n')
final_content = []

for para in paragraphs:
    para = para.strip()
    if para and not para.startswith('<') and not para.endswith('>'):
        final_content.append(f'<p>{para}</p>')
    else:
        final_content.append(para)

html_content = '\n\n'.join(final_content)

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