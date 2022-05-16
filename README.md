# Movie Review Sentiment Analysis using Reddit 

## Tools Used: Python,Django,Apache Solr
### Prerequisites
1. Run scrape.py to fetch documents from Reddit Posts
2. Install Apache Solr.
3. Navigate to bin directory and run command
    >bin/solr start
4. Create solr core
    >solr create -c movies
5. Navigate to csv directory ,unzip the docs and run the following command:
    >find . -name "*.csv" -print0 | xargs -0 ../bin/post -c movies
### To run the project on localhost run the command in the root directory
>python manage.py runserver
