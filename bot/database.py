import os
import psycopg2


def url():
    return os.environ['DATABASE_URL']


def rows_to_text(rows):
    txt = f'{len(rows)} records retrieved'
    for i, row in enumerate(rows):
        txt += f'\n{i+1}: {row}'
    return txt


def error_to_text(header, e):
    txt = header
    txt += f'Error: {e.pgerror.strip()} (Code: {e.pgcode})\n'
    txt += f'Message: {e.diag.message_primary} (Severity: {e.diag.severity})'
    print(txt)
    return txt


class HerokuDB():
    """Class for a Heroku Database"""

    def __init__(self, params=None):
        self._url = None
        self._lasterr = None
        self._conn = self.connect(params)

    def get_url(self):
        try:
            url = os.environ['DATABASE_URL']
        except:
            print('DATABASE_URL is not defined')
            print('Did you attach the Heroku Postgres add-on in your app\'s dashboard?')
            url = None
        return url

    def connect(self, params=None):
        if params is None:
            self._url = get_url()
            if self._url is None:
                print('Cannot connect without URL')
                return None
            try:
                conn = psycopg2.connect(self._url, sslmode='require')
            except (Exception, psycopg2.Error) as e:
                print(
                    f'Failed to connect to PostgreSQL DB at URL: {self._url}')
                return None
        else:
            try:
                conn = psycopg2.connect(
                    user=params['USER'],
                    password=params['PASSWORD'],
                    host=params['HOST'],
                    port=params['PORT'],
                    database=params['DATABASE'])
            except (Exception, psycopg2.Error) as e:
                print(f"Failed to connect to PostgreSQL DB. Error: {e}")
                return None
        return conn

    def dsn(self):
        return self._conn.get_dsn_parameters()  # [dictionary]

    def fetchone(self, sql_query, my_tuple=None, err_msg=None):
        try:
            with self._conn.cursor() as c:
                if my_tuple is None:
                    c.execute(sql_query)
                else:
                    c.execute(sql_query, my_tuple)
                rows = c.fetchone()  # [a tuple of length 1]
                txt = f'Success: execute("{sql_query}", ({my_tuple})); fetchone()'
                self._lasterr = None
        except psycopg2.Error as e:
            rows = None
            if err_msg is None:
                txt = error_to_text(
                    f'Failed to execute "{sql_query}" followed by fetchone\n', e)
            else:
                txt = error_to_text(err_msg, e)
            self._lasterr = e
        return {'data': rows, 'txt': txt, 'err': self._lasterr}

    def fetchall(self, sql_query, my_tuple=None, err_msg=None):
        try:
            with self._conn.cursor() as c:
                if my_tuple is None:
                    c.execute(sql_query)
                else:
                    c.execute(sql_query, my_tuple)
                rows = c.fetchall()
                txt = f'Success: execute("{sql_query}", ({my_tuple})); fetchall()'
                self._lasterr = None
        except psycopg2.Error as e:
            rows = None
            if err_msg is None:
                txt = error_to_text(
                    f'Failed to execute "{sql_query}" followed by fetchall\n', e)
            else:
                txt = error_to_text(err_msg, e)
            self._lasterr = e
        return {'data': rows, 'txt': txt, 'err': self._lasterr}

    def commit(self, sql_query, my_tuple=None, err_msg=None):
        try:
            with self._conn.cursor() as c:
                if my_tuple is None:
                    c.execute(sql_query)
                else:
                    c.execute(sql_query, my_tuple)
                self._conn.commit()
                txt = f'Success: execute("{sql_query}", ({my_tuple})); commit()'
                self._lasterr = None
        except psycopg2.Error as e:
            if err_msg is None:
                txt = error_to_text(
                    f'Failed to execute+commit "{sql_query}", {my_tuple}\n', e)
            else:
                txt = error_to_text(err_msg, e)
            self._lasterr = e
        return {'data': None, 'txt': txt, 'err': self._lasterr}

    def custom(self, cmd, my_tuple=None, my_params=None):
        if cmd not in command_dictionary.keys():
            print('Command not found')
            return None
        cmd_type, sql_query, err_msg = command_dictionary[cmd]
        if my_params is not None:
            sql_query = sql_query.format(**my_params)
            err_msg = err_msg.format(**my_params)
        print(
            f'conn.cursor.{cmd_type}("{sql_query}", {my_tuple}), err_msg="{err_msg}", my_params={my_params}')
        if cmd_type == 'fetchone':
            r = self.fetchone(sql_query, my_tuple, err_msg)
        elif cmd_type == 'fetchall':
            r = self.fetchall(sql_query, my_tuple, err_msg)
        elif cmd_type == 'commit':
            r = self.commit(sql_query, my_tuple, err_msg)
        else:
            print(f'Invalid cmd_type = {cmd_type}')
            r = None
        return r

    def close(self):
        try:
            if (self._conn):
                self._conn.close()
                txt = "PostgreSQL connection closed"
                self._conn = False
            else:
                print('PostgreSQL connection is already closed')
        except psycopg2.Error as e:
            txt = error_to_text('Failed to close database connection\n', e)
            print('Failed to close connection')
        finally:
            return txt, self._conn

    def check_connection(self):
        if self._conn is None:
            txt = 'Database is not connected'
            print(txt)
            return txt
        else:
            print(self._conn)
            print(f'\nConnection - dsn: {self._conn.dsn}')
            print(f'\nDSN parameters: {self._conn.get_dsn_parameters()}')

            txt = f'Database is connected at {self._url}'
            txt += f'\nDSN parameters: {self._conn.get_dsn_parameters()}'
            txt += f'\nClosed: {self._conn.closed} (0 = open, non-zero = closed/broken)'
            return txt


