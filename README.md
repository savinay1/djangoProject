# Movie Review Sentiment Analysis using Reddit 

## Tools Used: Python,Django,Apache Solr
### Prerequisites
1. Run scrape.py in Reddit_scraper to scrape reddit posts in the form of csv from Reddit
2. Install Apache Solr.
3. Navigate to Apache Solr bin directory and run command
    >bin/solr start
4. Create solr core
    >solr create -c movies
5. Navigate to csv directory ,unzip the docs and run the following command:
    >find . -name "*.csv" -print0 | xargs -0 ../bin/post -c movies
### To run the project on localhost run the command in the root directory
>python manage.py runserver
