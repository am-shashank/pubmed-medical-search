def cleanTokens(tokens):
    if not type(tokens) is list:
        raise ValueError("tokens must be a list")
    from clean_methods import removePunctuation
    from clean_methods import toLowercase
    cleaned = removePunctuation(tokens)
    cleaned = toLowercase(cleaned)
    return cleaned
