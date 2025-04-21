import os
import re
import sys

def fix_func_now_in_file(file_path):
    """Fix func.now to text('NOW()') in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add text import if not already present
    if 'from sqlalchemy.sql import func' in content and 'from sqlalchemy import text' not in content and 'from sqlalchemy.sql import text' not in content:
        content = content.replace(
            'from sqlalchemy.sql import func',
            'from sqlalchemy.sql import func, text'
        )
    
    # Replace server_default=func.now with server_default=text('NOW()')
    content = re.sub(r'server_default=func\.now\(\)', r"server_default=text('NOW()')", content)
    content = re.sub(r'server_default=func\.now(?!\()', r"server_default=text('NOW()')", content)
    
    # Keep onupdate=func.now() as is, it works differently
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def main():
    """Fix func.now to text('NOW()') in all model files."""
    model_files = [
        'app/models/user.py',
        'app/models/post.py',
        'app/models/award.py',
        'app/models/course.py',
        'app/models/learning_path.py',
        'app/models/quiz.py',
        'app/models/series.py',
        'app/models/marketing.py',
        'app/models/prelaunch.py',
        'app/models/booklet.py',
    ]
    
    for file_path in model_files:
        if os.path.exists(file_path):
            print(f"Fixing {file_path}...")
            fixed = fix_func_now_in_file(file_path)
            if fixed:
                print(f"  ✅ Fixed {file_path}")
            else:
                print(f"  ❌ Failed to fix {file_path}")
        else:
            print(f"  ⚠️ File not found: {file_path}")
    
    print("Done!")

if __name__ == "__main__":
    main()
