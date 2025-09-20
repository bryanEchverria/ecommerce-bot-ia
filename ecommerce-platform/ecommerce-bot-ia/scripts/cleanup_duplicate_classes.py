import os
import re

def cleanup_duplicate_dark_classes(file_path):
    """Clean up duplicate dark: classes in Tailwind CSS"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix duplicate border classes like "border-gray-200 dark:border-gray-200 dark:border-white/10"
    content = re.sub(r'border-gray-200 dark:border-gray-200 dark:border-white/10', 'border-gray-200 dark:border-white/10', content)
    content = re.sub(r'border-gray-300 dark:border-gray-300 dark:border-white/20', 'border-gray-300 dark:border-white/20', content)
    
    # Fix duplicate hover classes like "hover:bg-gray-50 dark:hover:bg-gray-50 dark:hover:bg-white/5"
    content = re.sub(r'hover:bg-gray-50 dark:hover:bg-gray-50 dark:hover:bg-white/5', 'hover:bg-gray-50 dark:hover:bg-white/5', content)
    content = re.sub(r'hover:bg-gray-100 dark:hover:bg-gray-100 dark:hover:bg-white/10', 'hover:bg-gray-100 dark:hover:bg-white/10', content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def cleanup_all_components():
    """Clean up all React components in the frontend"""
    
    components_dir = r'C:\Users\bryan\OneDrive\Documentos\GitHub\e-commerce-backoffice\frontend\components'
    
    cleaned_files = []
    
    for filename in os.listdir(components_dir):
        if filename.endswith('.tsx'):
            file_path = os.path.join(components_dir, filename)
            if cleanup_duplicate_dark_classes(file_path):
                cleaned_files.append(filename)
                print(f'[CLEANED] {filename}')
            else:
                print(f'[NO CLEANUP NEEDED] {filename}')
    
    print(f'\nCleaned {len(cleaned_files)} files:')
    for filename in cleaned_files:
        print(f'  - {filename}')

if __name__ == "__main__":
    print("=== CLEANING DUPLICATE DARK CLASSES ===")
    cleanup_all_components()
    print("\n=== CLEANUP COMPLETE ===")