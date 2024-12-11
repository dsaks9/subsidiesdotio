import re

def fix_bijdrage_formatting(input_path, output_path):
    # Read the file content
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match the problematic section
    pattern = r'( Minimale bijdrage:\s+.*?\n) Maximale\s+(\s+)(.*?\n) bijdrage:'
    
    # Replace with corrected format
    # Group 1: Minimale bijdrage line
    # Group 2: Original spacing
    # Group 3: The value that was on the Maximale line
    fixed_content = re.sub(
        pattern,
        r'\1 Maximale bijdrage:\2\3',
        content
    )
    
    # Write the corrected content to the new file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

if __name__ == "__main__":
    input_path = "../data/v_two_subsidies.txt"
    output_path = "../data/v_two_subsidies_fixed.txt"
    fix_bijdrage_formatting(input_path, output_path)
