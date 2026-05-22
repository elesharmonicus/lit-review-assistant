from src.analysis import clean_and_tokenize

def test_removes_stopwords():
    result = clean_and_tokenize("the cell is using a method")
    assert "the" not in result
    assert "using" not in result  # domain stopword

def test_lemmatizes():
    result = clean_and_tokenize("images cells proteins")
    assert "image" in result
    assert "cell" in result
    assert "protein" in result

def test_filters_short_tokens():
    result = clean_and_tokenize("an of to cell")
    assert "an" not in result
    assert "cell" in result