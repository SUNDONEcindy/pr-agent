
# Generated by CodiumAI
import pytest

from pr_agent.algo.utils import try_fix_yaml


class TestTryFixYaml:

    # The function successfully parses a valid YAML string.
    def test_valid_yaml(self):
        review_text = "key: value\n"
        expected_output = {"key": "value"}
        assert try_fix_yaml(review_text) == expected_output

    # The function adds '|-' to 'relevant line:' if it is not already present and successfully parses the YAML string.
    def test_add_relevant_line(self):
        review_text = "relevant line: value: 3\n"
        expected_output = {'relevant line': 'value: 3\n'}
        assert try_fix_yaml(review_text) == expected_output

    # The function extracts YAML snippet
    def test_extract_snippet(self):
        review_text = '''\
Here is the answer in YAML format:

```yaml
name: John Smith
age: 35
```
'''
        expected_output = {'name': 'John Smith', 'age': 35}
        assert try_fix_yaml(review_text) == expected_output


    # The YAML string is empty.
    def test_empty_yaml_fixed(self):
        review_text = ""
        assert try_fix_yaml(review_text) is None


    # The function extracts YAML snippet
    def test_no_initial_yaml(self):
        review_text = '''\
I suggest the following:

code_suggestions:
- relevant_file: |
    src/index.ts
  label: |
    best practice

- relevant_file: |
    src/index2.ts
  label: |
    enhancement
```

We can further improve the code by using the `const` keyword instead of `var` in the `src/index.ts` file.
'''
        expected_output = {'code_suggestions': [{'relevant_file': 'src/index.ts\n', 'label': 'best practice\n'}, {'relevant_file': 'src/index2.ts\n', 'label': 'enhancement'}]}

        assert try_fix_yaml(review_text, first_key='code_suggestions', last_key='label') == expected_output

    def test_with_initial_yaml(self):
        review_text = '''\
I suggest the following:

```
code_suggestions:
- relevant_file: |
    src/index.ts
  label: |
    best practice

- relevant_file: |
    src/index2.ts
  label: |
    enhancement
```

We can further improve the code by using the `const` keyword instead of `var` in the `src/index.ts` file.
'''
        expected_output = {'code_suggestions': [{'relevant_file': 'src/index.ts\n', 'label': 'best practice\n'}, {'relevant_file': 'src/index2.ts\n', 'label': 'enhancement'}]}
        assert try_fix_yaml(review_text, first_key='code_suggestions', last_key='label') == expected_output


    def test_with_brackets_yaml_content(self):
        review_text = '''\
{
code_suggestions:
- relevant_file: |
    src/index.ts
  label: |
    best practice

- relevant_file: |
    src/index2.ts
  label: |
    enhancement
}
'''
        expected_output = {'code_suggestions': [{'relevant_file': 'src/index.ts\n', 'label': 'best practice\n'}, {'relevant_file': 'src/index2.ts\n', 'label': 'enhancement'}]}
        assert try_fix_yaml(review_text, first_key='code_suggestions', last_key='label') == expected_output

    def test_tab_indent_yaml(self):
        review_text = '''\
code_suggestions:
- relevant_file: |
    src/index.ts
  label: |
\tbest practice

- relevant_file: |
    src/index2.ts
  label: |
    enhancement
'''
        expected_output = {'code_suggestions': [{'relevant_file': 'src/index.ts\n', 'label': 'best practice\n'}, {'relevant_file': 'src/index2.ts\n', 'label': 'enhancement\n'}]}
        assert try_fix_yaml(review_text, first_key='code_suggestions', last_key='label') == expected_output


    def test_leading_plus_mark_code(self):
        review_text = '''\
code_suggestions:
- relevant_file: |
    src/index.ts
  label: |
    best practice
  existing_code: |
+   var router = createBrowserRouter([
  improved_code: |
+   const router = createBrowserRouter([
'''
        expected_output = {'code_suggestions': [{
            'relevant_file': 'src/index.ts\n',
            'label': 'best practice\n',
            'existing_code': 'var router = createBrowserRouter([\n',
            'improved_code': 'const router = createBrowserRouter([\n'
        }]}
        assert try_fix_yaml(review_text, first_key='code_suggestions', last_key='improved_code') == expected_output


    def test_inconsistent_indentation_in_block_scalar_yaml(self):
        """
            This test case represents a situation where the AI outputs the opening '{' with 5 spaces
            (resulting in an inferred indent level of 5), while the closing '}' is output with only 4 spaces.
            This inconsistency makes it impossible for the YAML parser to automatically determine the correct
            indent level, causing a parsing failure.

            The root cause may be the LLM miscounting spaces or misunderstanding the active block scalar context
            while generating YAML output.
        """

        review_text = '''\
code_suggestions:
- relevant_file: |
    tsconfig.json
  existing_code: |
     {
        "key1": "value1",
        "key2": {
          "subkey": "value"
         }
    }
'''
        expected_json = '''\
 {
    "key1": "value1",
    "key2": {
      "subkey": "value"
     }
}
'''
        expected_output = {
            'code_suggestions': [{
                'relevant_file': 'tsconfig.json\n',
                'existing_code': expected_json
            }]
        }
        assert try_fix_yaml(review_text, first_key='code_suggestions', last_key='existing_code') == expected_output


    def test_inconsistent_and_insufficient_indentation_in_block_scalar_yaml(self):
        """
            This test case reproduces a YAML parsing failure where the block scalar content
            generated by the AI includes inconsistent and insufficient indentation levels.

            The root cause may be the LLM miscounting spaces or misunderstanding the active block scalar context
            while generating YAML output.
        """

        review_text = '''\
code_suggestions:
- relevant_file: |
    tsconfig.json
  existing_code: |
    {
      "key1": "value1",
      "key2": {
        "subkey": "value"
      }
  }
'''
        expected_json = '''\
{
  "key1": "value1",
  "key2": {
    "subkey": "value"
  }
}
'''
        expected_output = {
            'code_suggestions': [{
                'relevant_file': 'tsconfig.json\n',
                'existing_code': expected_json
            }]
        }
        assert try_fix_yaml(review_text, first_key='code_suggestions', last_key='existing_code') == expected_output


    def test_wrong_indentation_code_block_scalar(self):
        review_text = '''\
code_suggestions:
- relevant_file: |
    a.c
  existing_code: |
  int sum(int a, int b) {
    return a + b;
  }

  int sub(int a, int b) {
    return a - b;
  }
'''
        expected_code_block = '''\
int sum(int a, int b) {
  return a + b;
}

int sub(int a, int b) {
  return a - b;
}
'''
        expected_output = {
            "code_suggestions": [
                {
                    "relevant_file": "a.c\n",
                    "existing_code": expected_code_block
                }
            ]
        }
        assert try_fix_yaml(review_text, first_key='code_suggestions', last_key='existing_code') == expected_output
