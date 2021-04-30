# eznlp

Easy access to text summarization, sentiment analysis, subject classification, semantic search, and question answering. Includes a get_text method that extracts raw text from any URL or file (.pdf, .docx, .html, etc.).

These capabilities are built using the excellent machine learning library [ktrain](https://github.com/amaiya/ktrain) which provides clean interfaces to a number of pretrained models (BERT, NBSVM, fastText, LDA, [etc.](https://github.com/amaiya/ktrain#overview)). Text extraction is performed via [textract](https://textract.readthedocs.io/en/stable/).

# Installation

`pip install git+https://github.com/dpinney/eznlp`

Please note that this module requires multiple large machine learning libraries and pre-trained models. Full installation size is multiple gigabytes.

# Usage Examples

```python
>>> import eznlp

>>> # get the text of a test document
>>> demo_doc = eznlp.get_text('https://drive.google.com/uc?export=download&id=13dd5nWDvdzrSf01d8g-tZzhh32ewZ-Rc', is_url=True)
>>> demo_doc
'Guilty pleas, victim impact statements could have slew of implications for PG&E...'

>>> # summarizing the document
>>> eznlp.summarize(demo_doc)
"Judge imposes roughly $3.5 million fine on Pacific Gas & Electric. PG&E has pleaded guilty"
"to 84 counts of involuntary manslaughter caused by the Camp Fire. Victim impact statements"
"criticized PG&e's maintenance of its power system. The guilty pleas could have a slew of "
"implications for the company and state, stakeholders say."

>>> # sentiment analyis: is this a positive or negative article?
>>> eznlp.sentiment(demo_doc)
[('negative', 0.6047303676605225), ('positive', 0.09912186115980148)]

>>> # test whether the document is about the given subjects
>>> eznlp.subjects(demo_doc, ['wildfires','energy','bacon','pge'])
[('wildfires', 0.9944069385528564), ('energy', 0.8900003433227539),
  ('bacon', 0.012442146427929401), ('pge', 0.9794674515724182)]

>>> # extract the named entities in the document, along with their type
>>> eznlp.named_entities(demo_doc)
{('Butte County', 'MISC'), ('Palermo', 'ORG'), ('PG & E Corp', 'ORG'), ...}

>>> # gather a folder full of documents and make a semantic search index
>>> eznlp._get_sample_data()
>>> qae = eznlp.search_make_index('en_docs', 'en_docs_index')

>>> # semantic answering via the indexed documents
>>> search(qae, 'Energy storage deployment?')
[{'answer': 'global energy storage deployment to increase 122x over the next two decades',
  'confidence': 0.3261045284748744,
  'context': '...',
  'reference': '134'},
 {'answer': 'the revisions to the iso market rule will become effective april 1, and will allow storage to be dispatched into real time energy markets',
  'confidence': 0.30367338538738653,
  'context': '...',
  'reference': '131'},
 {'answer': 'the los angeles department of water and power (ladwp) is preparing a potentially world record setting power purchase agreement (ppa) for solar + storage',
  'confidence': 0.011269367223707761,
  'context': '...',
  'reference': '202'}]

```

# Future Work

* Improved CI testing.
* Better requirement version control.
* Raw text synthesis. Tried huggingface gpt2 and xlnet, both have mediocre results. will have to rely on separate [gpt3 library](https://news.ycombinator.com/item?id=25819803) for this.
* Semantic answering via google. Google has a very good question answering model trained on the entire internet. However, API access to Google is very tricky. There are some experiments in the code using [serpapi](https://stackoverflow.com/questions/54162249/is-there-a-google-api-for-people-also-ask), which is expensive at $50/month, the [Google Custom Search api](https://stackoverflow.com/a/49122258/7447778), which is free but doesn't have access to the semantic answer material, and selenium, which works great and is free but will require a lot of careful parsing.