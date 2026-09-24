# earmark


<!-- README.md is generated from README.qmd by `quarto render README.qmd`.
     The body below is assets/_common.qmd, shared with the docs landing page:
     edit that file, not README.md. -->

<img src="docs/logo.png" align="right" width="160" alt="earmark logo" />

Turn articles into dictated audio, then publish to a public podcast feed

**[Documentation →](https://earmark-dev.github.io/earmark/)**

`earmark` turns articles and documents into dictated audio that you can
stream to your phone. Give it a URL or a document (PDF, DOCX, PPTX,
EPUB, HTML, Markdown), and earmark will extract the text, clean it for
listening, dictate it with
[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), and add the MP3
to a podcast feed that you subscribe to on your phone.

The audio is a word-for-word dictation of the text. earmark removes
things that do not read well aloud, such as links, citations and
reference lists. It does not summarize the text or rewrite it as a
podcast show.

No API keys, no subscriptions, no per-minute cost.

## Two ways to use it

**[Use it on
GitHub](https://earmark-dev.github.io/earmark/github/setup.html)
(recommended).** Make a repo from a template and turn on GitHub Pages.
Then list what you want to hear in `sources.yml`. Each commit dictates
the new entries and updates your feed. You install nothing and run
nothing.

**[Use it
locally](https://earmark-dev.github.io/earmark/local/install.html).**
Install the command-line tool and run
`earmark publish https://example.com/article`. Host the library on
pCloud, a storage bucket or your own server.

The [Reference](https://earmark-dev.github.io/earmark/reference/) lists
every command, flag and setting.

## Development

``` bash
uv venv --python 3.12
uv pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```

The docs site is built with
[great-docs](https://github.com/posit-dev/great-docs):

``` bash
uv tool install great-docs
great-docs preview
```

## License

MIT © John Paul Helveston
