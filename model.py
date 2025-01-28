from langfuse.decorators import observe
from langfuse.openai import openai

client = openai.OpenAI()

config = {
#    'model': 'claude-3.5-sonnet-latest'
    'model': 'gpt-4o-mini',
    'system': 'You are a helpful assistant'
}

class Conversation(object):
    def __init__(self, model=None, system=None):
        self.model = config['model'] if model is None else model
        self.system = config['system'] if system is None else system
        self.messages = [{ 'role': 'system', 'content': self.system }]

    def add_message(self, role, content):
        self.messages.append({'role': role, 'content': content})
        return self

    def add_user_message(self, content):
        self.add_message('user', content)
        return self

    def add_assistant_message(self, content):
        self.add_message('assistant', content)
        return self

    @observe()
    def gen(self, user_msg=None):
        " Basic LLM call "
        if user_msg:
            self.add_user_message(user_msg)
        completion = client.chat.completions.create(model = self.model, messages = self.messages)
        output = completion.choices[0].message
        self.add_assistant_message(output.content)

        return output.content

    @observe()
    def gen_structured(self, format, user_msg=None):
        """ LLM call with structured output parsing """
        if user_msg:
            self.add_user_message(user_msg)
        completion = client.beta.chat.completions.parse(
            model = self.model,
            messages = self.messages,
            response_format=format
        )
        output = completion.choices[0].message
        self.add_assistant_message(output)
        return output.parsed