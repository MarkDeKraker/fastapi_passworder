#!/bin/zsh

git clone https://github.com/MarkDeKraker/fastapi_passworder.git

cd "./fastapi_passworder"

pip3 install -r requirements.txt
python3 -m unittest discover .

if [ $? -eq 0 ];
then
    echo "All tests were succesful"
else
    echo "Failed test: $?"
    echo 1;
fi

git describe --tags > "./git_mark_tags.txt"

cd ".."
mkdir "passworder_test"
mv "./fastapi_passworder" "passworder_test"
cd "./passworder_test/fastapi_passworder/passworder"

python3 main.py