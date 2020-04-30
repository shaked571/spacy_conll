import spacy
from spacy.language import Language
from spacy.tokens import Doc

from . import ConllFormatter


def init_parser(parser: str = 'spacy',
                model_or_lang: str = 'en',
                is_tokenized: bool = False,
                disable_sbd: bool = False,
                include_headers: bool = False,
                **kwargs) -> Language:
    """Initialise a spacy-wrapped parser given a language or model and some options.

    :param parser: which parser to use. Parsers other than 'spacy' need to be installed separately. Valid options are
    'spacy', 'stanfordnlp', 'stanza', 'udpipe'. Note that the spacy-* wrappers of those libraries need to be
    installed, e.g. spacy-stanza. Defaults to 'spacy'
    :param model_or_lang: language model to use (must be installed). Defaults to an English model
    :param is_tokenized: indicates whether your text has already been tokenized (space-seperated;
        does not work for udpipe)
    :param disable_sbd: disables spaCy automatic sentence boundary detection (only works for spaCy)
    :param include_headers: to include headers before the output of every sentence
    :param kwargs: will be passed to the core pipeline. For spacy and udpipe, it will be passed to their
        `.load()` initialisations, for stanfordnlp and stanza kwargs is passed to to their `.Pipeline()`
         initialisations
    :return: an initialised Language object; the parser
    """
    if parser == 'spacy':
        nlp = spacy.load(model_or_lang, **kwargs)
        if is_tokenized:
            nlp.tokenizer = nlp.tokenizer.tokens_from_list
        if disable_sbd:
            nlp.add_pipe(_prevent_sbd, name='prevent-sbd', before='parser')
    elif parser == 'stanfordnlp':
        from spacy_stanfordnlp import StanfordNLPLanguage
        import stanfordnlp

        snlp = stanfordnlp.Pipeline(lang=model_or_lang, tokenize_pretokenized=is_tokenized, **kwargs)
        nlp = StanfordNLPLanguage(snlp)
    elif parser == 'stanza':
        import stanza
        from spacy_stanza import StanzaLanguage

        snlp = stanza.Pipeline(lang=model_or_lang, tokenize_pretokenized=is_tokenized, **kwargs)
        nlp = StanzaLanguage(snlp)
    elif parser == 'udpipe':
        import spacy_udpipe

        nlp = spacy_udpipe.load(model_or_lang, **kwargs)
    else:
        raise ValueError("Unexpected value for 'parser'. Options are: 'spacy', 'stanfordnlp', 'stanza', 'udpipe'")

    conllformatter = ConllFormatter(nlp, include_headers=include_headers)
    nlp.add_pipe(conllformatter, last=True)

    return nlp


def _prevent_sbd(doc: Doc):
    """Disables spaCy's sentence boundary detection."""
    for token in doc:
        token.is_sent_start = False
    return doc
