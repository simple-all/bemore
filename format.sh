isort noodle
black noodle
flake8 noodle
if [[ "$?" != "0" ]]; then
  echo "Formatting failed, flake8 errors remain"
  exit 1
fi