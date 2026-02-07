#!/usr/bin/env python3
import os

def generate_index():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    readme_path = os.path.join(root_dir, "README.md")
    
    files = sorted([f for f in os.listdir(root_dir) if f.endswith(".md") and f != "README.md"])
    
    content = ["# MVP P0 Documentation Index\n\n"]
    content.append("Auto-generated index of MVP P0 specifications and plans.\n\n")
    content.append("| File | Description |\n")
    content.append("|------|-------------|\n")
    
    for filename in files:
        # Extract title from first line
        description = "No description"
        try:
            with open(os.path.join(root_dir, filename), "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    description = first_line[2:]
        except Exception:
            pass
            
        content.append(f"| [{filename}]({filename}) | {description} |\n")
    
    content.append("\n*Last updated: " + os.popen("date").read().strip() + "*\n")
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.writelines(content)
    
    print(f"Index generated at {readme_path}")

if __name__ == "__main__":
    generate_index()
