import os
import shutil
from textnode import TextNode, TextType


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


def main():
    # Copy static files to public directory
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    static_path = os.path.join(project_root, "static")
    public_path = os.path.join(project_root, "public")

    print("Starting static site generation...")
    copy_static_to_public(static_path, public_path)
    print("Static files copied successfully!")

    # Example TextNode functionality (keeping for testing)
    node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(f"Example TextNode: {node}")

if __name__ == "__main__":
    main()