# iOS Contacts to csv
Converts screenshots of iOS contacts into CSV file that could be imported into Google Contacts.

## Why
An exercise to experiment with [Google's Tessaract OCR](https://github.com/tesseract-ocr/tesseract) and [pytessaract](https://pypi.org/project/pytesseract/).

## Problem
When adding work Exchange account to iOS devices, the default contacts storage location changes to the work account. This means that the old contacts stay where they are, but newer contacts will end up being saved in work account. Of course, this is not entirely obvious, so one may save one-too-many contacts in these work accounts. Unfortunately, there is no easy way to change a contact's saving-location to a different account. There are currently two ways to do this:

1. (Manual) Go into each contact, export each contact to file. Then re-import them into contacts after changing default contacts storage... by going through each file. This method is foolproof and recommended yet slow, since all your data will make it across.
1. (This repo) Take screenshots of each contact, use this program to generate a CSV that you can import into [contacts.google.com](https://contacts.google.com).

### Beware
1. OCR is a guessing game. It does not yield 100% correct data.
2. Your screenshot may not capture a long contact.

## Install
```
brew bundle
pip install -r requirements.txt
```

## Usage
```
source venv/bin/activate
python ios-contacts.to-csv.py  --image <filename-1> [<file-name-2>] # try with an example file
```