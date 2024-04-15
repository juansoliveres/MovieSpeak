from django.db import models
from ckeditor.fields import RichTextField
from sqltranslator.gen_ai.config import (
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_TOP_P,
    DEFAULT_FREQUENCY_PENALTY,
    DEFAULT_PRESENCE_PENALTY,
)
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from uuid import uuid4

def uuid4_gen():
    return "test_" + uuid4().hex[:10]


def uuid4_sql_gen():
    return "testSQL_" + uuid4().hex[:10]

# Create your models here.
class GPTBase(models.Model):
    temperature = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=DEFAULT_TEMPERATURE,
        help_text="Temperature",
    )
    max_output_tokens = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=DEFAULT_MAX_OUTPUT_TOKENS,
        help_text="Maximum number of output tokens",
    )
    top_p = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=DEFAULT_TOP_P,
        help_text="Top P",
    )
    frequency_penalty = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=DEFAULT_FREQUENCY_PENALTY,
        help_text="Frequency Penalty",
    )
    presence_penalty = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=DEFAULT_PRESENCE_PENALTY,
        help_text="Presence Penalty",
    )
    query = models.TextField(
        help_text="The query to ask in a natural lenguage. This field is required."
    )
    final_prompt = RichTextField(
        help_text="The final prompt which is passed to the LLM.", null=True, blank=True
    )
    prediction = RichTextField(
        help_text="The resulting prediction of the model.", null=True, blank=True
    )
    last_run = models.DateTimeField(
        help_text="The last time this model was executed.", null=True, blank=True
    )

    class Meta:
        abstract = True

class GPT3_5(GPTBase):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="A unique name to identify this query.",
        default=uuid4_sql_gen,
    )
    query_result = RichTextField(
        help_text="The result of the query over the table", null=True, blank=True
    )
    query_is_valid = models.BooleanField(
        null=True,
        blank=True,
        help_text="If the predicted query has been successfully executed.",
    )

    class Meta:
        verbose_name_plural = "GPT3_5"
        app_label = 'sqltranslator'

class GPT_4(GPTBase):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="A unique name to identify this query.",
        default=uuid4_sql_gen,
    )
    query_result = RichTextField(
        help_text="The result of the query over the table", null=True, blank=True
    )
    query_is_valid = models.BooleanField(
        null=True,
        blank=True,
        help_text="If the predicted query has been successfully executed.",
    )

    class Meta:
        verbose_name_plural = "GPT_4"
        app_label = 'sqltranslator'