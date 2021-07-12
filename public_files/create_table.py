import sqlite3
import sys
import traceback
import logging


def create_table():
    """
    Creates a table based on the original database, but emptied, to allow testing for users outside the repo.
    Parameters
    -----------
      database
        A database (if not exist, it will be created)

    Returns
    -------
        None

    Usage
    -----
        python3 create_table database_name
    """
    try:
        if sys.argv[1] == "help":
            print(help(create_table))
            return ""
        else:
            db = sqlite3.connect(f"{sys.argv[1]}.db")
            c = db.cursor()
            author = """CREATE TABLE "AUTHOR" (
                "channel_id"	INTEGER,
                "userID"	INTEGER,
                "idS"	INTEGER,
                "created_by"	INTEGER,
                PRIMARY KEY("channel_id")
            );"""

            category = """CREATE TABLE "CATEGORY" (
                "idM"	INTEGER,
                "channelM"	INTEGER,
                "category_list"	TEXT,
                "idS"	INTEGER,
                "config_name"	INTEGER
            );
            """

            DC = """CREATE TABLE "DC" (
                "idDC"	INTEGER,
                "idS"	INTEGER,
                "idU"	INTEGER,
                "Nom"	TEXT,
                "Avatar"	TEXT,
                "Token"	TEXT,
                "Active"	INTEGER,
                PRIMARY KEY("idDC")
            );"""

            fiche = """CREATE TABLE "FICHE" (
        	    "idS"	INTEGER,
        	    "fiche_pj"	INTEGER,
        	    "fiche_pnj"	INTEGER,
        	    "fiche_validation"	INTEGER,
        	    "champ_general"	TEXT,
        	    "champ_physique"	TEXT,
        	    PRIMARY KEY("idS")
            );"""

            serveur = """CREATE TABLE "SERVEUR" (
            	"prefix"	TEXT,
            	"idS"	INTEGER,
            	"roliste"	TEXT,
            	"notes"	INTEGER,
            	"rolerm"	TEXT,
            	"chanRP"	TEXT,
            	"maxDC"	INTEGER,
            	"sticky"	INTEGER,
            	"tag"	TEXT,
            	"tokenHRP"	TEXT,
            	"delete_hrp"	INTEGER,
            	"delay_HRP"	INTEGER,
            	PRIMARY KEY("idS")
            );"""

            ticket = """CREATE TABLE "TICKET" (
            	"idM"	INTEGER,
            	"channelM"	INTEGER,
            	"channel"	INTEGER,
            	"num"	TEXT,
            	"modulo"	INTEGER,
            	"limitation"	INTEGER,
            	"emote"	TEXT,
            	"idS"	INTEGER,
            	"name_auto"	TEXT,
            	PRIMARY KEY("idM")
            );"""
            c.execute(author)
            c.execute(ticket)
            c.execute(serveur)
            c.execute(fiche)
            c.execute(DC)
            c.execute(category)
            c.close()
            db.close()
    except BaseException as error:
        print("An exception occurred: {}".format(error))
        print(help(create_table))


if __name__ == "__main__":
    create_table()
