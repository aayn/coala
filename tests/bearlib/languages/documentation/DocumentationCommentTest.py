import unittest

from coalib.bearlib.languages.documentation.DocumentationComment import (
    DocumentationComment)


class DocumentationCommentTest(unittest.TestCase):

    def test_fields(self):
        uut = DocumentationComment("my doc",
                                   ("/**", "*", "*/"),
                                   (25, 45))

        self.assertEqual(uut.documentation, "my doc")
        # self.assertEqual(str(uut), "my doc")
        self.assertEqual(uut.markers, ("/**", "*", "*/"))
        self.assertEqual(uut.textrange, (25, 45))

        uut = DocumentationComment("qwertzuiop",
                                   ("##", "#", "#"),
                                   None)

        self.assertEqual(uut.documentation, "qwertzuiop")
        # self.assertEqual(str(uut), "qwertzuiop")
        self.assertEqual(uut.markers, ("##", "#", "#"))
        self.assertEqual(uut.textrange, None)


class DocumentationCommentParserTest(unittest.TestCase):

    def test_from_docstring(self):
        self.check_from_docstring_dataset("")
        self.check_from_docstring_dataset(" description only ",
                                          desc="description only")
        self.check_from_docstring_dataset(" :param test:  test description ",
                                          param_dict={
                                              "test": "test description"})
        self.check_from_docstring_dataset(" @param test:  test description ",
                                          param_dict={
                                              "test": "test description"})
        self.check_from_docstring_dataset(" :return: something ",
                                          retval_desc="something")
        self.check_from_docstring_dataset(" @return: something ",
                                          retval_desc="something")
        self.check_from_docstring_dataset("""
        Main description

        @param p1: this is

        a multiline desc for p1

        :param p2: p2 description

        @return: retval description
        :return: retval description
        override
        """, desc="Main description", param_dict={
            "p1": "this is\na multiline desc for p1\n",
            "p2": "p2 description\n"
        }, retval_desc="retval description override")

    # def test_str(self):
    #     uut = DocumentationComment.from_docstring(
    #         '''
    #         Description of something. No params.
    #         ''')

    #     self.assertEqual(str(uut), "Description of something. No params.")

    #     uut = DocumentationComment.from_docstring(
    #         '''
    #         Description of something with params.

    #         :param x: Imagine something.
    #         :param y: x^2
    #         ''')

    #     self.assertEqual(uut, "Description of something with params.")

    def check_from_docstring_dataset(self,
                                     docstring,
                                     desc="",
                                     param_dict=None,
                                     retval_desc=""):
        param_dict = param_dict or {}

        self.assertIsInstance(docstring,
                              str,
                              "docstring needs to be a string for this test.")
        doc_comment = DocumentationComment.from_docstring(docstring)
        self.assertEqual(doc_comment.description, desc)
        self.assertEqual(doc_comment.params, param_dict)

        self.assertEqual(doc_comment.retval, retval_desc)
