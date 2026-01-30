import unittest

from htmlnode import HTMLNode, LeafNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_with_props(self):
        node = HTMLNode("a", "Click me", None, {"href": "https://www.google.com", "target": "_blank"})
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_empty_props(self):
        node = HTMLNode("p", "Hello world", None, {})
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_none_props(self):
        node = HTMLNode("p", "Hello world", None, None)
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_single_prop(self):
        node = HTMLNode("img", None, None, {"src": "image.jpg"})
        expected = ' src="image.jpg"'
        self.assertEqual(node.props_to_html(), expected)

    def test_to_html_not_implemented(self):
        node = HTMLNode("p", "Hello world")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_repr_all_params(self):
        children = [HTMLNode("span", "child")]
        node = HTMLNode("div", "Hello", children, {"class": "container"})
        expected = "HTMLNode(div, Hello, children: [HTMLNode(span, child, children: None, None)], {'class': 'container'})"
        self.assertEqual(repr(node), expected)

    def test_repr_minimal(self):
        node = HTMLNode()
        expected = "HTMLNode(None, None, children: None, None)"
        self.assertEqual(repr(node), expected)


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Just plain text")
        self.assertEqual(node.to_html(), "Just plain text")

    def test_leaf_to_html_no_value_raises_error(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_leaf_to_html_b_tag(self):
        node = LeafNode("b", "Bold text")
        self.assertEqual(node.to_html(), "<b>Bold text</b>")

    def test_leaf_to_html_img_with_props(self):
        node = LeafNode("img", "", {"src": "image.jpg", "alt": "An image"})
        self.assertEqual(node.to_html(), '<img src="image.jpg" alt="An image"></img>')

    def test_leaf_repr(self):
        node = LeafNode("p", "Hello", {"class": "text"})
        expected = "LeafNode(p, Hello, {'class': 'text'})"
        self.assertEqual(repr(node), expected)

    def test_leaf_repr_no_props(self):
        node = LeafNode("span", "Text")
        expected = "LeafNode(span, Text, None)"
        self.assertEqual(repr(node), expected)


if __name__ == "__main__":
    unittest.main()