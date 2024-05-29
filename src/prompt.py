'''
    Note: only the class PromptGenerator is needed, the other classes are only used to segment the comments of different prompt types.

'''

class PromptGenerator(object):
    """
        Super class for prompt generation
    """
    def __init__(self, prompt_path):
        super(PromptGenerator, self).__init__()
        with open(prompt_path) as f:
            self.prompt = f.read()

    def generate_prompt(self, **kwargs):
        return self.prompt.format(**kwargs)

class CluePromptGenerator(PromptGenerator):
    '''
        Basic prompt generation for clues

        Question: <q>
        Answer: <ans>
    '''
    def __init__(self, prompt_path, category):
        super(CluePromptGenerator, self).__init__(prompt_path)
        self.cat_name = category

class CategoryPromptGenerator(PromptGenerator):
    """
        Prompt generates trivia categories in the form:

        <singular>, <plural>, <title>

        Needs num = <number of categories to generate>
    """
    def __init__(self, prompt_path = './prompts/categories.txt'): 
        super(CategoryPromptGenerator, self).__init__(prompt_path)

class AnswerPromptGenerator(PromptGenerator):
    """
        Prompt generates answers based on the categories.

        Answer: <Your answer>

        Needs:
            num = <number of categories to generate>
            singular = <specific instance of the category>
            plural = <plural descriptor for the category>
    """
    def __init__(self, prompt_path = './prompts/answer_prompt.txt'):
        super(AnswerPromptGenerator, self).__init__(prompt_path)
        self.prompt_path = prompt_path
        