class HerokuDiscordTable(HerokuDB):

    def __init__(self, params=None):
        self._lasterr = None
        self._url = None
        self._conn = super().connect(params)
        if params is None:
            self._url = super()._url

    def dsn(self):
        return super().dsn()

    def fetchone(self, sql_query, my_tuple=None, err_msg=None):
        return super().fetchone(sql_query, my_tuple, err_msg)

    def fetchall(self, sql_query, my_tuple=None, err_msg=None):
        return super().fetchall(sql_query, my_tuple, err_msg)

    def commit(self, sql_query, my_tuple=None, err_msg=None):
        return super().commit(sql_query, my_tuple, err_msg)

    def custom(self, cmd, my_tuple=None, my_params=None):
        return super().custom(cmd, my_tuple, my_params)

    def close(self):
        txt, self._conn = super().close()
        return txt

    def drop(self):
        sql_query = """DROP TABLE IF EXISTS players;"""
        txt, e = super().commit(sql_query)
        if e is None:
            return txt
        else:
            return error_to_text('Failed to delete table\n', e)

    def add_column(self, column_name, data_type):
        if data_type == 'TEXT':
            sql_query = """ALTER TABLE players ADD %s TEXT;"""
        else:
            return f'Unknown/unimplemented data type: {data_type}'
        txt, e = super().commit(sql_query, (column_name,))
        if e is None:
            return txt
        else:
            return error_to_text(f'Failed to add column {column_name}\n', e)

    def drop_column(self, column_name):
        sql_query = """ALTER TABLE players DROP COLUMN %s;"""
        txt, e = super().commit(sql_query, (column_name,))
        if e is None:
            return txt
        else:
            return error_to_text(f'Failed to drop column {column_name}\n', e)

    def read(self):
        sql_query = """SELECT * from players;"""
        rows, txt, e = super().fetchall(sql_query)
        if rows is None:
            return txt
        else:
            return rows_to_text(rows)

    def getrow(self, discord_id):
        sql_query = """SELECT * from players WHERE discord_id = %s;"""
        rows, txt, e = super().fetchall(sql_query, (discord_id,))
        if rows is None:
            return txt
        else:
            return rows_to_text(rows)

    def set_home_discord(self, author_id, server_id, author_name):
        sql_query = """INSERT INTO players (discord_id, server_id, discord_name)
            VALUES (%s, %s, %s) ON CONFLICT (discord_id) DO UPDATE SET server_id = EXCLUDED.server_id;"""
        my_tuple = (author_id, server_id, author_name)
        txt, e = super().commit(sql_query, my_tuple)
        if e is None:
            return txt
        else:
            return error_to_text(f'Failed to set home discord {server_id}\n', e)

    def insert_ign(self, author_id, server_id, author_name, ign):
        sql_query = """INSERT INTO players (discord_id, server_id, discord_name, ign)
            VALUES (%s, %s, %s, %s) ON CONFLICT (discord_id) DO UPDATE SET ign = EXCLUDED.ign;"""
        my_tuple = (author_id, server_id, author_name, ign)
        txt, e = super().commit(sql_query, my_tuple)
        if e is None:
            return txt
        else:
            return error_to_text(f'Failed to set ign = "{ign}"\n', e)

    def insert_local(self, author_id, server_id, author_name, txt):
        # To do: local data can only be done on home discord
        sql_query = """INSERT INTO players (discord_id, discord_name, local_data)
            VALUES (%s, %s, %s) ON CONFLICT (discord_id) DO UPDATE SET local_data = EXCLUDED.local_data;"""
        my_tuple = (author_id, author_name, txt)
        txt, e = super().commit(sql_query, my_tuple)
        if e is None:
            return txt
        else:
            return error_to_text(f'Failed to set local_data = "{local_data}"\n', e)

    def insert_global(self, author_id, author_name, txt):
        sql_query = """INSERT INTO players (discord_id, discord_name, global_data)
            VALUES (%s, %s, %s) ON CONFLICT (discord_id) DO UPDATE SET global_data = EXCLUDED.global_data;"""
        my_tuple = (author_id, author_name, txt)
        txt, e = super().commit(sql_query, my_tuple)
        if e is None:
            return txt
        else:
            return error_to_text(f'Failed to set global_data = "{global_data}"\n', e)

    def sql_commit(self, sql_query):
        txt, e = super().commit(sql_query)
        if e is None:
            return txt
        else:
            return error_to_text(f'Failed to execute+commit query: "{sql_query}"\n', e)

    def sql_fetch(self, sql_query):
        rows, txt, e = super().fetchall(sql_query)
        if e is None:
            return rows_to_text(txt)
        else:
            return error_to_text(f'Failed to execute+fetchall query: "{sql_query}"\n', e)
