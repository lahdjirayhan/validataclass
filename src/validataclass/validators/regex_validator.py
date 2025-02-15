"""
validataclass
Copyright (c) 2021, binary butterfly GmbH and contributors
Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.
"""

import re
from typing import Any, Optional, Union, Type

from validataclass.exceptions import RegexMatchError, ValidationError
from .string_validator import StringValidator

__all__ = [
    'RegexValidator',
]


class RegexValidator(StringValidator):
    """
    Validator that matches strings against a regular expression, optionally with minimal/maximal length requirements.

    This validator is based on the `StringValidator` which first handles type checking and optional length requirements.
    The input string is then matched against the regex using `re.fullmatch()` from the Python standard library, which
    means that the *full* string must match the regex.

    The regex can be specified either as a precompiled pattern (see `re.compile()`) or as a string which will be
    compiled by the class. Regex flags (e.g. `re.IGNORECASE` for case-insensitive matching) can only be set by
    precompiling a pattern with those flags.

    For further information on regular expressions, see: https://docs.python.org/3/library/re.html

    If the input string does not match the regex, a `RegexMatchError` validation error with the default error code
    'invalid_string_format' is raised. To get more explicit error messages, you can specify a custom validation error
    using the parameters `custom_error_class` (which must be a subclass of `ValidationError`) and/or `custom_error_code`
    (which is a string that overrides the default error code).

    By default only "safe" singleline strings are allowed (i.e. no non-printable characters). See the `StringValidator`
    options `unsafe` and `multiline` for more details.

    Examples:

    ```
    # Import Python standard library for regular expressions
    import re

    # Use a precompiled regular expression to match lower-case hexadecimal numbers (e.g. '0', '123abc', '00ff00')
    RegexValidator(re.compile(r'[0-9a-f]+'))

    # Same as above, but with the re.IGNORECASE flag for case-insensitive matching (e.g. '123abc', '123ABC')
    RegexValidator(re.compile(r'[0-9a-f]+', re.IGNORECASE))

    # Same as above, but using a raw string instead of a precompiled pattern (explicitly allowing uppercase letters in character class)
    RegexValidator(r'[0-9a-fA-F]+')

    # As above, but setting string length requirements to only allow 6-digit hex numbers (e.g. '123abc')
    RegexValidator(re.compile(r'[0-9a-f]+', re.IGNORECASE), min_length=6, max_length=6)

    # Set a custom error code (will raise RegexMatchError with error code 'invalid_hex_number' on error)
    RegexValidator(re.compile(r'[0-9a-f]+'), custom_error_code='invalid_hex_number')

    # Set a custom error class (will raise this exception with its default error code on error)
    class InvalidHexNumberError(RegexMatchError):
        code = 'invalid_hex_number'

    RegexValidator(re.compile(r'[0-9a-f]+'), custom_error_class=InvalidHexNumberError)
    ```

    Valid input: Any `str` that matches the regex
    Output: `str` (unmodified input if valid)
    """

    # Precompiled regex pattern
    regex_pattern: re.Pattern

    # Exception class to use when regex matching fails
    custom_error_class: Type[ValidationError]

    # Custom error code to use in the regex match exception (use default if None)
    custom_error_code: Optional[str]

    def __init__(
        self,
        pattern: Union[re.Pattern, str],
        *,
        custom_error_class: Type[ValidationError] = RegexMatchError,
        custom_error_code: Optional[str] = None,
        **kwargs,
    ):
        """
        Create a RegexValidator with a specified regex pattern (as string or precompiled `re.Pattern` object).

        Optionally with a custom error class (subclass of ValidationError) and custom error code. Other keyword
        arguments (e.g. 'min_length', 'max_length', 'multiline' and 'unsafe') will be passed to `StringValidator`.

        Parameters:
            pattern: `re.Pattern` or `str`, regex pattern to use for validation (required)
            custom_error_class: Subclass of `ValidationError` raised when regex matching fails (default: RegexMatchError)
            custom_error_code: Optional `str`, overrides the default error code in the regex match exception (default: None)
        """
        # Initialize base StringValidator (may set min_length/max_length via kwargs)
        super().__init__(**kwargs)

        # Check parameter validity
        if not issubclass(custom_error_class, ValidationError):
            raise TypeError('Custom error class must be a subclass of ValidationError.')

        # Save regex pattern (precompile if necessary)
        if isinstance(pattern, re.Pattern):
            self.regex_pattern = pattern
        else:
            self.regex_pattern = re.compile(pattern)

        # Save custom error class and code
        self.custom_error_class = custom_error_class
        self.custom_error_code = custom_error_code

    def validate(self, input_data: Any) -> str:
        """
        Validate input as string and match full string against regular expression. Returns unmodified string.
        """
        # Validate input with base StringValidator (checks length requirements)
        input_data = super().validate(input_data)

        # Match full string against Regex pattern
        if not self.regex_pattern.fullmatch(input_data):
            raise self.custom_error_class(code=self.custom_error_code)

        return input_data
