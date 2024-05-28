class CategoryGenerator:
    '''
        
    '''
    def __init__(self, prompt_path, category):
        self.cat_name = category
        self.prompt = ""
        with open(prompt_path) as f:
            self.prompt = f.read()

    def generate_question_prompt(self, num_questions) -> str:
        return self.prompt.format(num_questions = num_questions, category = self.cat_name)
