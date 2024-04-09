import openai
from typing import Dict, List, Literal, Optional, Tuple, Union
from sqltranslator.gen_ai.config import GPT3_5
from sqltranslator.gen_ai.config import OPENAI_API_KEY
from sqltranslator.gen_ai.prompt.prompt import prompt_sql_generator

from sqltranslator.gen_ai.config import (
    DEFAULT_EXAMPLES_SEPARATOR,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
)

class TextGeneratorGPT3_5:
    """
    A class for generating text using GPT-3.5 language model.

    The `TextGeneratorGPT3_5` class provides a method called `predict` for generating text based
    on a given input prompt.
    That method uses a set of parameters to control the level of randomness
    and conservatism in the generated text, such as `temperature`, `max_tokens`, and `top_p`.

    The class utilizes the GPT-3 language model from the OpenAI library to generate the text.
    If no API key is specified during initialization, you'll need to set the `OPENAI_API_KEY`
    environment variable with your API key.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        if api_key is None:
            raise ValueError("API key not provided. Set OPENAI_API_KEY environment variable.")
        self.client = openai.OpenAI(api_key=api_key)

    def predict_sql(
        self,
        text: str,
        text_examples: str,
        trakt_username: str,
        max_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
        extract_sql: bool = False,
        input_sep: str = DEFAULT_EXAMPLES_SEPARATOR,
    ) -> Tuple[str, str]:
        """
        This function predicts an SQL query given an optional text or file examples.

        - `text` argument is a string which contains a natural language query.
        - `max_tokens` argument is an integer specifying the maximum number
        of tokens to generate. The default value is `DEFAULT_MAX_OUTPUT_TOKENS`.
        - `temperature` argument is a float specifying the randomness of the
        generated text. The default value is `DEFAULT_TEMPERATURE`.
        - `top_p` argument is a float specifying the probability of the top-p
        tokens to consider when generating text. The default value is `DEFAULT_TOP_P`.
        - `text_examples` argument is an optional list of `TableExample` instances
        containing examples of text tables related to the given SQL query.
        - `file_examples` argument is an optional list of dictionaries
        containing examples of table files related to the given SQL query.
        - `input_sep` argument is a string specifying the separator to be used
        when generating the prompt from the given examples.
        The default value is `DEFAULT_EXAMPLES_SEPARATOR`.

        The function returns a tuple containing the generated text and the
        prompt used to generate it.
        """
        prompt = prompt_sql_generator(
            question=text,
            text_examples=text_examples,
            input_sep=input_sep,
            trakt_username = trakt_username,
        )
        print(prompt)

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
        )
        print(response)

        response_text = response.choices[0].message.content

        if extract_sql:
            sql_extracted = extract_sql_query_from_text(
                text=response_text, raise_=False
            )
            return sql_extracted, prompt
        
        return response_text, prompt