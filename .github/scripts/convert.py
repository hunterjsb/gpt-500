#!/usr/bin/env python3
import re

# Read the markdown file
with open('agent/md/indices/GPT20.md', 'r') as f:
    content = f.read()

# Convert headers
html_content = content
html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE) 
html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)

# Convert bold and italic text
html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
html_content = re.sub(r'_(.+?)_', r'<em>\1</em>', html_content)

# Process numbered lists properly
lines = html_content.split('\n')
result_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this is the start of a numbered list
    if re.match(r'^\d+\.\s', line):
        result_lines.append('<ol>')
        
        # Process all numbered list items (including ones separated by empty lines)
        while i < len(lines):
            current_line = lines[i]
            
            if re.match(r'^\d+\.\s', current_line):
                list_content = re.sub(r'^\d+\.\s(.+)', r'\1', current_line)
                
                # Check if next line is description (indented or continuation)
                if i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r'^\d+\.\s', lines[i + 1]) and not lines[i + 1].startswith('#'):
                    description = lines[i + 1].strip()
                    result_lines.append(f'<li>{list_content}<br>{description}</li>')
                    i += 2  # Skip both lines
                else:
                    result_lines.append(f'<li>{list_content}</li>')
                    i += 1
                
                # Skip empty lines after list items
                while i < len(lines) and lines[i].strip() == '':
                    i += 1
            else:
                # If we hit a non-numbered line that's not empty, break
                if current_line.strip():
                    break
                i += 1
        
        result_lines.append('</ol>')
    elif line.startswith('- '):
        # Handle bullet lists
        result_lines.append('<ul>')
        while i < len(lines) and lines[i].startswith('- '):
            content = lines[i][2:]
            result_lines.append(f'<li>{content}</li>')
            i += 1
        result_lines.append('</ul>')
    else:
        result_lines.append(line)
        i += 1

html_content = '\n'.join(result_lines)

# Convert paragraphs
paragraphs = html_content.split('\n\n')
final_content = []

for para in paragraphs:
    para = para.strip()
    if para and not para.startswith('<') and not re.match(r'.*</?(h[123]|ol|ul|li).*>', para):
        final_content.append(f'<p>{para}</p>')
    elif para:
        final_content.append(para)

html_content = '\n\n'.join(final_content)

# Create full HTML document
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