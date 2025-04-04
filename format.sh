isort ./bemore
black ./bemore

isort ./tests
black ./tests

flake8 ./bemore
result1=$?

flake8 ./tests
result2=$?

if [[ "$result1" != "0" ]] || [[ "$result2" != "0" ]]; then
  echo "Formatting failed, flake8 errors remain"
  exit 1
fi
