import os
import shutil
import sys
from textnode import TextNode, TextType, markdown_to_html_node, extract_title


def copy_static_to_public(src_path, dest_path):
    # Remove destination directory if it exists
    if os.path.exists(dest_path):
        print(f"Removing existing directory: {dest_path}")
        shutil.rmtree(dest_path)

    # Create destination directory
    print(f"Creating directory: {dest_path}")
    os.mkdir(dest_path)

    # Copy all files and directories recursively
    _copy_directory_contents(src_path, dest_path)


def _copy_directory_contents(src_path, dest_path):
    # List all items in the source directory
    items = os.listdir(src_path)

    for item in items:
        src_item_path = os.path.join(src_path, item)
        dest_item_path = os.path.join(dest_path, item)

        if os.path.isfile(src_item_path):
            # Copy file
            print(f"Copying file: {src_item_path} -> {dest_item_path}")
            shutil.copy(src_item_path, dest_item_path)
        else:
            # Create subdirectory and recursively copy its contents
            print(f"Creating directory: {dest_item_path}")
            os.mkdir(dest_item_path)
            _copy_directory_contents(src_item_path, dest_item_path)


def generate_page(from_path, template_path, dest_path, basepath="/"):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    # Read the markdown file
    with open(from_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Read the template file
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()

    # Extract title
    title = extract_title(markdown_content)

    # Replace placeholders in template
    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)

    # Replace href and src attributes with basepath
    final_html = final_html.replace('href="/', f'href="{basepath}')
    final_html = final_html.replace('src="/', f'src="{basepath}')

    # Ensure destination directory exists
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Write the final HTML file
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_html)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    # Get the original content root for calculating relative paths
    if not hasattr(generate_pages_recursive, 'content_root'):
        generate_pages_recursive.content_root = dir_path_content

    # List all items in the content directory
    items = os.listdir(dir_path_content)

    for item in items:
        src_item_path = os.path.join(dir_path_content, item)

        if os.path.isfile(src_item_path):
            if item.endswith('.md'):
                # Calculate the relative path from the original content root
                rel_path = os.path.relpath(src_item_path, generate_pages_recursive.content_root)
                # Change .md to .html
                html_filename = os.path.splitext(rel_path)[0] + '.html'
                dest_item_path = os.path.join(dest_dir_path, html_filename)

                # Generate the page
                generate_page(src_item_path, template_path, dest_item_path, basepath)
        elif os.path.isdir(src_item_path):
            # Recursively process subdirectories
            generate_pages_recursive(src_item_path, template_path, dest_dir_path, basepath)


def main():
    # Get basepath from command line arguments, default to "/"
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]

    print(f"Using basepath: {basepath}")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    static_path = os.path.join(project_root, "static")
    docs_path = os.path.join(project_root, "docs")

    print("Starting static site generation...")
    copy_static_to_public(static_path, docs_path)
    print("Static files copied successfully!")

    # Generate all pages recursively
    content_path = os.path.join(project_root, "content")
    template_path = os.path.join(project_root, "template.html")

    generate_pages_recursive(content_path, template_path, docs_path, basepath)
    print("All pages generated successfully!")

    # Example TextNode functionality (keeping for testing)
    node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(f"Example TextNode: {node}")

if __name__ == "__main__":
    main()