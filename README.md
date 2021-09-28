# Pybrary #
A Python program to manage a library of PDFs.

Script can be run dicrectly, through `pybrary.py`. I recommend that it is run from `pybrary.bat` (on Windows). The batch file will automatically activate a virtualenv and then run the script.

The library data is stored in `library.json`. An example is included in the repo.

I have also included a virtual environment with necessary packages installed.

The GUI is written using [PyQt5](https://pypi.org/project/PyQt5/), and the add, delete and open icons used were taken from [Bootstrap Icons](https://icons.getbootstrap.com/). The book icon for the window was taken from [SVG Repo](https://www.svgrepo.com/).

## Recommended directory structure: ##

* master directory  
  * pybrary.bat  
  * books  
    * books go here  
  * Pybrary  
    * pybrary.py  
    * env  
    * resources  
    * etc.  

## Screenshots: ##
Main window:
![image](https://user-images.githubusercontent.com/22815544/135133146-6440d777-bdf0-463f-b3bd-133be57023d5.png)

Add new file to library:
![image](https://user-images.githubusercontent.com/22815544/135134333-f621d4f4-93b2-43d1-ba44-88b1641b2e39.png)

Pop-ups:

![image](https://user-images.githubusercontent.com/22815544/131254813-3a3bd8d8-8cee-474d-b14d-0c9c714f945e.png)
![image](https://user-images.githubusercontent.com/22815544/131254837-af5aae6d-a875-4e04-ad7d-1a17bd361ad0.png)

