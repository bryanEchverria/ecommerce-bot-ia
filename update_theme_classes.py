import os
import re

def update_theme_classes(file_path):
    """Update Tailwind CSS classes to use the new theme system"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Define replacements for theme classes
    replacements = [
        # Background classes
        (r'bg-surface(?![-.:])', 'bg-surface-light dark:bg-surface-dark'),
        (r'bg-background(?![-.:])', 'bg-background-light dark:bg-background-dark'),
        (r'bg-secondary(?![-.:])', 'bg-secondary-light dark:bg-secondary-dark'),
        
        # Text classes
        (r'text-on-surface(?!-)', 'text-on-surface-light dark:text-on-surface-dark'),
        (r'text-on-surface-secondary(?![-.:])', 'text-on-surface-secondary-light dark:text-on-surface-secondary-dark'),
        
        # Border classes
        (r'border-white/10', 'border-gray-200 dark:border-white/10'),
        (r'border-white/20', 'border-gray-300 dark:border-white/20'),
        
        # Hover states
        (r'hover:bg-white/5', 'hover:bg-gray-50 dark:hover:bg-white/5'),
        (r'hover:bg-white/10', 'hover:bg-gray-100 dark:hover:bg-white/10'),
        (r'hover:bg-surface(?![-.:])', 'hover:bg-surface-light dark:hover:bg-surface-dark'),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def update_all_components():
    """Update all React components in the frontend"""
    
    components_dir = r'C:\Users\bryan\OneDrive\Documentos\GitHub\e-commerce-backoffice\frontend\components'
    
    updated_files = []
    
    for filename in os.listdir(components_dir):
        if filename.endswith('.tsx') and filename not in ['Header.tsx', 'Sidebar.tsx', 'ThemeContext.tsx']:
            file_path = os.path.join(components_dir, filename)
            if update_theme_classes(file_path):
                updated_files.append(filename)
                print(f'[UPDATED] {filename}')
            else:
                print(f'[NO CHANGE] {filename}')
    
    print(f'\nUpdated {len(updated_files)} files:')
    for filename in updated_files:
        print(f'  - {filename}')

if __name__ == "__main__":
    print("=== UPDATING THEME CLASSES ===")
    update_all_components()
    print("\n=== UPDATE COMPLETE ===")