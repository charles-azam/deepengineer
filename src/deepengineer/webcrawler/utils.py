import re
import unicodedata

def sanitize_filename(filename, replacement_char="_", max_length=255):
    """
    Sanitizes a string to be suitable for use as a filename.

    This function performs the following steps:
    1. Replaces spaces with the specified replacement_char.
    2. Converts the string to Unicode Normalization Form KD (NFKD) to separate
       base characters from their diacritical marks (e.g., 'é' becomes 'e').
    3. Encodes to ASCII and decodes back to remove non-ASCII characters.
    4. Removes any characters that are not alphanumeric, hyphens, underscores,
       or periods, replacing them with the replacement_char.
    5. Replaces multiple consecutive replacement_char characters with a single one.
    6. Trims leading/trailing replacement_char characters.
    7. Ensures the filename doesn't start with a period (which makes it hidden on some systems).
    8. Truncates the filename to the specified max_length (important for OS compatibility).

    Args:
        filename (str): The original string to sanitize.
        replacement_char (str, optional): The character to replace invalid characters with.
                                          Defaults to "_".
        max_length (int, optional): The maximum allowed length for the filename.
                                    Defaults to 255, a common OS limit.

    Returns:
        str: The sanitized filename.
    """

    # 1. Replace spaces with the replacement_char
    # This is done early to ensure spaces are handled before other replacements
    # to avoid issues with double replacement characters in subsequent steps.
    cleaned_filename = filename.replace(' ', replacement_char)

    # 2. Convert to NFKD and encode to ASCII to handle accented characters
    # This transforms 'crème brûlée' into 'creme brulee'
    cleaned_filename = unicodedata.normalize('NFKD', cleaned_filename).encode('ascii', 'ignore').decode('utf-8')

    # 3. Remove characters that are not alphanumeric, hyphen, underscore, or period.
    #    Replace them with the specified replacement_char.
    #    The regex pattern `[^a-zA-Z0-9\-_.]` matches any character that is NOT
    #    (a-z, A-Z, 0-9, hyphen, underscore, or period).
    cleaned_filename = re.sub(r'[^a-zA-Z0-9\-_.]', replacement_char, cleaned_filename)

    # 4. Replace multiple consecutive replacement_char characters with a single one
    cleaned_filename = re.sub(re.escape(replacement_char) + r'+', replacement_char, cleaned_filename)

    # 5. Trim leading/trailing replacement_char characters
    cleaned_filename = cleaned_filename.strip(replacement_char)

    # 6. Ensure the filename doesn't start with a period (hidden file on some systems)
    if cleaned_filename.startswith('.'):
        cleaned_filename = replacement_char + cleaned_filename[1:]

    # 7. Truncate to max_length
    # This is important for cross-platform compatibility (e.g., Windows limits are around 255)
    if len(cleaned_filename) > max_length:
        # Try to keep the file extension if present
        name, ext = "", ""
        if '.' in cleaned_filename:
            parts = cleaned_filename.rsplit('.', 1)
            name, ext = parts[0], "." + parts[1]

        if len(name) > max_length - len(ext):
            cleaned_filename = name[:max_length - len(ext)] + ext
        else:
            cleaned_filename = cleaned_filename[:max_length]

    # Handle empty string case after all operations
    if not cleaned_filename:
        return "untitled" + replacement_char + "file"

    return cleaned_filename
