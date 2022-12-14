# Summary

This programme translates a tex file using google translate. Since feeding
latex commands to google translate leads to problems, what this programme does
is to replace all equations and anything related to math commands with
placeholders, translate the text, and then place back the commands.

The default translates from English into Spanish but you can change this
in line 10 of translate.py:

```
translator = GoogleTranslator(source='en', target='es')
```

## Usage

* First create a virtual environment and make sure it's python3

```
python3 -m venv env
```

* Activate it

```
source ./env/bin/activate
```

* Install dependencies

```
pip install -r requirements.txt
```

* Use it like this

```
python translate.py yourfile.tex
```
