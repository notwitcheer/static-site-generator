import re
from enum import Enum
from htmlnode import LeafNode, ParentNode

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError(f"Unsupported text type: {text_node.text_type}")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text = old_node.text
        if delimiter not in text:
            new_nodes.append(old_node)
            continue

        parts = text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown syntax: unmatched delimiter '{delimiter}' in text '{text}'")

        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]

    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text = old_node.text
        images = extract_markdown_images(text)

        if not images:
            new_nodes.append(old_node)
            continue

        current_text = text
        for alt_text, url in images:
            full_image_markdown = f"![{alt_text}]({url})"

            parts = current_text.split(full_image_markdown, 1)

            if len(parts) != 2:
                continue

            before_text = parts[0]
            after_text = parts[1]

            if before_text:
                new_nodes.append(TextNode(before_text, TextType.TEXT))

            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))

            current_text = after_text

        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text = old_node.text
        links = extract_markdown_links(text)

        if not links:
            new_nodes.append(old_node)
            continue

        current_text = text
        for link_text, url in links:
            full_link_markdown = f"[{link_text}]({url})"

            parts = current_text.split(full_link_markdown, 1)

            if len(parts) != 2:
                continue

            before_text = parts[0]
            after_text = parts[1]

            if before_text:
                new_nodes.append(TextNode(before_text, TextType.TEXT))

            new_nodes.append(TextNode(link_text, TextType.LINK, url))

            current_text = after_text

        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))

    return new_nodes


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []

    for block in blocks:
        stripped_block = block.strip()
        if stripped_block:
            filtered_blocks.append(stripped_block)

    return filtered_blocks


def block_to_block_type(block):
    lines = block.split('\n')

    # Check for heading (1-6 # characters followed by space)
    if block.startswith('#'):
        # Count leading # characters
        hash_count = 0
        for char in block:
            if char == '#':
                hash_count += 1
            else:
                break

        # Must be 1-6 # characters followed by a space
        if 1 <= hash_count <= 6 and len(block) > hash_count and block[hash_count] == ' ':
            return BlockType.HEADING

    # Check for code block (starts with ``` and ends with ```)
    if len(lines) > 1 and block.startswith('```') and block.endswith('```'):
        return BlockType.CODE

    # Check for quote block (every line starts with >)
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE

    # Check for unordered list (every line starts with - followed by space)
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST

    # Check for ordered list (lines start with number. followed by space, incrementing from 1)
    if len(lines) > 0:
        is_ordered_list = True
        for i, line in enumerate(lines):
            expected_number = i + 1
            expected_start = f"{expected_number}. "
            if not line.startswith(expected_start):
                is_ordered_list = False
                break

        if is_ordered_list:
            return BlockType.ORDERED_LIST

    # Default to paragraph
    return BlockType.PARAGRAPH


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph_text = " ".join(lines)
    children = text_to_children(paragraph_text)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break

    if level < 1 or level > 6:
        raise ValueError(f"Invalid heading level: {level}")

    text = block[level + 1:]  # Skip the hashes and space
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("Invalid code block")

    text = block[4:-3]  # Remove ``` from start and end, plus newline after opening ```
    code_node = LeafNode("code", text)
    return ParentNode("pre", [code_node])


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("Invalid quote block")
        new_lines.append(line[1:].lstrip())  # Remove > and any following space

    content = "\n".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)


def unordered_list_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]  # Remove "- "
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def ordered_list_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        # Find the first space after the number and period
        first_space = item.find(". ") + 2
        text = item[first_space:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.PARAGRAPH:
            children.append(paragraph_to_html_node(block))
        elif block_type == BlockType.HEADING:
            children.append(heading_to_html_node(block))
        elif block_type == BlockType.CODE:
            children.append(code_to_html_node(block))
        elif block_type == BlockType.QUOTE:
            children.append(quote_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            children.append(unordered_list_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            children.append(ordered_list_to_html_node(block))
        else:
            raise ValueError(f"Invalid block type: {block_type}")

    return ParentNode("div", children)


def extract_title(markdown):
    lines = markdown.strip().split('\n')

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('# ') or stripped_line == '#':
            if not stripped_line.startswith('## '):
                if stripped_line == '#':
                    return ""
                title = stripped_line[2:].strip()
                return title

    raise Exception("No h1 header found")
