from io import StringIO
from unittest import TestCase
from json2code.cdm_generator import CDMGenerator
from json2code.code_generator import CodeGenerator

__author__ = 'jzaczek'


class EndToEndTests(TestCase):

    def test_generate_with_predictions(self):
        cdm_generator = CDMGenerator("json_examples", "json_configs", predict_references=True)
        code_generator = CodeGenerator("json_examples/config", persist_output=True)
        code_generator.generate()
        output = code_generator.output

        with file("json2code_tests/test_output.swift") as test_output:
            t_output = test_output.read()
            self.assertEqual(output, t_output)