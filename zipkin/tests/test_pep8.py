from unittest2.case import TestCase
import pep8
import os

__all__ = ['TestCodeFormat']


class TestCodeFormat(TestCase):

    def test_pep8_conformance(self):
        style = pep8.StyleGuide(exclude=['_thrift'], max_line_length=140)
        result = style.check_files(['zipkin'])
        self.assertEqual(result.total_errors, 0, "Found style errors")
