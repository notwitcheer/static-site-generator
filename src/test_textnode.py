import unittest

from textnode import TextNode, TextType, BlockType, text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, markdown_to_html_node, extract_title
from htmlnode import LeafNode


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        node2 = TextNode("Click here", TextType.LINK, "https://example.com")
        self.assertEqual(node, node2)

    def test_not_eq_different_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_text_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_eq_different_url(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        node2 = TextNode("Click here", TextType.LINK, "https://different.com")
        self.assertNotEqual(node, node2)

    def test_eq_url_none(self):
        node = TextNode("This is a text node", TextType.TEXT, None)
        node2 = TextNode("This is a text node", TextType.TEXT, None)
        self.assertEqual(node, node2)

    def test_not_eq_one_url_none(self):
        node = TextNode("Click here", TextType.LINK, None)
        node2 = TextNode("Click here", TextType.LINK, "https://example.com")
        self.assertNotEqual(node, node2)


class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")
        self.assertEqual(html_node.props, None)

    def test_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")
        self.assertEqual(html_node.props, None)

    def test_code(self):
        node = TextNode("console.log('hello')", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "console.log('hello')")
        self.assertEqual(html_node.props, None)

    def test_link(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://example.com/image.png", "alt": "Alt text"})

    def test_unsupported_type_raises_exception(self):
        class UnsupportedType:
            pass

        node = TextNode("text", UnsupportedType())
        with self.assertRaises(ValueError) as context:
            text_node_to_html_node(node)
        self.assertIn("Unsupported text type", str(context.exception))

    def test_link_with_none_url(self):
        node = TextNode("Link text", TextType.LINK, None)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Link text")
        self.assertEqual(html_node.props, {"href": None})

    def test_image_with_none_url(self):
        node = TextNode("Alt text", TextType.IMAGE, None)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": None, "alt": "Alt text"})

    def test_conversion_to_html_output(self):
        text_node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        self.assertEqual(html_node.to_html(), "<b>Bold text</b>")

        link_node = TextNode("Google", TextType.LINK, "https://google.com")
        html_link = text_node_to_html_node(link_node)
        self.assertEqual(html_link.to_html(), '<a href="https://google.com">Google</a>')

        img_node = TextNode("A cat", TextType.IMAGE, "cat.jpg")
        html_img = text_node_to_html_node(img_node)
        self.assertEqual(html_img.to_html(), '<img src="cat.jpg" alt="A cat"></img>')


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_code_block(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_bold_text(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_italic_text(self):
        node = TextNode("This is *italic* text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_multiple_delimiters(self):
        node = TextNode("This has `code` and `more code` in it", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("more code", TextType.CODE),
            TextNode(" in it", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_no_delimiter(self):
        node = TextNode("This is plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("This is plain text", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_split_non_text_node_unchanged(self):
        node = TextNode("Bold text", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [TextNode("Bold text", TextType.BOLD)]
        self.assertEqual(new_nodes, expected)

    def test_split_multiple_nodes_mixed_types(self):
        nodes = [
            TextNode("This is **bold** text", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("This is **also bold**", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("This is ", TextType.TEXT),
            TextNode("also bold", TextType.BOLD),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_unmatched_delimiter_raises_error(self):
        node = TextNode("This has unmatched `delimiter", TextType.TEXT)
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertIn("Invalid markdown syntax", str(context.exception))
        self.assertIn("unmatched delimiter", str(context.exception))

    def test_split_starting_with_delimiter(self):
        node = TextNode("`code` at the start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("code", TextType.CODE),
            TextNode(" at the start", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_ending_with_delimiter(self):
        node = TextNode("Text ending with `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Text ending with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_only_delimiter_content(self):
        node = TextNode("`only code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [TextNode("only code", TextType.CODE)]
        self.assertEqual(new_nodes, expected)

    def test_split_empty_delimiter_content(self):
        node = TextNode("Text with `` empty", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("", TextType.CODE),
            TextNode(" empty", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_complex_markdown(self):
        node = TextNode("Start `code1` middle `code2` end", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("code1", TextType.CODE),
            TextNode(" middle ", TextType.TEXT),
            TextNode("code2", TextType.CODE),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_adjacent_delimiters(self):
        node = TextNode("`code1``code2`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("code1", TextType.CODE),
            TextNode("code2", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]
        self.assertListEqual(expected, matches)

    def test_extract_no_images(self):
        matches = extract_markdown_images("This is just plain text with no images")
        self.assertListEqual([], matches)

    def test_extract_image_empty_alt_text(self):
        matches = extract_markdown_images("This has an image with ![](https://example.com/image.png)")
        self.assertListEqual([("", "https://example.com/image.png")], matches)

    def test_extract_image_complex_alt_text(self):
        matches = extract_markdown_images("![A very long alt text with spaces and symbols!](https://example.com/image.jpg)")
        self.assertListEqual([("A very long alt text with spaces and symbols!", "https://example.com/image.jpg")], matches)

    def test_extract_image_with_query_params(self):
        matches = extract_markdown_images("![image](https://example.com/image.png?size=large&format=jpg)")
        self.assertListEqual([("image", "https://example.com/image.png?size=large&format=jpg")], matches)

    def test_extract_image_with_path(self):
        matches = extract_markdown_images("![local image](./images/photo.jpg)")
        self.assertListEqual([("local image", "./images/photo.jpg")], matches)

    def test_extract_images_mixed_with_links(self):
        text = "Here's an image ![cat](cat.jpg) and a [link](https://example.com)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("cat", "cat.jpg")], matches)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
        self.assertListEqual(expected, matches)

    def test_extract_single_link(self):
        matches = extract_markdown_links("Check out [this link](https://example.com)")
        self.assertListEqual([("this link", "https://example.com")], matches)

    def test_extract_no_links(self):
        matches = extract_markdown_links("This is just plain text with no links")
        self.assertListEqual([], matches)

    def test_extract_link_empty_text(self):
        matches = extract_markdown_links("This has a link with [](https://example.com)")
        self.assertListEqual([("", "https://example.com")], matches)

    def test_extract_link_complex_anchor_text(self):
        matches = extract_markdown_links("Visit [Boot.dev - Learn to Code!](https://boot.dev)")
        self.assertListEqual([("Boot.dev - Learn to Code!", "https://boot.dev")], matches)

    def test_extract_link_with_query_params(self):
        matches = extract_markdown_links("Search [Google](https://google.com/search?q=python)")
        self.assertListEqual([("Google", "https://google.com/search?q=python")], matches)

    def test_extract_local_link(self):
        matches = extract_markdown_links("See [documentation](./docs/readme.md)")
        self.assertListEqual([("documentation", "./docs/readme.md")], matches)

    def test_extract_links_not_confused_by_images(self):
        text = "Here's a ![image](image.jpg) and a [link](https://example.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "https://example.com")], matches)

    def test_extract_multiple_mixed_content(self):
        text = "Check ![image](pic.jpg) and [link1](url1.com) and ![another](pic2.jpg) and [link2](url2.com)"
        matches = extract_markdown_links(text)
        expected = [("link1", "url1.com"), ("link2", "url2.com")]
        self.assertListEqual(expected, matches)

    def test_extract_links_with_nested_brackets_in_url(self):
        matches = extract_markdown_links("Visit [site](https://example.com/page[1])")
        self.assertListEqual([("site", "https://example.com/page[1]")], matches)

    def test_extract_links_adjacent(self):
        matches = extract_markdown_links("[First](url1.com)[Second](url2.com)")
        expected = [("First", "url1.com"), ("Second", "url2.com")]
        self.assertListEqual(expected, matches)


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_single_image(self):
        node = TextNode("Here is ![an image](url.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("an image", TextType.IMAGE, "url.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_no_images(self):
        node = TextNode("This is just plain text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("This is just plain text with no images", TextType.TEXT)]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_at_start(self):
        node = TextNode("![start image](start.jpg) at the beginning", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("start image", TextType.IMAGE, "start.jpg"),
            TextNode(" at the beginning", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_at_end(self):
        node = TextNode("Text ending with ![end image](end.jpg)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text ending with ", TextType.TEXT),
            TextNode("end image", TextType.IMAGE, "end.jpg"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_only_image(self):
        node = TextNode("![only image](only.jpg)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("only image", TextType.IMAGE, "only.jpg")]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_empty_alt(self):
        node = TextNode("Image with ![](empty_alt.jpg) empty alt", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Image with ", TextType.TEXT),
            TextNode("", TextType.IMAGE, "empty_alt.jpg"),
            TextNode(" empty alt", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_non_text_node_unchanged(self):
        node = TextNode("Bold text", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("Bold text", TextType.BOLD)]
        self.assertListEqual(expected, new_nodes)

    def test_split_multiple_nodes_mixed_types(self):
        nodes = [
            TextNode("Text with ![img1](url1.jpg)", TextType.TEXT),
            TextNode("Already an image", TextType.IMAGE, "existing.jpg"),
            TextNode("More text with ![img2](url2.jpg)", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(nodes)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("img1", TextType.IMAGE, "url1.jpg"),
            TextNode("Already an image", TextType.IMAGE, "existing.jpg"),
            TextNode("More text with ", TextType.TEXT),
            TextNode("img2", TextType.IMAGE, "url2.jpg"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_images_adjacent(self):
        node = TextNode("![img1](url1.jpg)![img2](url2.jpg)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("img1", TextType.IMAGE, "url1.jpg"),
            TextNode("img2", TextType.IMAGE, "url2.jpg"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_images_complex_urls(self):
        node = TextNode(
            "Image with ![complex](https://example.com/image.png?size=large&format=jpg) complex URL",
            TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Image with ", TextType.TEXT),
            TextNode("complex", TextType.IMAGE, "https://example.com/image.png?size=large&format=jpg"),
            TextNode(" complex URL", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links_basic(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_single_link(self):
        node = TextNode("Check out [this link](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Check out ", TextType.TEXT),
            TextNode("this link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_no_links(self):
        node = TextNode("This is just plain text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("This is just plain text with no links", TextType.TEXT)]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_at_start(self):
        node = TextNode("[start link](start.com) at the beginning", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("start link", TextType.LINK, "start.com"),
            TextNode(" at the beginning", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_at_end(self):
        node = TextNode("Text ending with [end link](end.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text ending with ", TextType.TEXT),
            TextNode("end link", TextType.LINK, "end.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_only_link(self):
        node = TextNode("[only link](only.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("only link", TextType.LINK, "only.com")]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_empty_text(self):
        node = TextNode("Link with [](empty_text.com) empty text", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Link with ", TextType.TEXT),
            TextNode("", TextType.LINK, "empty_text.com"),
            TextNode(" empty text", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_non_text_node_unchanged(self):
        node = TextNode("Bold text", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("Bold text", TextType.BOLD)]
        self.assertListEqual(expected, new_nodes)

    def test_split_multiple_nodes_mixed_types(self):
        nodes = [
            TextNode("Text with [link1](url1.com)", TextType.TEXT),
            TextNode("Already a link", TextType.LINK, "existing.com"),
            TextNode("More text with [link2](url2.com)", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(nodes)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("link1", TextType.LINK, "url1.com"),
            TextNode("Already a link", TextType.LINK, "existing.com"),
            TextNode("More text with ", TextType.TEXT),
            TextNode("link2", TextType.LINK, "url2.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_adjacent(self):
        node = TextNode("[link1](url1.com)[link2](url2.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("link1", TextType.LINK, "url1.com"),
            TextNode("link2", TextType.LINK, "url2.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_complex_urls(self):
        node = TextNode(
            "Link with [complex](https://example.com/page?param=value&other=data) complex URL",
            TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Link with ", TextType.TEXT),
            TextNode("complex", TextType.LINK, "https://example.com/page?param=value&other=data"),
            TextNode(" complex URL", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_ignore_images(self):
        node = TextNode("Here's an ![image](img.jpg) and a [link](link.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Here's an ![image](img.jpg) and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "link.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_links_complex_anchor_text(self):
        node = TextNode("Visit [Boot.dev - Learn to Code!](https://boot.dev)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Visit ", TextType.TEXT),
            TextNode("Boot.dev - Learn to Code!", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected, new_nodes)


class TestTextToTextnodes(unittest.TestCase):
    def test_text_to_textnodes_full_example(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_plain_text(self):
        text = "This is just plain text with no markdown"
        nodes = text_to_textnodes(text)
        expected = [TextNode("This is just plain text with no markdown", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_bold(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_italic(self):
        text = "This is *italic* text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_code(self):
        text = "This is `code` text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_image(self):
        text = "This has ![image](url.png)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "url.png"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_only_link(self):
        text = "This has [link](https://example.com)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_mixed_formatting(self):
        text = "**Bold** and *italic* and `code`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_image_and_link(self):
        text = "![image](img.png) and [link](url.com)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("image", TextType.IMAGE, "img.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url.com"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_empty_string(self):
        text = ""
        nodes = text_to_textnodes(text)
        expected = [TextNode("", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_multiple_same_type(self):
        text = "**bold1** and **bold2** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold1", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("bold2", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_adjacent_formatting(self):
        text = "**bold***italic*`code`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode("italic", TextType.ITALIC),
            TextNode("code", TextType.CODE),
        ]
        self.assertListEqual(expected, nodes)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_single_block(self):
        md = "This is a single block of text with no double newlines"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a single block of text with no double newlines"])

    def test_markdown_to_blocks_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_only_whitespace(self):
        md = "   \n\n   \t\n\n   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_with_leading_trailing_whitespace(self):
        md = """

  This is a block with whitespace

  Another block

    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a block with whitespace", "Another block"])

    def test_markdown_to_blocks_multiple_consecutive_newlines(self):
        md = "Block 1\n\n\n\nBlock 2\n\n\n\n\nBlock 3"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block 1", "Block 2", "Block 3"])

    def test_markdown_to_blocks_heading_and_paragraph(self):
        md = """# This is a heading

This is a paragraph with some text."""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["# This is a heading", "This is a paragraph with some text."])

    def test_markdown_to_blocks_complex_markdown(self):
        md = """# Heading 1

This is a paragraph with **bold** text.

## Heading 2

- List item 1
- List item 2

> This is a blockquote

```python
def hello():
    print("Hello")
```

Final paragraph."""
        blocks = markdown_to_blocks(md)
        expected = [
            "# Heading 1",
            "This is a paragraph with **bold** text.",
            "## Heading 2",
            "- List item 1\n- List item 2",
            "> This is a blockquote",
            "```python\ndef hello():\n    print(\"Hello\")\n```",
            "Final paragraph."
        ]
        self.assertEqual(blocks, expected)

    def test_markdown_to_blocks_preserve_single_newlines(self):
        md = """Line 1
Line 2
Line 3

New block with
multiple lines"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Line 1\nLine 2\nLine 3", "New block with\nmultiple lines"])

    def test_markdown_to_blocks_mixed_whitespace(self):
        md = " \t Block 1 \t \n\n\t  Block 2  \n\n   Block 3   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Block 1", "Block 2", "Block 3"])


class TestBlockToBlockType(unittest.TestCase):
    def test_block_to_block_type_heading_h1(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_heading_h2(self):
        block = "## This is a level 2 heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_heading_h6(self):
        block = "###### This is a level 6 heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_heading_no_space(self):
        block = "#This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading_too_many_hashes(self):
        block = "####### This has too many hashes"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_code_block(self):
        block = """```
def hello():
    print("Hello, World!")
```"""
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_block_to_block_type_code_block_with_language(self):
        block = """```python
def hello():
    print("Hello, World!")
```"""
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_block_to_block_type_code_block_single_line(self):
        block = "```code```"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote_single_line(self):
        block = ">This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_quote_with_space(self):
        block = "> This is a quote with space"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_quote_multiline(self):
        block = """>This is the first line of a quote
>This is the second line
>This is the third line"""
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_quote_multiline_mixed(self):
        block = """>This is a quote
This is not a quote
>This is a quote again"""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list_single(self):
        block = "- This is a list item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_unordered_list_multiple(self):
        block = """- First item
- Second item
- Third item"""
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_unordered_list_no_space(self):
        block = "-No space after dash"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list_mixed(self):
        block = """- First item
Not a list item
- Third item"""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_single(self):
        block = "1. This is an ordered list item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_multiple(self):
        block = """1. First item
2. Second item
3. Third item"""
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_wrong_start(self):
        block = """2. This starts at 2
3. This is third"""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_skip_number(self):
        block = """1. First item
3. Third item"""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_no_space(self):
        block = "1.No space after period"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_mixed(self):
        block = """1. First item
Not a list item
2. Second item"""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_paragraph_simple(self):
        block = "This is just a regular paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_paragraph_multiline(self):
        block = """This is a paragraph
with multiple lines
that doesn't match any special pattern."""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_paragraph_with_formatting(self):
        block = "This paragraph has **bold** and *italic* text but is still a paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_empty_string(self):
        block = ""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading_with_text_after(self):
        block = "# Heading\nSome text after"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_block_to_block_type_quote_empty_lines(self):
        block = """>First line
>
>Third line"""
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_block_to_block_type_code_block_no_closing(self):
        block = """```
def hello():
    print("Hello")"""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        md = """
# This is a heading

## This is a subheading
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>This is a heading</h1><h2>This is a subheading</h2></div>",
        )

    def test_heading_with_inline_formatting(self):
        md = "# This is a **bold** heading"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>This is a <b>bold</b> heading</h1></div>",
        )

    def test_quote(self):
        md = """
>This is a quote
>with multiple lines
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote\nwith multiple lines</blockquote></div>",
        )

    def test_quote_with_formatting(self):
        md = ">This is a quote with **bold** text"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote with <b>bold</b> text</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- First item
- Second item
- Third item
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>First item</li><li>Second item</li><li>Third item</li></ul></div>",
        )

    def test_unordered_list_with_formatting(self):
        md = """
- First item with **bold**
- Second item with _italic_
- Third item with `code`
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>First item with <b>bold</b></li><li>Second item with <i>italic</i></li><li>Third item with <code>code</code></li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. First item
2. Second item
3. Third item
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>First item</li><li>Second item</li><li>Third item</li></ol></div>",
        )

    def test_ordered_list_with_formatting(self):
        md = """
1. First item with **bold**
2. Second item with _italic_
3. Third item with `code`
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>First item with <b>bold</b></li><li>Second item with <i>italic</i></li><li>Third item with <code>code</code></li></ol></div>",
        )

    def test_mixed_block_types(self):
        md = """
# Main Heading

This is a paragraph with **bold** text.

## Subheading

>This is a quote block

- List item 1
- List item 2

1. Ordered item 1
2. Ordered item 2

```
def hello():
    print("Hello, World!")
```

Final paragraph.
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        expected = "<div><h1>Main Heading</h1><p>This is a paragraph with <b>bold</b> text.</p><h2>Subheading</h2><blockquote>This is a quote block</blockquote><ul><li>List item 1</li><li>List item 2</li></ul><ol><li>Ordered item 1</li><li>Ordered item 2</li></ol><pre><code>def hello():\n    print(\"Hello, World!\")\n</code></pre><p>Final paragraph.</p></div>"
        self.assertEqual(html, expected)

    def test_empty_markdown(self):
        md = ""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div></div>")

    def test_single_paragraph(self):
        md = "This is a simple paragraph."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>This is a simple paragraph.</p></div>")

    def test_paragraph_with_links_and_images(self):
        md = "This paragraph has a [link](https://example.com) and an ![image](img.png)."
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This paragraph has a <a href=\"https://example.com\">link</a> and an <img src=\"img.png\" alt=\"image\"></img>.</p></div>",
        )

    def test_multiline_paragraph(self):
        md = """This is a paragraph
with multiple lines
that should be joined."""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is a paragraph with multiple lines that should be joined.</p></div>",
        )

    def test_all_heading_levels(self):
        md = """
# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><h2>Heading 2</h2><h3>Heading 3</h3><h4>Heading 4</h4><h5>Heading 5</h5><h6>Heading 6</h6></div>",
        )


class TestExtractTitle(unittest.TestCase):
    def test_extract_title_basic(self):
        markdown = "# Hello"
        title = extract_title(markdown)
        self.assertEqual(title, "Hello")

    def test_extract_title_with_whitespace(self):
        markdown = "#   Hello World   "
        title = extract_title(markdown)
        self.assertEqual(title, "Hello World")

    def test_extract_title_with_content_after(self):
        markdown = """# Main Title

This is some content after the title.

## Subtitle

More content here."""
        title = extract_title(markdown)
        self.assertEqual(title, "Main Title")

    def test_extract_title_no_h1_raises_exception(self):
        markdown = """## This is h2

This is just paragraph text.

### This is h3"""
        with self.assertRaises(Exception) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found")

    def test_extract_title_empty_h1(self):
        markdown = "# "
        title = extract_title(markdown)
        self.assertEqual(title, "")

    def test_extract_title_h1_with_formatting(self):
        markdown = "# **Bold** and _italic_ title"
        title = extract_title(markdown)
        self.assertEqual(title, "**Bold** and _italic_ title")

    def test_extract_title_multiple_h1_returns_first(self):
        markdown = """# First Title

Some content

# Second Title

More content"""
        title = extract_title(markdown)
        self.assertEqual(title, "First Title")

    def test_extract_title_h1_in_middle(self):
        markdown = """## Subtitle first

Some paragraph content.

# Main Title

More content here."""
        title = extract_title(markdown)
        self.assertEqual(title, "Main Title")

    def test_extract_title_only_h2_and_above(self):
        markdown = """## Heading 2

### Heading 3

#### Heading 4

Content without h1."""
        with self.assertRaises(Exception) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found")

    def test_extract_title_h1_without_space_is_not_valid(self):
        markdown = "#NotAValidHeading"
        with self.assertRaises(Exception) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found")


if __name__ == "__main__":
    unittest.main()