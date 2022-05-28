python -m pytest --cov=flashcards --cov-report=xml --cov-report=html --junitxml="reports/junit.xml" tests
mkdir -p reports
mv coverage.xml htmlcov reports/.
