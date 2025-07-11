#!/usr/bin/env python
import os
import re

def update_file_colors(file_path):
    """Update all color classes in a file to use deep blue and white only."""
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Color replacement patterns
    replacements = [
        # Background colors
        (r'bg-blue-\d+', 'bg-[#1e3a8a]'),
        (r'bg-indigo-\d+', 'bg-[#1e3a8a]'),
        (r'bg-green-\d+', 'bg-[#1e3a8a]'),
        (r'bg-purple-\d+', 'bg-[#1e3a8a]'),
        (r'bg-pink-\d+', 'bg-[#1e3a8a]'),
        (r'bg-red-\d+', 'bg-[#1e3a8a]'),
        (r'bg-yellow-\d+', 'bg-[#1e3a8a]'),
        (r'bg-orange-\d+', 'bg-[#1e3a8a]'),
        (r'bg-teal-\d+', 'bg-[#1e3a8a]'),
        (r'bg-cyan-\d+', 'bg-[#1e3a8a]'),
        
        # Text colors
        (r'text-blue-\d+', 'text-[#1e3a8a]'),
        (r'text-indigo-\d+', 'text-[#1e3a8a]'),
        (r'text-green-\d+', 'text-[#1e3a8a]'),
        (r'text-purple-\d+', 'text-[#1e3a8a]'),
        (r'text-pink-\d+', 'text-[#1e3a8a]'),
        (r'text-red-\d+', 'text-[#1e3a8a]'),
        (r'text-yellow-\d+', 'text-[#1e3a8a]'),
        (r'text-orange-\d+', 'text-[#1e3a8a]'),
        (r'text-teal-\d+', 'text-[#1e3a8a]'),
        (r'text-cyan-\d+', 'text-[#1e3a8a]'),
        
        # Border colors
        (r'border-blue-\d+', 'border-[#1e3a8a]'),
        (r'border-indigo-\d+', 'border-[#1e3a8a]'),
        (r'border-green-\d+', 'border-[#1e3a8a]'),
        (r'border-purple-\d+', 'border-[#1e3a8a]'),
        (r'border-pink-\d+', 'border-[#1e3a8a]'),
        (r'border-red-\d+', 'border-[#1e3a8a]'),
        (r'border-yellow-\d+', 'border-[#1e3a8a]'),
        (r'border-orange-\d+', 'border-[#1e3a8a]'),
        (r'border-teal-\d+', 'border-[#1e3a8a]'),
        (r'border-cyan-\d+', 'border-[#1e3a8a]'),
        
        # Focus ring colors
        (r'focus:ring-blue-\d+', 'focus:ring-[#1e3a8a]'),
        (r'focus:ring-indigo-\d+', 'focus:ring-[#1e3a8a]'),
        (r'focus:ring-green-\d+', 'focus:ring-[#1e3a8a]'),
        (r'focus:ring-purple-\d+', 'focus:ring-[#1e3a8a]'),
        (r'focus:ring-pink-\d+', 'focus:ring-[#1e3a8a]'),
        (r'focus:ring-red-\d+', 'focus:ring-[#1e3a8a]'),
        (r'focus:ring-yellow-\d+', 'focus:ring-[#1e3a8a]'),
        (r'focus:ring-orange-\d+', 'focus:ring-[#1e3a8a]'),
        (r'focus:ring-teal-\d+', 'focus:ring-[#1e3a8a]'),
        (r'focus:ring-cyan-\d+', 'focus:ring-[#1e3a8a]'),
        
        # Focus border colors
        (r'focus:border-blue-\d+', 'focus:border-[#1e3a8a]'),
        (r'focus:border-indigo-\d+', 'focus:border-[#1e3a8a]'),
        (r'focus:border-green-\d+', 'focus:border-[#1e3a8a]'),
        (r'focus:border-purple-\d+', 'focus:border-[#1e3a8a]'),
        (r'focus:border-pink-\d+', 'focus:border-[#1e3a8a]'),
        (r'focus:border-red-\d+', 'focus:border-[#1e3a8a]'),
        (r'focus:border-yellow-\d+', 'focus:border-[#1e3a8a]'),
        (r'focus:border-orange-\d+', 'focus:border-[#1e3a8a]'),
        (r'focus:border-teal-\d+', 'focus:border-[#1e3a8a]'),
        (r'focus:border-cyan-\d+', 'focus:border-[#1e3a8a]'),
        
        # Hover colors
        (r'hover:bg-blue-\d+', 'hover:bg-[#1e3a8a]'),
        (r'hover:bg-indigo-\d+', 'hover:bg-[#1e3a8a]'),
        (r'hover:bg-green-\d+', 'hover:bg-[#1e3a8a]'),
        (r'hover:bg-purple-\d+', 'hover:bg-[#1e3a8a]'),
        (r'hover:bg-pink-\d+', 'hover:bg-[#1e3a8a]'),
        (r'hover:bg-red-\d+', 'hover:bg-[#1e3a8a]'),
        (r'hover:bg-yellow-\d+', 'hover:bg-[#1e3a8a]'),
        (r'hover:bg-orange-\d+', 'hover:bg-[#1e3a8a]'),
        (r'hover:bg-teal-\d+', 'hover:bg-[#1e3a8a]'),
        (r'hover:bg-cyan-\d+', 'hover:bg-[#1e3a8a]'),
        
        (r'hover:text-blue-\d+', 'hover:text-[#1e3a8a]'),
        (r'hover:text-indigo-\d+', 'hover:text-[#1e3a8a]'),
        (r'hover:text-green-\d+', 'hover:text-[#1e3a8a]'),
        (r'hover:text-purple-\d+', 'hover:text-[#1e3a8a]'),
        (r'hover:text-pink-\d+', 'hover:text-[#1e3a8a]'),
        (r'hover:text-red-\d+', 'hover:text-[#1e3a8a]'),
        (r'hover:text-yellow-\d+', 'hover:text-[#1e3a8a]'),
        (r'hover:text-orange-\d+', 'hover:text-[#1e3a8a]'),
        (r'hover:text-teal-\d+', 'hover:text-[#1e3a8a]'),
        (r'hover:text-cyan-\d+', 'hover:text-[#1e3a8a]'),
        
        # Gradient replacements
        (r'from-blue-\d+', 'from-[#1e3a8a]'),
        (r'to-blue-\d+', 'to-[#1e3a8a]'),
        (r'from-indigo-\d+', 'from-[#1e3a8a]'),
        (r'to-indigo-\d+', 'to-[#1e3a8a]'),
        (r'from-green-\d+', 'from-[#1e3a8a]'),
        (r'to-green-\d+', 'to-[#1e3a8a]'),
        (r'from-purple-\d+', 'from-[#1e3a8a]'),
        (r'to-purple-\d+', 'to-[#1e3a8a]'),
        (r'from-pink-\d+', 'from-[#1e3a8a]'),
        (r'to-pink-\d+', 'to-[#1e3a8a]'),
        
        # Replace medium-blue, light-blue, very-light-blue with deep-blue
        (r'medium-blue', '[#1e3a8a]'),
        (r'light-blue', 'white'),
        (r'very-light-blue', 'white'),
        
        # Replace specific color codes
        (r'#3b82f6', '#1e3a8a'),
        (r'#60a5fa', '#ffffff'),
        (r'#dbeafe', '#ffffff'),
        (r'#4F46E5', '#1e3a8a'),
    ]
    
    # Apply all replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Update all template files."""
    template_dir = "templates/core"
    
    # Get all HTML files
    html_files = []
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Found {len(html_files)} HTML files to update")
    
    # Update each file
    for file_path in html_files:
        try:
            update_file_colors(file_path)
            print(f"✅ Updated: {file_path}")
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
    
    # Also update CSS files
    css_files = [
        "static/css/admin-custom.css",
    ]
    
    for css_file in css_files:
        if os.path.exists(css_file):
            try:
                update_file_colors(css_file)
                print(f"✅ Updated: {css_file}")
            except Exception as e:
                print(f"❌ Error updating {css_file}: {e}")
    
    print("\n🎉 All files updated to use deep blue (#1e3a8a) and white (#ffffff)!")

if __name__ == "__main__":
    main() 