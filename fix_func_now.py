import os
import re
import sys

def fix_func_now_in_file(file_path):
    """Fix func.now to func.now() in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace server_default=func.now with server_default=func.now()
    content = re.sub(r'server_default=func\.now(?!\()', 'server_default=func.now()', content)
    
    # Replace onupdate=func.now with onupdate=func.now()
    content = re.sub(r'onupdate=func\.now(?!\()', 'onupdate=func.now()', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

def main():
    """Fix func.now to func.now() in all model files."""
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
