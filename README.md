# The Times - Next Generation Smart News

#Application for recommending live news obtained from news api 

libraries and api's used -

1)News Api to get live news

2)Newspaper library for natural language processing and article curation 

3)Ny times Search api library to generate recommended news based on keywords extracted from step 2

Web application built in flask 

[Register for news api access here](https://newsapi.org/register "News Api")

[Link to the newspaper library](https://github.com/codelucas/newspaper "Newspaper library")

[Register for ny times search api](http://developer.nytimes.com "Ny times search api")


**Steps to run the application -**

1)fork the repository 

2)Run `pip install -r requirements.txt` to install required packages in python

3) Install news paper library `pip install newspaper` .[ For further details](https://pypi.python.org/pypi/newspaper "newspaper library") 

4) Install ny times article package `pip install nytimesarticle`. [ For further details](https://pypi.python.org/pypi/nytimesarticle/0.1.0 "ny times article package")

5)Insert both api keys in their respective placeholders in `app/views.py`
 
6)to create user  login database  -`python db_create.py` 

7)to run the application - `python run.py`

Project by Karan Chaudhari (kc3289) and Rewa Jayant Kale (rjk422):

**Currently completed features -**

1)login(based on openid)

2)news api data extraction

3)passing news api data to curate and process news articles

4)curate and process obtained data using newspaper library for similar news articles

5)Dropdown to select a particular category of news like (business, entertainment, science-and-nature, music, technology, etc.)

6)Storing the data for user views, news articles, recommendations in Elasticsearch

7)Recommending news articles based on user views using NLP algorithm

8)Added an additional feature of sending emails (using Gmail address) and sms to any (T mobile number) using MIMEMultipart and MIMEText python libraries

9)Search news by a keyword eg: desktops

10)Improved the UI through CSS styles

11)Added weather widget using accuweather.com widget to show current weather details, mta widget for subway details

