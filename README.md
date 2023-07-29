
# Gaming BacklogTracker




## Overview
This Flask web app is designed to help gamers (like myself who buys games and doesn't play them right away) keep track of their gaming backlogs alongside other pertinent information such as completion progress, total hours, total cost spent, and so forth. Users can create backlogs in which games can be added and categorized as in-progress or completed. Additionally, users may input information about a specific game such as how long it takes to beat, the cost at which the it was purchased, then easily visualize this information on a single page. 

## Screenshots

<img src="https://github.com/onelastbyt3/backlogtracker/blob/main/app/screenshots/1.png" width="700" height="450">

<img src="https://github.com/onelastbyt3/backlogtracker/blob/main/app/screenshots/2.png" width="700" height="450">


## Installation

1. Clone this repository to your local machine using the command:
```
git clone https://github.com/onelastbyt3/backlogtracker.git
```

2. Ensure you have Python installed (ver.3.9.9)

3. Install the required dependencies using the command: 
```
pip install -r requirements.txt
```

4. Configure your PostgreSQL database URI and secret key in the source code on the init file located inside the app folder:
```
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
```

5. Create a database in your PostgreSQL, then migrate/upgrade the tables.
```
flask db migrate
flask db upgrade
```

6. Run the application from the main.py file located on the root folder which will generate a local URI link where the app will run.
```
python main.py
```

## Development Notes

As a backend developer, my main focus for this project was on creating a robust backend to handle all functionalities. Leveraging Flask and PostgreSQL, I built a simple CRUD API with various endpoints that enable users to efficiently manage their gaming backlogs. Users can add new games, mark them as completed, update game information, and remove games from their backlogs through these endpoints. This led me to craft a focused ER diagram with three main entities: Users, Backlogs, and Games. Each entity would have non-nullable properties associated with them, with relationships mainly being one-to-many, as users can have many backlogs, but a backlog belongs to only one user, and a backlog can have many games, while a game is specific to at least one backlog. 

For the persistent database, I chose to go with PostgreSQL for its numerous advantages. PostgreSQL is renowned for its reliability, stability, and scalability. It efficiently handles large volumes of data and supports seamless growth as the app attracts more users which is appealing for scalability. Furthermore, PostgreSQL's ACID compliance ensures data integrity and consistency, making it the ideal choice for maintaining the security and reliability of the app's data.  

A challenging aspect of development was providing users with easily accessible insights into their gaming backlogs, in particular on the user dashboard. To accomplish this, I wrote SQL statements to calculate and retrieve essential data from the database, including cleared backlogs, total number of games, and total cost spent on games. 
```
total_cash_spent_query = db.session.execute(
        "SELECT COALESCE(SUM(purchase_price), 0) AS total_purchase_price "
        "FROM game "
        "WHERE backlog_id IN ("
        "  SELECT id "
        "  FROM backlog "
        "  WHERE user_id = :user_id"
        ")",
        {"user_id": current_user.id})
    total_cash_spent = total_cash_spent_query.fetchone()["total_purchase_price"]
```

An issue I ran into during this process however was when I trying to display them properly. After much tinkering, it turned out that I simply had to return the variable (total_games, etc) set to itself in the function argument of render_template following the 'dashboard.html'. One simple mistake, but a lot learned. 

```
return render_template('dashboard.html', cleared_backlogs=cleared_backlogs, total_games=total_games, howlongtobeat_total=howlongtobeat_total,total_cash_spent=total_cash_spent)
```

Overall, this was a very fun project to build and learn from. I hope this app can help you or others tackle the dreaded old gaming backlog with much success. As the app is designed to scale, meaning more functionality such as user interaction, or consuming game information from another API such as HowLongToBeat's, can be implemented to further enhance the user experience. I do plan on adding testing, containerizing the app, and later deploy this for general use using a Cloud service. 

## License
This project is open-source and available under the MIT license.

## Contributions
Contributions to this project are welcome, as this was a simple project with many features/design elements still lacking mainly in CSS styling and overall page aesthetic. Any frontend developers looking to contribute are welcome to submit a pull request for review! 
