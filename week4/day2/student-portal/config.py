import os

variable_which_i_wont_use = "this is a variable which i wont use"


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_LINK")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

#DB_LINK = "postgresql://myuser:mypassword@database-for-student-portal.cu3wwe2iw53s.us-east-1.rds.amazonaws.com:5432/mydb"