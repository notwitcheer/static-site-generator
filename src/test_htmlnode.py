import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


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


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        expected = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(node.to_html(), expected)

    def test_to_html_no_tag_raises_error(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode(None, [child_node])
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertEqual(str(context.exception), "All parent nodes must have a tag")

    def test_to_html_no_children_raises_error(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertEqual(str(context.exception), "All parent nodes must have children")

    def test_to_html_empty_children_list(self):
        parent_node = ParentNode("div", [])
        self.assertEqual(parent_node.to_html(), "<div></div>")

    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container", "id": "main"})
        expected = '<div class="container" id="main"><span>child</span></div>'
        self.assertEqual(parent_node.to_html(), expected)

    def test_to_html_nested_mixed_nodes(self):
        nested_parent = ParentNode("ul", [
            LeafNode("li", "Item 1"),
            LeafNode("li", "Item 2"),
        ])
        root_node = ParentNode("div", [
            LeafNode("h1", "Title"),
            nested_parent,
            LeafNode("p", "Footer text"),
        ])
        expected = "<div><h1>Title</h1><ul><li>Item 1</li><li>Item 2</li></ul><p>Footer text</p></div>"
        self.assertEqual(root_node.to_html(), expected)

    def test_to_html_deeply_nested(self):
        deep_child = LeafNode("strong", "very nested")
        level3 = ParentNode("em", [deep_child])
        level2 = ParentNode("span", [level3])
        level1 = ParentNode("div", [level2])
        expected = "<div><span><em><strong>very nested</strong></em></span></div>"
        self.assertEqual(level1.to_html(), expected)

    def test_repr_with_children(self):
        child = LeafNode("span", "child")
        parent = ParentNode("div", [child], {"class": "container"})
        expected = "ParentNode(div, children: [LeafNode(span, child, None)], {'class': 'container'})"
        self.assertEqual(repr(parent), expected)

    def test_repr_no_props(self):
        child = LeafNode("span", "child")
        parent = ParentNode("div", [child])
        expected = "ParentNode(div, children: [LeafNode(span, child, None)], None)"
        self.assertEqual(repr(parent), expected)


if __name__ == "__main__":
    unittest.main()