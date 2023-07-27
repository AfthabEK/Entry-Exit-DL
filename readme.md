
# ENTRY EXIT SYSTEM
This application is used to track the entry and exit of students in the NITC library. 

On ubuntu
sudo apt update
sudo apt install git
sudo apt install python3-pip
sudo apt install python3-virtualenv

git clone https://github.com/AfthabEK/Entry-Exit-DL.git
cd Entry-Exit-DL
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt

In the views.py file inside the enter folder, change the readerIP into the required IP address.

python3 manage.py runserver

