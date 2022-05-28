rm -rf build dist
pyinstaller --onedir --console  --collect-all flashcards  --add-data locales:locales --name flashcards flashcards/__main__.py

