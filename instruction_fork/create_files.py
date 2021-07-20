import sqlite3
import sys
import traceback
import logging
import os


def create_table():
    """
    Creates the files and directories necessary to run and test the bot, outside the repo.
    Returns
    -------
        None

    Usage
    -----
        python3 create_files
    """
    try:
        if sys.argv[1] == "help":
            print(help(create_table))
            return ""
        else:
            if not os.path.exists("src/fiche/Saves_files"):
                os.makedirs("src/fiche/Saves_files")

            db = sqlite3.connect(f"src/owlly.db", timeout=300)
            c = db.cursor()

            author = """create table AUTHOR
            (
                channel_id INTEGER default 0,
                userID     INTEGER default 0,
                idS        INTEGER default 0,
                created_by INTEGER default 0,
                primary key (channel_id)
            );"""

            category = """create table CATEGORY
            (
                idM           INTEGER default 0,
                channelM      INTEGER default 0,
                category_list TEXT    default 0,
                idS           INTEGER default 0,
                config_name   INTEGER default 0,
                constraint CATEGORY_pk
                    primary key (idM)
            );
            """

            DC = """create table DC
                (
                    idDC   INTEGER default 0,
                    idS    INTEGER default 0,
                    idU    INTEGER default 0,
                    Nom    TEXT    default 0,
                    Avatar TEXT    default 0,
                    Token  TEXT    default 0,
                    Active INTEGER default 0,
                    primary key (idDC)
                );"""

            fiche = """create table FICHE
            (
                idS              INTEGER default 0,
                fiche_pj         INTEGER default 0,
                fiche_pnj        INTEGER default 0,
                fiche_validation INTEGER default 0,
                champ_general    TEXT    default 0,
                champ_physique   TEXT    default 0,
                primary key (idS)
            );"""

            dice = """create table DICE
            (
                idS        int  default 0,
                Dice       text default 0,
                seuil      text default 0,
                nb         int  default 0,
                stats      text default 0,
                type_borne text default 0,
                constraint Roll_Serv_pk
                    primary key (idS)
            );"""

            serveur = """create table SERVEUR
            (
                prefix     TEXT    default 0,
                idS        INTEGER default 0,
                roliste    TEXT    default 0,
                notes      INTEGER default 0,
                rolerm     TEXT    default 0,
                chanRP     TEXT    default 0,
                maxDC      INTEGER default -1,
                sticky     INTEGER default 0,
                tag        TEXT    default 0,
                tokenHRP   TEXT    default 0,
                delete_hrp INTEGER default 0,
                delay_HRP  INTEGER default 0,
                primary key (idS)
            );"""

            stats = """create table CARAC
            (
                idP    int  default 0,
                idS    int  default 0,
                Alias  text default 0,
                stats text default 0,
                constraint STATS_pk
                    primary key (Alias, idP, idS)
            );
            """

            ticket = """create table TICKET
            (
                idM        INTEGER default 0,
                channelM   INTEGER default 0,
                channel    INTEGER default 0,
                num        TEXT,
                modulo     INTEGER default 0,
                limitation INTEGER default 0,
                emote      TEXT    default 0,
                idS        INTEGER default 0,
                name_auto  TEXT    default 0,
                primary key (idM)
            );"""
            c.execute(author)
            c.execute(ticket)
            c.execute(serveur)
            c.execute(fiche)
            c.execute(DC)
            c.execute(category)
            c.execute(dice)
            c.execute(stats)
            c.close()
            db.close()
            f = open(".gitignore", "a")
            f.write("src/\n")
            f.close()
    except BaseException as error:
        print("An exception occurred: {}".format(error))
        print(help(create_table))


if __name__ == "__main__":
    create_table()
