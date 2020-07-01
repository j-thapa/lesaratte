# lesaratte
Lesaratte is an online book reviewing site where users can search details about around 5000 books and also leave their comment on the respective books .


This project has been done as a part of Harvard CS50's Web Designing with python and JavaScript.

Flask , HTML and CSS has been used for coding the site whereas postgresql is used for database . 

Goodread and Google Books API has been used to extract details and information about books.

You can check the site hosted in heroku through this link https://readers-insight.herokuapp.com/ .

API Access: If users make a GET request to the website’s as  https://readers-insight.herokuapp.com/api/isbn route, 
where <isbn> is an ISBN number of the book,  website will return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score. 
    
    
The resulting JSON should follow the format:
{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}


