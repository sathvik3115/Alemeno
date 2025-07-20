Project Structure

Alemeno/
├── backend/credit_system
 		└── credit_system/ # Django project (settings.py)
 		├── api/ # Main Django app (views, models, urls, tests, tasks)
 		└── manage.py
├── data/ # customer_data.xlsx & loan_data.xlsx
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README

Features:

- Register new customers
- Calculate credit score based on historical data
- Loan eligibility check with interest rate adjustments
- Loan creation based on eligibility
- View loan details with /view-loan/loan_id and also with /view-loans/customer_id
- Unit tests included
- Fully Dockerized deployment



USING DOCKER DESKTOP, POSTGRES, PGADMIN4


For Running Project:

RUN: 
PS D:\Alemeno\backend\credit_system> docker-compose up --build
and then CTRL+C for exiting and then:
PS D:\Alemeno\backend\credit_system> docker-compose up -d  #FOR RUNNING SERVICES "web" & "db" (MUST NEEDED)
[+] Running 2/2
 ✔ Container alemeno-web-1  Started 1.2s 
 ✔ Container alemeno-db-1   Started 0.4s 

Build and run the Django app inside a container
Run the database service (PostgreSQL or MongoDB)
Expose Django on http://localhost:8000

PS D:\Alemeno> docker-compose exec web python backend/credit_system/manage.py makemigrations  #MIGRATIONS
PS D:\Alemeno> docker-compose exec web python backend/credit_system/manage.py migrate

PS D:\Alemeno> docker-compose exec web python backend/credit_system/manage.py test api  #UNIT TESTS

PS D:\Alemeno> docker-compose exec web python backend/credit_system/manage.py createsuperuser  #SUPER USER ACCESS FROM /admin
# I have created one:
Username (leave blank to use 'root'): alemeno 
Email address: alemeno@gmail.com
Password: qwerty123




PS D:\Alemeno> docker-compose exec web pip install requests  #FOR INSTALLING MODULES ON "module not found" ERROR


Entire project is running accurately
if any issue, feel free to contact me any time
Mobile No.: +91 6359630820
Email ID: vemulasathvik3115@gmail.com
GitHub: https://github.com/sathvik3115
LinkedIn: https://www.linkedin.com/in/sathvik-vemula-027022359/






