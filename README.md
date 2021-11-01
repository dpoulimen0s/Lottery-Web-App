# Lottery Web Application
This project is part of Newcastle University coursework.
This web application represents a lottery system, there are users who can play lottery and 
there is an admin or more if u want to create more who can monitor the whole process and 
defining a new wining draw each round.
(New here)
## Getting Started
In order to start you will need to have python 3.10 and above installed on your computer along with an IDE such as Pycharm which i am going to use here. 
Then open up your Pycharm and create a flask project and name it "LotteryWebapp". After that download the files from github and move them to your project's folder , you should be ready to run the application.

### Requirements
You have to install some libraries to be able to run the application, check requirements.txt and install them to your system.
* [requirements.txt](https://github.com/dpoulimen0s/Lottery-Web-App/blob/main/requirements.txt)

### Database Initialisation
Just in case you want a fresh start of the database itself, go to python console in Pycharm and type:
```python
from models import init_db
init_db()
```

## Built With

* Pycharm
* Windows 10

## Authors

* **Dimitris Poulimenos** - *Initial work* - [dpoulimen0s](https://github.com/dpoulimen0s)


## License

This project is licensed under the Newcastle University License - see the [LICENSE.md](https://github.com/dpoulimen0s/Lottery-Web-App/blob/main/LICENSE) file for details

