from strands import tool


@tool
def valyu_search(prompt: str, results: int = 5):
    """Use Valyu to search for results that answer a prompt.

    Args:
        prompt (str): the prompt to search for
        results (int, optional): The number of results. Defaults to 5.
    """
    # \does something