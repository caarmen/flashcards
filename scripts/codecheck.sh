for project in flashcards tests
do
  black $project
  PYTHONPATH=. pylint $project
done
