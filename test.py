import sqlite3


def up_DB(base, var, row, idT, value):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    base = base
    var = var
    row = row
    idT = idT
    value = value
    sql = "UPDATE " + base + " SET " + var + " = ? WHERE " + row + " = ?"
    var_sql = (value, idT)
    c.execute(sql, var_sql)
    db.commit()
    c.close()
    db.close()
    print("Done")


up_DB("SERVEUR", "maxDC", "idS", 453162143668371456, 5)


def select_DB(base, row, type, value):
    db = sqlite3.connect("src/owlly.db", timeout=3000)
    c = db.cursor()
    value = str(value)
    sql = "SELECT " + row + " FROM " + base + " WHERE " + type + " = " + value + ""
    c.execute(sql)
    result = c.fetchone()
    if result is None:
        print("Result is none")
        result = "0"
    else:
        print(result[0])
        result = result[0]
    c.close()
    db.close()
    return result


select_DB("SERVEUR", "maxDC", "idS", 453162143668371456)
