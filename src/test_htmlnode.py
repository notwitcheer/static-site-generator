import unittest

from htmlnode import HTMLNode


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


if __name__ == "__main__":
    unittest.main()