import sqlite3
import datetime


def ongoing_party(parties):
    TD0 = datetime.timedelta(0)
    for party in parties:
        start_time = party[4]
        end_time = party[5]
        if datetime.datetime.now() - datetime.datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S') > TD0 and datetime.datetime.now() - datetime.datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S') < TD0:
            party_id = party[0]
            return party_id
    return None


def closest_party(parties):
    TD0 = datetime.timedelta(0)
    party_id = 0
    gaps = {}
    for party in parties:
        start_time = party[4]
        delta = datetime.datetime.now() - datetime.datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
        if delta > TD0:
            party_id = party[0]
            gaps[party_id] = delta
    if not gaps:
        return "No Scheduled Parties"
    else:
        closest = min(gaps.values())
        for ID, val in gaps.items():
            if val == closest:
                party_id = ID
        return party_id


def request_handler(request):
    sound_db = "__HOME__/iParty/sound_level.db"
    conn = sqlite3.connect(sound_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # move cursor into database (allows us to execute commands)

    if request['method'] == "GET":
        c.execute('''CREATE TABLE IF NOT EXISTS parties_table (party_id int, party_name string, capacity int, location string, start_time timestamp, end_time timestamp);''')  # run a CREATE TABLE command
        parties = c.execute('''SELECT * FROM parties_table;''').fetchall()
        party_id = ongoing_party(parties)
        if party_id is None:
            party_id = closest_party(parties)
        levels = c.execute('''SELECT level FROM sound_level WHERE party_id = (?) ORDER BY timing DESC''', (party_id,)).fetchone()[0]
        #levels_list = map(int, levels.split(","))
        conn.commit()
        conn.close()
        return levels

    elif request['method'] == "POST":
        c.execute('''CREATE TABLE IF NOT EXISTS parties_table (party_id int, party_name string, capacity int, location string, start_time timestamp, end_time timestamp);''')  # run a CREATE TABLE command
        c.execute('''CREATE TABLE IF NOT EXISTS sound_level (party_id int, level int, timing timestamp);''')  # run a CREATE TABLE command
        parties = c.execute('''SELECT * FROM parties_table;''').fetchall()
        party_id = ongoing_party(parties)
        if party_id is None:
            party_id = closest_party(parties)
        c.execute('''INSERT INTO sound_level VALUES (?,?,?);''', (party_id,request['form']['levels'],datetime.datetime.now()))
        conn.commit()
        conn.close()
        return request['form']['levels']



