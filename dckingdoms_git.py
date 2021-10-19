import discord
import pandas as pd
import pymysql
from datetime import datetime, timedelta
import threading
import json
import random

server = ""
user = "" 
pwd = ""
schema = ""

db = pymysql.connect(server, user, pwd, schema)
db.db
cursor = db.cursor(pymysql.cursors.DictCursor) 

#check connection to database
def ping_msql():
  threading.Timer(3600.0, ping_msql).start()
  db.ping(reconnect=True)

ping_msql()

def read_quotes():
    quotes = []
    
    with open("quotes.txt", 'r') as f:
        for l in f:
            quotes.append(l.strip())
    return quotes

quotes = read_quotes()

def get_quote():
    global quotes
    
    quote = "```" + random.choice(quotes) + "```"
    
    return quote

def get_datetime():
        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        
        return formatted_date
    
def add_sub_hours(amount):
    date = datetime.now() + timedelta(hours=amount)
    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_date

def compare_date(database_date):
    database_date = datetime.strptime(database_date, '%Y-%m-%d %H:%M:%S')
    now = get_datetime()
    now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
    
    if now > database_date:
        return True
    else:
        return False
    
def time_diff(database_date):
    database_date = datetime.strptime(database_date, '%Y-%m-%d %H:%M:%S')
    diff = database_date - datetime.now()
    
    return diff

def owner_admin(server_id, user_id):
    query = "SELECT game.owner_id FROM game WHERE server_id = " + server_id + " AND game.owner_id = " + user_id

    df = pd.read_sql(query, db)

    index = df.index
    count = len(index)
    
    if count > 0:
        return True
    else:
        citizen_id = get_citizen_id(server_id, user_id)
        query = "SELECT citizen.id FROM citizen WHERE citizen.id = '%s' AND citizen.role = 'admin'" % (citizen_id)
    
        index = df.index
        count = len(index)
        
        if count > 0:
            return True
        else:
            return False
    
def game_started(server_id):
    query = "SELECT game.id FROM game WHERE server_id = " + server_id
    df = pd.read_sql(query, db)

    index = df.index
    count = len(index)
    
    if count > 0:
        return True
    else:
        return False
    
def update_game(server_id):
    now = get_datetime()
    
    sql = "UPDATE game SET game.updated = '%s' WHERE game.server_id = '%s'" % (now, server_id)
    cursor.execute(sql)
    db.commit()
    
def kingdom_exists(server_id, kingdom_name):
    query = "SELECT kingdom.id FROM kingdom INNER JOIN game ON kingdom.game_id = game.id WHERE name = '%s' AND game.server_id = '%s'" % (kingdom_name, server_id)
    df = pd.read_sql(query, db)

    index = df.index
    count = len(index)
    
    if count > 0:
        return True
    else:
        return False
    
def region_exists(server_id, region_name):
    query = "SELECT kingdom.id FROM region INNER JOIN kingdom ON region.kingdom_id = kingdom.id INNER JOIN game ON kingdom.game_id = game.id WHERE region.name = '%s' AND game.server_id = '%s'" % (region_name, server_id)
    df = pd.read_sql(query, db)

    index = df.index
    count = len(index)
    
    if count > 0:
        return True
    else:
        return False
    
def user_exists(server_id, user_id):
    query = "SELECT citizen.id FROM citizen INNER JOIN kingdom ON citizen.kingdom_id = kingdom.id INNER JOIN game ON kingdom.game_id = game.id WHERE citizen.userid = '%s' AND game.server_id = '%s'" % (user_id, server_id)
    df = pd.read_sql(query, db)

    index = df.index
    count = len(index)
    
    if count > 0:
        return True
    else:
        return False
    
def battle_exists(region_id):
    query = "SELECT attack.id FROM attack WHERE attack.region_id = '%s'" % (region_id)
    df = pd.read_sql(query, db)

    index = df.index
    count = len(index)
    
    if count > 0:
        return True
    else:
        return False
    
def end_battle(battle_id):
    query = "SELECT attack.attacker_strength, attack.defender_strength, attack.region_id, attack.attacker_kingdom, attack.defender_kingdom FROM attack WHERE id = '%s'" % (battle_id)
    df = pd.read_sql(query, db)
    
    attacker_strength = df['attacker_strength'].iloc[0]
    attacker_strength = int(attacker_strength)
    
    defender_strength = df['defender_strength'].iloc[0]
    defender_strength = int(defender_strength)
    
    region_id = df['region_id'].iloc[0]
    region_id = int(region_id)
    
    attacker_kingdom = df['attacker_kingdom'].iloc[0]
    attacker_kingdom = int(attacker_kingdom)
    
    defender_kingdom = df['defender_kingdom'].iloc[0]
    defender_kingdom = int(defender_kingdom)
    
    if attacker_strength > defender_strength:
        sql = "UPDATE region SET region.kingdom_id = '%s' WHERE region.id = '%s'" % (attacker_kingdom, region_id)
        cursor.execute(sql)
        db.commit()
        
        sql = "DELETE from attack WHERE attack.id = '%s'" % (battle_id)
        cursor.execute(sql)
        db.commit()
        
        msg = "The attacker won the battle."
        return msg
    else:
        sql = "DELETE from attack WHERE attack.id = '%s'" % (battle_id)
        cursor.execute(sql)
        db.commit()
        
        msg = "The defender won the battle."
        return msg
    
def select_game_id(server_id):
    query = "SELECT game.id FROM game WHERE game.server_id = " + server_id
    df = pd.read_sql(query, db)
    game_id = df['id'].iloc[0]
    game_id = int(game_id)
    
    return game_id
    
def get_kingdom_id(server_id, kingdom_name):
    game_id = select_game_id(server_id)
    query = "SELECT kingdom.id FROM kingdom INNER JOIN game ON kingdom.game_id = game.id WHERE name = '%s' AND game.id = '%s'" % (kingdom_name, game_id)
    df = pd.read_sql(query, db)
    
    kingdom_id = df['id'].iloc[0]
    kingdom_id = int(kingdom_id)
    
    return kingdom_id

def get_region_id(server_id, region_name):
    query = "SELECT region.id FROM region INNER JOIN kingdom ON region.kingdom_id = kingdom.id INNER JOIN game ON kingdom.game_id = game.id WHERE region.name = '%s' AND game.server_id = '%s'" % (region_name, server_id)
    df = pd.read_sql(query, db)
    
    region_id = df['id'].iloc[0]
    region_id = int(region_id)
    
    return region_id

def get_citizen_id(server_id, user_id):
    query = "SELECT citizen.id FROM citizen INNER JOIN kingdom ON citizen.kingdom_id = kingdom.id INNER JOIN game ON kingdom.game_id = game.id WHERE citizen.userid = '%s' AND game.server_id = '%s'" % (user_id, server_id)
    df = pd.read_sql(query, db)
    
    citizen_id = df['id'].iloc[0]
    citizen_id = int(citizen_id)
    
    return citizen_id

def get_battle_id(region_id):
    query = "SELECT attack.id FROM attack WHERE attack.region_id = '%s'" % (region_id)
    df = pd.read_sql(query, db)

    battle_id = df['id'].iloc[0]
    battle_id = int(battle_id)
    
    return battle_id

def get_king_id(server_id, kingdom_name, user_id):
    if game_started(server_id):  
        if kingdom_exists(server_id, kingdom_name): 
            kingdom_id = get_kingdom_id(server_id, kingdom_name)              
            
            query = "SELECT kingdom.king_id FROM kingdom WHERE id = '%s'" % (kingdom_id)
            df = pd.read_sql(query, db)
            
            king_id = df['king_id'].iloc[0]
            if king_id != None:
                king_id = int(king_id)
            
            return king_id
        else:
            msg = "This kingdom does not exist."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg

def user_is_king(kingdom_id, user_id):
    query = "SELECT kingdom.king_id FROM kingdom WHERE id = '%s'" % (kingdom_id)
    df = pd.read_sql(query, db)
    
    king_id = df['king_id'].iloc[0]
    user_id = int(user_id)
    if king_id != None:
        king_id = int(king_id)
    
    if king_id == user_id:
        return True
    else:
        return False

def start_game(server_id, user_id):
    if game_started(server_id):
        msg = "A game has already started on this server."
        return msg
    else:
        now = get_datetime()
        
        sql = "INSERT INTO game (server_id, owner_id, created, updated) VALUES (%s, %s, %s, %s)"
        val = (server_id, user_id, now, now)
        
        cursor.execute(sql, val)
        db.commit()   
        
        msg = "Game has started."
        return msg
    
def end_game(server_id, user_id):
    if game_started(server_id):
        if owner_admin(server_id, user_id):        
            sql = "DELETE FROM game WHERE game.server_id = '%s'" % (server_id)
            
            cursor.execute(sql)
            db.commit()   
            
            msg = "Game has ended."
            return msg
    else:    
        msg = "A game has not been started on this server."
        return msg
    
def create_kingdom(server_id, user_id, kingdom_name):
    if game_started(server_id):
        if owner_admin(server_id, user_id):
            if kingdom_exists(server_id, kingdom_name):
                msg = "A kingdom with this name already exists."
                return msg
            else:                
                game_id = select_game_id(server_id)
                
                sql = "INSERT INTO kingdom (game_id, name, workpower) VALUES (%s, %s, %s)"
                val = (game_id, kingdom_name, 0)
                
                cursor.execute(sql, val)
                db.commit()   
                
                msg = "Created kingdom."
                return msg
        else:
            msg = "You do not have permission for this command."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def create_region(server_id, user_id, kingdom_name, region_name):
    if game_started(server_id):    
        if owner_admin(server_id, user_id):   
            if kingdom_exists(server_id, kingdom_name):
                if region_exists(server_id, region_name):
                    msg = "A region with this name already exists on this server."
                    return msg
                else:
                    kingdom_id = get_kingdom_id(server_id, kingdom_name)
                    
                    sql = "INSERT INTO region (kingdom_id, name) VALUES (%s, %s)"
                    val = (kingdom_id, region_name)
                    
                    cursor.execute(sql, val)
                    db.commit()   
                    
                    msg = "Created region."
                    return msg
            else:                            
                msg = "There is no kingdom with this name on this server."
                return msg
        else:
            msg = "You do not have permission for this command."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg
 
def set_admin(server_id, user_id, new_admin_id):
    if game_started(server_id):    
        if owner_admin(server_id, user_id):   
            if user_exists(server_id, new_admin_id):
                new_admin_citizen_id = get_citizen_id(server_id, new_admin_id)
                
                sql = "UPDATE citizen SET citizen.role = 'admin' WHERE citizen.id = '%s'" % (new_admin_citizen_id)
                cursor.execute(sql)
                db.commit()
                
                msg = "Added new admin."
                return msg
            else:
                msg = "This user did not joined the game yet."
                return msg
        else:
            msg = "You do not have permission for this command."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg   
    
def demote_admin(server_id, user_id, new_admin_id):
    if game_started(server_id):    
        if owner_admin(server_id, user_id):   
            if user_exists(server_id, new_admin_id):
                new_admin_citizen_id = get_citizen_id(server_id, new_admin_id)
                
                sql = "UPDATE citizen SET citizen.role = 'citizen' WHERE citizen.id = '%s'" % (new_admin_citizen_id)
                cursor.execute(sql)
                db.commit()
                
                msg = "Demoted admin."
                return msg
            else:
                msg = "This user did not joined the game yet."
                return msg
        else:
            msg = "You do not have permission for this command."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg   
 
def set_king(server_id, user_id, kingdom_name, new_king_id):
    if game_started(server_id):    
        if owner_admin(server_id, user_id):   
            if kingdom_exists(server_id, kingdom_name):   
                if user_exists(server_id, new_king_id):
                    kingdom_id = get_kingdom_id(server_id, kingdom_name)
                    game_id = select_game_id(server_id)
                    
                    sql = "UPDATE kingdom SET kingdom.king_id = 'null' WHERE kingdom.king_id = '%s' AND kingdom.game_id = '%s'" % (new_king_id, game_id)
                    cursor.execute(sql)
                    db.commit()
                    
                    sql = "UPDATE kingdom SET kingdom.king_id = '%s' WHERE kingdom.id = '%s' AND kingdom.game_id = '%s'" % (new_king_id, kingdom_id, game_id)
                    cursor.execute(sql)
                    db.commit()
                    
                    msg = "Appointed new king."
                    return msg
                else:
                    msg = "This user did not joined the game yet."
                    return msg
            else:                            
                msg = "There is no kingdom with this name on this server."
                return msg
        else:
            msg = "You do not have permission for this command."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def join_kingdom(server_id, user_id, kingdom_name, region_name):
    if game_started(server_id):           
        if kingdom_exists(server_id, kingdom_name):                
            if region_exists(server_id, region_name):
                if user_exists(server_id, user_id):
                    msg = "You already joined a kingdom."
                    return msg
                else:
                    now = add_sub_hours(-2)
                    
                    kingdom_id = get_kingdom_id(server_id, kingdom_name)
                    region_id = get_region_id(server_id, region_name)
                    
                    sql = "INSERT INTO citizen (kingdom_id, userid, role, strength, trained, location, moved, worked) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (kingdom_id, user_id, "citizen", 0, now, region_id, now, now)
                    
                    cursor.execute(sql, val)
                    db.commit()   
                    
                    msg = "You joined a kingdom."
                    return msg
            else:
                msg = "A region with this name does not exists on this server."
                return msg
        else:                            
            msg = "There is no kingdom with this name on this server."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def train(server_id, user_id):
    if game_started(server_id):                          
        if user_exists(server_id, user_id):
            citizen_id = get_citizen_id(server_id, user_id)
            
            query = "SELECT citizen.trained, citizen.strength FROM citizen WHERE id = '%s'" % (citizen_id)
            df = pd.read_sql(query, db)
            
            trained = df['trained'].iloc[0]
            trained = str(trained)
            
            strength = df['strength'].iloc[0]
            strength = int(strength)
            
            if compare_date(trained):
                new_date = add_sub_hours(1)
                strength = strength + 5
                
                sql = "UPDATE citizen SET citizen.trained = '%s', citizen.strength = '%s' WHERE citizen.id = '%s'" % (new_date, strength, citizen_id)
                cursor.execute(sql)
                db.commit()
                
                msg = "You successfully trained."
                return msg
            else:
                msg = "You can only train once every hour."
                return msg
        else:
            msg = "You do not participate in this game yet."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def work(server_id, user_id):
    if game_started(server_id):                          
        if user_exists(server_id, user_id):
            citizen_id = get_citizen_id(server_id, user_id)
            
            query = "SELECT citizen.worked, citizen.kingdom_id, citizen.currency FROM citizen WHERE id = '%s'" % (citizen_id)
            df = pd.read_sql(query, db)
            
            worked = df['worked'].iloc[0]
            worked = str(worked)
            
            kingdom_id = df['kingdom_id'].iloc[0]
            kingdom_id = int(kingdom_id)
            
            currency = df['currency'].iloc[0]
            currency = float(currency)
            
            query = "SELECT kingdom.workpower FROM kingdom WHERE id = '%s'" % (kingdom_id)
            df = pd.read_sql(query, db)
            
            workpower = df['workpower'].iloc[0]
            workpower = int(workpower)
            
            if compare_date(worked):
                new_date = add_sub_hours(1)
                workpower = workpower + 5
                currency = currency + 5
                
                sql = "UPDATE citizen SET citizen.worked = '%s', citizen.currency = '%s' WHERE citizen.id = '%s'" % (new_date, currency, citizen_id)
                cursor.execute(sql)
                db.commit()
                
                sql = "UPDATE kingdom SET kingdom.workpower = '%s' WHERE kingdom.id = '%s'" % (workpower, kingdom_id)
                cursor.execute(sql)
                db.commit()
                
                msg = "You successfully worked."
                return msg
            else:
                msg = "You can only work once every hour."
                return msg
        else:
            msg = "You do not participate in this game yet."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def attack_region(server_id, user_id, kingdom_name, region_name):
    if game_started(server_id):           
        if kingdom_exists(server_id, kingdom_name):                
            if region_exists(server_id, region_name):
                if user_exists(server_id, user_id):
                    kingdom_id = get_kingdom_id(server_id, kingdom_name)
                    region_id = get_region_id(server_id, region_name)
                    if user_is_king(kingdom_id, user_id):
                        query = "SELECT attack.id FROM attack WHERE region_id = '%s'" % (region_id)
                        df = pd.read_sql(query, db)
                    
                        index = df.index
                        count = len(index)
                        
                        if count == 0:
                            attacker_id = kingdom_id
                            
                            query = "SELECT region.kingdom_id FROM region WHERE id = '%s'" % (region_id)
                            df = pd.read_sql(query, db)
                            
                            defender_id = df['kingdom_id'].iloc[0]
                            defender_id = int(defender_id)
                            
                            new_date = add_sub_hours(12)
                            
                            if attacker_id != defender_id:
                                sql = "INSERT INTO attack (region_id, attacker_kingdom, defender_kingdom, attacker_strength, defender_strength, started) VALUES (%s, %s, %s, %s, %s, %s)"
                                val = (region_id, attacker_id, defender_id, 0, 0, new_date)
                                
                                cursor.execute(sql, val)
                                db.commit() 
                                
                                msg = "The attack has started."
                                return msg
                            else:
                                msg = "You can not attack your own kingdom."
                                return msg
                        else:
                            msg = "This region is already under attack."
                            return msg
                    else:
                        msg = "You are not the king of this kingdom."
                        return msg
                else:
                    msg = "You did not join the game yet."
                    return msg
            else:
                msg = "A region with this name does not exists on this server."
                return msg
        else:                            
            msg = "There is no kingdom with this name on this server."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def change_location(server_id, region_name, user_id):
    if game_started(server_id):   
        if region_exists(server_id, region_name):                    
            if user_exists(server_id, user_id):
                citizen_id = get_citizen_id(server_id, user_id)
                
                query = "SELECT citizen.moved FROM citizen WHERE id = '%s'" % (citizen_id)
                df = pd.read_sql(query, db)
                
                moved = df['moved'].iloc[0]
                moved = str(moved)
                
                if compare_date(moved):
                    new_date = add_sub_hours(1)
                    region_id = get_region_id(server_id, region_name)
                    
                    sql = "UPDATE citizen SET citizen.location = '%s', citizen.moved = '%s' WHERE citizen.id = '%s'" % (region_id, new_date, citizen_id)
                    cursor.execute(sql)
                    db.commit()
                    
                    msg = "You successfully moved."
                    return msg
                else:
                    msg = "You can only move once every hour."
                    return msg
            else:
                msg = "You do not participate in this game yet."
                return msg
        else:
                msg = "This region does not exist on this server."
                return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def attack(server_id, region_name, user_id, amount):
    if game_started(server_id):   
        if region_exists(server_id, region_name):                    
            if user_exists(server_id, user_id):
                citizen_id = get_citizen_id(server_id, user_id)
                region_id = get_region_id(server_id, region_name)
                
                if battle_exists(region_id):
                    battle_id = get_battle_id(region_id)
                    
                    query = "SELECT attack.attacker_strength, attack.started FROM attack WHERE id = '%s'" % (battle_id)
                    df = pd.read_sql(query, db)
                    
                    attacker_strength = df['attacker_strength'].iloc[0]
                    attacker_strength = int(attacker_strength)
                    
                    started = df['started'].iloc[0]
                    started = str(started)
                    
                    query = "SELECT citizen.strength, citizen.location FROM citizen WHERE id = '%s'" % (citizen_id)
                    df = pd.read_sql(query, db)
                    
                    strength = df['strength'].iloc[0]
                    strength = int(strength)
                    
                    location = df['location'].iloc[0]
                    location = int(location)
                    
                    if location == region_id:
                        if compare_date(started):
                            msg = end_battle(battle_id)
                            return msg
                        else:
                           attacker_strength = attacker_strength + amount
                           strength = strength - amount
                            
                           if strength >= 0:
                               sql = "UPDATE attack SET attack.attacker_strength = '%s' WHERE attack.id = '%s'" % (attacker_strength, battle_id)
                               cursor.execute(sql)
                               db.commit()
                                
                               sql = "UPDATE citizen SET citizen.strength = '%s' WHERE citizen.id = '%s'" % (strength, citizen_id)
                               cursor.execute(sql)
                               db.commit()
                                
                               msg = "You successfully attacked the region."
                               return msg 
                           else:
                               msg = "You do not have enough strength"
                               return msg 
                    else:
                        msg = "You are not in the region you want to attack."
                        return msg 
                else:
                    msg = "There is no ongoing battle in his region."
                    return msg
            else:
                msg = "You do not participate in this game yet."
                return msg
        else:
                msg = "This region does not exist on this server."
                return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def defend(server_id, region_name, user_id, amount):
    if game_started(server_id):   
        if region_exists(server_id, region_name):                    
            if user_exists(server_id, user_id):
                citizen_id = get_citizen_id(server_id, user_id)
                region_id = get_region_id(server_id, region_name)
                
                if battle_exists(region_id):
                    battle_id = get_battle_id(region_id)
                    
                    query = "SELECT attack.defender_strength, attack.started FROM attack WHERE id = '%s'" % (battle_id)
                    df = pd.read_sql(query, db)
                    
                    defender_strength = df['defender_strength'].iloc[0]
                    defender_strength = int(defender_strength)
                    
                    started = df['started'].iloc[0]
                    started = str(started)
                    
                    query = "SELECT citizen.strength, citizen.location FROM citizen WHERE id = '%s'" % (citizen_id)
                    df = pd.read_sql(query, db)
                    
                    strength = df['strength'].iloc[0]
                    strength = int(strength)
                    
                    location = df['location'].iloc[0]
                    location = int(location)
                    
                    if location == region_id:
                        if compare_date(started):
                            msg = end_battle(battle_id)
                            return msg
                        else:
                            defender_strength = defender_strength + amount
                            strength = strength - amount
                            
                            if strength >= 0:
                                sql = "UPDATE attack SET attack.defender_strength = '%s' WHERE attack.id = '%s'" % (defender_strength, battle_id)
                                cursor.execute(sql)
                                db.commit()
                                
                                sql = "UPDATE citizen SET citizen.strength = '%s' WHERE citizen.id = '%s'" % (strength, citizen_id)
                                cursor.execute(sql)
                                db.commit()
                                
                                msg = "You successfully defended the region."
                                return msg 
                            else:
                                msg = "You do not have enough strength"
                                return msg 
                    else:
                        msg = "You are not in the region you want to defend."
                        return msg 
                else:
                    msg = "There is no ongoing battle in his region."
                    return msg
            else:
                msg = "You do not participate in this game yet."
                return msg
        else:
                msg = "This region does not exist on this server."
                return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def use_workpower(server_id, region_name, kingdom_name, user_id, amount):
    if game_started(server_id):   
        if kingdom_exists(server_id, kingdom_name):
            if region_exists(server_id, region_name):                    
                if user_exists(server_id, user_id):
                    kingdom_id = get_kingdom_id(server_id, kingdom_name)
                    region_id = get_region_id(server_id, region_name)
                    
                    if user_is_king(kingdom_id, user_id):
                        
                        if battle_exists(region_id):
                            battle_id = get_battle_id(region_id)
                            
                            query = "SELECT attack.attacker_strength, defender_strength, attack.started, attack.attacker_kingdom, attack.defender_kingdom FROM attack WHERE id = '%s'" % (battle_id)
                            df = pd.read_sql(query, db)
                            
                            attacker_strength = df['attacker_strength'].iloc[0]
                            attacker_strength = int(attacker_strength)
                            
                            defender_strength = df['defender_strength'].iloc[0]
                            defender_strength = int(defender_strength)
                            
                            started = df['started'].iloc[0]
                            started = str(started)
                            
                            attacker_kingdom = df['attacker_kingdom'].iloc[0]
                            attacker_kingdom = int(attacker_kingdom)
                            
                            defender_kingdom = df['defender_kingdom'].iloc[0]
                            defender_kingdom = int(defender_kingdom)
                            
                            query = "SELECT kingdom.workpower FROM kingdom WHERE id = '%s'" % (kingdom_id)
                            df = pd.read_sql(query, db)
                            
                            workpower = df['workpower'].iloc[0]
                            workpower = int(workpower)
                            
                            if kingdom_id == attacker_kingdom:
                                if compare_date(started):
                                    msg = end_battle(battle_id)
                                    return msg
                                else:
                                   attacker_strength = attacker_strength + amount
                                   workpower = workpower - amount
                                    
                                   if workpower >= 0:
                                       sql = "UPDATE attack SET attack.attacker_strength = '%s' WHERE attack.id = '%s'" % (attacker_strength, battle_id)
                                       cursor.execute(sql)
                                       db.commit()
                                        
                                       sql = "UPDATE kingdom SET kingdom.workpower = '%s' WHERE kingdom.id = '%s'" % (workpower, kingdom_id)
                                       cursor.execute(sql)
                                       db.commit()
                                        
                                       msg = "You successfully attacked the region."
                                       return msg 
                                   else:
                                       msg = "The kingdom does not have enough workpower"
                                       return msg 
                            else:
                                if compare_date(started):
                                    msg = end_battle(battle_id)
                                    return msg
                                else:
                                   defender_strength = defender_strength + amount
                                   workpower = workpower - amount
                                    
                                   if workpower >= 0:
                                       sql = "UPDATE attack SET attack.defender_strength = '%s' WHERE attack.id = '%s'" % (defender_strength, battle_id)
                                       cursor.execute(sql)
                                       db.commit()
                                        
                                       sql = "UPDATE kingdom SET kingdom.workpower = '%s' WHERE kingdom.id = '%s'" % (workpower, kingdom_id)
                                       cursor.execute(sql)
                                       db.commit()
                                        
                                       msg = "You successfully defended the region."
                                       return msg 
                                   else:
                                       msg = "The kingdom does not have enough workpower"
                                       return msg 
                        else:
                            msg = "There is no ongoing battle in his region."
                            return msg
                    else:
                        msg = "You are not the king of this kingdom."
                        return msg
                else:
                    msg = "You do not participate in this game yet."
                    return msg
            else:
                    msg = "This region does not exist on this server."
                    return msg
        else:
                msg = "This kingdom does not exist on this server."
                return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def profile(server_id, user_id, user_profile_id, user_profile_name):
    if game_started(server_id):                     
        if user_exists(server_id, user_id):
            citizen_id = get_citizen_id(server_id, user_id)
            
            query = "SELECT citizen.location, citizen.strength, citizen.kingdom_id, citizen.currency FROM citizen WHERE id = '%s'" % (citizen_id)
            df = pd.read_sql(query, db)
            
            location_id= df['location'].iloc[0]
            location_id = int(location_id)
            
            strength = df['strength'].iloc[0]
            strength = str(strength)
        
            kingdom_id = df['kingdom_id'].iloc[0]
            kingdom_id = int(kingdom_id)
            
            currency = df['currency'].iloc[0]
            currency = round(float(currency), 3)
            
            query = "SELECT kingdom.name FROM kingdom WHERE id = '%s'" % (kingdom_id)
            df = pd.read_sql(query, db)
            
            kingdom_name = df['name'].iloc[0]
            kingdom_name = str(kingdom_name)
            
            query = "SELECT region.name FROM region WHERE id = '%s'" % (location_id)
            df = pd.read_sql(query, db)
            
            region_name = df['name'].iloc[0]
            region_name = str(region_name)
            
            msg = "User: " + user_profile_name + ", strength: " + strength + ", kingdom: " + kingdom_name + ", location: " + region_name + ", currency: " + str(currency)
            return msg
        else:
            msg = "This user does not participate in this game yet."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def kingdom_info(server_id, kingdom_name, king_name, user_id):
    if game_started(server_id):  
        if kingdom_exists(server_id, kingdom_name): 
            kingdom_id = get_kingdom_id(server_id, kingdom_name)              
            
            query = "SELECT kingdom.king_id, kingdom.workpower FROM kingdom WHERE id = '%s'" % (kingdom_id)
            df = pd.read_sql(query, db)
            
            king_id= df['king_id'].iloc[0]
            if king_id != None:
                king_id = int(king_id)
            
            workpower = df['workpower'].iloc[0]
            workpower = str(workpower)
            
            query = "SELECT kingdom.name FROM kingdom WHERE id = '%s'" % (kingdom_id)
            df = pd.read_sql(query, db)
            
            kingdom_name = df['name'].iloc[0]
            kingdom_name = str(kingdom_name)
            
            query = "SELECT region.name FROM region WHERE kingdom_id = '%s'" % (kingdom_id)
            df = pd.read_sql(query, db)
            
            df_list = df.values.tolist()
            
            msg = "Kingdom: " + kingdom_name + ", king: " + king_name + ", workpower: " + workpower + ", regions: "
            for item in df_list:
                msg = msg + str(item).strip('[]') + ", "
            return msg
        else:
            msg = "This kingdom does not exist."
            return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def kingdom_list(server_id, user_id):
    if game_started(server_id):  
        query = "SELECT kingdom.name FROM kingdom INNER JOIN game ON kingdom.game_id = game.id WHERE server_id = '%s'" % (server_id)
        df = pd.read_sql(query, db)
        
        df_list = df.values.tolist()
        
        msg = "Kingdoms: "
        for item in df_list:
            msg = msg + str(item).strip('[]') + ", "
        return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def region_list(server_id, user_id):
    if game_started(server_id):  
        query = "SELECT region.name FROM region INNER JOIN kingdom ON region.kingdom_id = kingdom.id INNER JOIN game ON kingdom.game_id = game.id WHERE server_id = '%s'" % (server_id)
        df = pd.read_sql(query, db)
        
        df_list = df.values.tolist()
        
        msg = "Regions: "
        for item in df_list:
            msg = msg + str(item).strip('[]') + ", "
        return msg
    else:
        msg = "No game has been started on this server."
        return msg

def status_battle(server_id, region_name, user_id):
    if game_started(server_id):   
        if region_exists(server_id, region_name):                    
            region_id = get_region_id(server_id, region_name)
            
            if battle_exists(region_id):
                battle_id = get_battle_id(region_id)
                
                query = "SELECT attack.attacker_strength, defender_strength, attack.started, attack.attacker_kingdom, attack.defender_kingdom FROM attack WHERE id = '%s'" % (battle_id)
                df = pd.read_sql(query, db)
                
                attacker_strength = df['attacker_strength'].iloc[0]
                attacker_strength = str(attacker_strength)
                
                defender_strength = df['defender_strength'].iloc[0]
                defender_strength = str(defender_strength)
                
                started = df['started'].iloc[0]
                started = str(started)
                
                attacker_kingdom = df['attacker_kingdom'].iloc[0]
                attacker_kingdom = int(attacker_kingdom)
                
                defender_kingdom = df['defender_kingdom'].iloc[0]
                defender_kingdom = int(defender_kingdom)
                
                query = "SELECT kingdom.name FROM kingdom WHERE id = '%s'" % (attacker_kingdom)
                df = pd.read_sql(query, db)
                
                attacker_kingdom_name = df['name'].iloc[0]
                attacker_kingdom_name = str(attacker_kingdom_name)
                
                query = "SELECT kingdom.name FROM kingdom WHERE id = '%s'" % (defender_kingdom)
                df = pd.read_sql(query, db)
                
                defender_kingdom_name = df['name'].iloc[0]
                defender_kingdom_name = str(defender_kingdom_name)
                
                time_left = str(time_diff(started))
                
                msg_ext = " "
                if compare_date(started):
                    msg_ext = end_battle(battle_id)
                
                msg = "Battle for: " + region_name + ", attacking kingdom: " + attacker_kingdom_name + ", damage dealt: " + attacker_strength + ", defending kingdom: " + defender_kingdom_name + ", damage dealt: " + defender_strength + ", time left: " + time_left + msg_ext
                return msg
            else:
                msg = "There is no ongoing battle in his region."
                return msg
        else:
                msg = "This region does not exist on this server."
                return msg
    else:
        msg = "No game has been started on this server."
        return msg
    
def read_stockmarket():
    stock_list = []
    try:
        with open("../stock_market/output.txt") as f:
            for jsonObj in f:
                stockdict = json.loads(jsonObj)
                stock_list.append(stockdict)
    except:
        pass
    
    return stock_list

def show_stocks(server_id):
    if game_started(server_id): 
        stock_list = read_stockmarket()
        msg = "```"
        for stock_index, stock in enumerate(stock_list):  
            stock_name = stock.get('stock_name')
            value_scaler = stock.get('value_scaler')
            current_price = stock.get('current_price') / value_scaler
            msg = msg + str(stock_name) + ", price: " + str(current_price) + "\n"
        msg = msg + "```"
        return msg
    else:
        msg = "No game has been started on this server."
        return msg

def show_wallet(server_id, user_id, user_name):
    if game_started(server_id):  
        if user_exists(server_id, user_id):
            citizen_id = get_citizen_id(server_id, user_id)
            
            query = "SELECT stock.* FROM stock WHERE citizen_id = '%s'" % (citizen_id)
            df = pd.read_sql(query, db)
        
            index = df.index
            count = len(index)
            
            if count > 0:
                msg = "```"
                msg = msg + str(user_name) + " owns: \n"
                for index, row in df.iterrows():
                    msg = msg + str(row['stock_name']) + ", amount: " + str(row['amount']) + "\n"
                msg = msg + "```"
                return msg
            else:
                msg = "This user does not own any stocks."
                return msg
        else:
            msg = "You are not participating in this game."
            return msg   
    else:
        msg = "No game has been started on this server."
        return msg
    
def buy_stocks(server_id, user_id, buy_stock_name, amount):
    if game_started(server_id):  
        if user_exists(server_id, user_id):
            citizen_id = get_citizen_id(server_id, user_id)
            stock_list = read_stockmarket()
            
            query = "SELECT citizen.currency FROM citizen WHERE citizen.id = '%s'" % (citizen_id)
            df = pd.read_sql(query, db)
            currency = df['currency'].iloc[0]
            
            msg = "This stock does not exist."
            for stock_index, stock in enumerate(stock_list):  
                stock_name = stock.get('stock_name')
                value_scaler = stock.get('value_scaler')
                current_price = stock.get('current_price') / value_scaler
                
                if buy_stock_name == stock_name:
                    currency = currency - (amount * current_price) - 0.5 - (amount * 0.01)
                    if currency >= 0:
                        query2 = "SELECT stock.id, stock.amount FROM stock WHERE citizen_id = '%s' and stock_name = '%s'" % (citizen_id, stock_name)
                        df2 = pd.read_sql(query2, db)
                        
                        index = df2.index
                        count = len(index)
                        
                        if count > 0:
                            stock_id = df2['id'].iloc[0]
                            stock_amount = df2['amount'].iloc[0]
                            
                            stock_amount = stock_amount + amount
                            
                            sql = "UPDATE stock SET stock.amount = '%s' WHERE stock.id = '%s'" % (stock_amount, stock_id)
                            cursor.execute(sql)
                            db.commit()
                            
                            sql = "UPDATE citizen SET citizen.currency = '%s' WHERE citizen.id = '%s'" % (currency, citizen_id)
                            cursor.execute(sql)
                            db.commit()
                            
                            msg = "You purchased the stocks."
                            return msg
                        else:
                            sql = "INSERT INTO stock (citizen_id, stock_name, amount) VALUES (%s, %s, %s)"
                            val = (citizen_id, stock_name, amount)
                            
                            cursor.execute(sql, val)
                            db.commit()  
                            
                            sql = "UPDATE citizen SET citizen.currency = '%s' WHERE citizen.id = '%s'" % (currency, citizen_id)
                            cursor.execute(sql)
                            db.commit()
                            
                            msg = "You purchased the stocks."
                            return msg
                    else:
                        msg = "You do not have enough currency."
                        return msg
        else:
            msg = "You are not participating in this game."
            return msg   
    else:
        msg = "No game has been started on this server."
        return msg
    return msg
    
def sell_stocks(server_id, user_id, sell_stock_name, amount):
    if game_started(server_id):  
        if user_exists(server_id, user_id):
            citizen_id = get_citizen_id(server_id, user_id)
            stock_list = read_stockmarket()
            
            query = "SELECT citizen.currency FROM citizen WHERE citizen.id = '%s'" % (citizen_id)
            df = pd.read_sql(query, db)
            currency = df['currency'].iloc[0]
            
            msg = "This stock does not exist."
            for stock_index, stock in enumerate(stock_list):  
                stock_name = stock.get('stock_name')
                value_scaler = stock.get('value_scaler')
                current_price = stock.get('current_price') / value_scaler
                
                if sell_stock_name == stock_name:
                    currency = currency + (amount * current_price) - 0.5 - (amount * 0.01)
                    if currency >= 0:
                        query2 = "SELECT stock.id, stock.amount FROM stock WHERE citizen_id = '%s' and stock_name = '%s'" % (citizen_id, stock_name)
                        df2 = pd.read_sql(query2, db)
                        
                        index = df2.index
                        count = len(index)
                        
                        if count > 0:
                            stock_id = df2['id'].iloc[0]
                            stock_amount = df2['amount'].iloc[0]
                            
                            stock_amount = stock_amount - amount
                            
                            if stock_amount >= 0:
                                sql = "UPDATE stock SET stock.amount = '%s' WHERE stock.id = '%s'" % (stock_amount, stock_id)
                                cursor.execute(sql)
                                db.commit()
                                
                                sql = "UPDATE citizen SET citizen.currency = '%s' WHERE citizen.id = '%s'" % (currency, citizen_id)
                                cursor.execute(sql)
                                db.commit()
                                
                                msg = "You sold the stocks."
                                return msg
                            else:
                                msg = "You do not have enough stocks in your wallet."
                        else:
                            msg = "You do not own this stock."
                            return msg
                    else:
                        msg = "You do not have enough currency."
                        return msg
        else:
            msg = "You are not participating in this game."
            return msg   
    else:
        msg = "No game has been started on this server."
        return msg
    return msg

def buy_strength(server_id, user_id, amount):
    if game_started(server_id):  
        if user_exists(server_id, user_id):
            citizen_id = get_citizen_id(server_id, user_id)
            
            query = "SELECT citizen.currency, citizen.strength FROM citizen WHERE citizen.id = '%s'" % (citizen_id)
            df = pd.read_sql(query, db)
            currency = df['currency'].iloc[0]
            strength = df['strength'].iloc[0]
            
            currency = currency - amount * 0.1
            strength = strength + amount
            if currency >= 0:
                sql = "UPDATE citizen SET citizen.currency = '%s', citizen.strength = '%s' WHERE citizen.id = '%s'" % (currency, strength, citizen_id)
                cursor.execute(sql)
                db.commit()
                
                msg = "You succesfully bought strength."
                return msg
            else:
                msg = "You do not have enough currency."
                return msg
        else:
            msg = "You are not participating in this game."
            return msg   
    else:
        msg = "No game has been started on this server."
        return msg
    
def leave_game(server_id, user_id):
    if game_started(server_id):  
        if user_exists(server_id, user_id):
            citizen_id = get_citizen_id(server_id, user_id)
            
            sql = "DELETE from citizen WHERE citizen.id = '%s'" % (citizen_id)
            cursor.execute(sql)
            db.commit()
            
            msg = "The attacker won the battle."
            return msg
        else:
            msg = "You are not participating in this game."
            return msg   
    else:
        msg = "No game has been started on this server."
        return msg
    
def get_stat():
    msg = "```"
    
    query = "SELECT game.id FROM game"
    df = pd.read_sql(query, db)
    index = df.index
    count = len(index)
    msg = msg + "number of games: " + str(count) + "\n"
    
    query = "SELECT kingdom.id FROM kingdom"
    df = pd.read_sql(query, db)
    index = df.index
    count = len(index)
    msg = msg + "number of kingdoms: " + str(count) + "\n"
    
    query = "SELECT region.id FROM region"
    df = pd.read_sql(query, db)
    index = df.index
    count = len(index)
    msg = msg + "number of regions: " + str(count) + "\n"
    
    query = "SELECT citizen.id FROM citizen"
    df = pd.read_sql(query, db)
    index = df.index
    count = len(index)
    msg = msg + "number of citizens: " + str(count) + "\n"
    
    msg = msg + "```"
    return msg
        
def help():
    msg = "```"
    
    msg = msg + "All commands start with -dck, arguments are separated by a whitespace: -dck set_admin @user \n"
    
    msg = msg + "\n"
    msg = msg + "**By using this bot users agree that their discord user_id will be stored while the game is running. Users may leave the game at any time by using the leave_game command** \n"
    
    msg = msg + "\n"
    msg = msg + "**Admin commands:** \n"
    msg = msg + " start_game \n end_game \n create_kingdom kingdomname \n create_region kingdomname regionname \n set_admin @user \n demote_admin @user \n set_king kingdomname @user \n"
    
    msg = msg + "\n"
    msg = msg + "**King commands:** \n"
    msg = msg + " attack_region kingdomname regionname \n use_workpower kingdomname regionname amount \n"
    
    msg = msg + "\n"
    msg = msg + "**Citizen commands:** \n"
    msg = msg + " join_kingdom kingdomname regionname \n train \n work \n change_location regionname \n attack regionname amount \n defend regionname amount \n buy_stocks company_name amount \n sell_stocks company_name amount \n leave_game \n"

    msg = msg + "\n"
    msg = msg + "**General commands:** \n"
    msg = msg + " profile @user \n kingdom kingdomname \n kingdom_list \n region_list \n status_battle regionname \n show_stocks \n show_wallet @user \n quote \n github \n help"
    
    msg = msg + "```"
    return msg

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.channel.type.name != discord.ChannelType.text.name:
        return

    if message.content.startswith('-dck'):
        message_content = message.content.split(" ")
        server_id = message.channel.id
        server_id = str(server_id)
        author_id = message.author.id
        author_id = str(author_id)
        
        if len(message_content) == 0:
            return
        
        #update game
        if game_started(server_id):
            update_game(server_id)
        
        #owner/admin commands
        if message_content[1] == "start_game":
            botreply = start_game(server_id, author_id)
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "end_game":
            botreply = end_game(server_id, author_id)
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "create_kingdom" and len(message_content) == 3:
            kingdom_name = message_content[2]
            kingdom_name = db.escape_string(kingdom_name)
            botreply = create_kingdom(server_id, author_id, kingdom_name)
            await message.channel.send(botreply)
            return
            
        if message_content[1] == "create_region" and len(message_content) == 4:
            kingdom_name = message_content[2]
            kingdom_name = db.escape_string(kingdom_name)
            region_name = message_content[3]
            region_name = db.escape_string(region_name)
            botreply = create_region(server_id, author_id, kingdom_name, region_name)
            await message.channel.send(botreply)
            return
            
        if message_content[1] == "set_admin" and len(message_content) == 3:
            try:
                mention_id = message.mentions[0]
                new_admin_id = str(mention_id.id)
                botreply = set_admin(server_id, author_id, new_admin_id)
                await message.channel.send(botreply)
            except IndexError:
                return
            
            return
            
        if message_content[1] == "demote_admin" and len(message_content) == 3:
            try:
                mention_id = message.mentions[0]
                new_admin_id = str(mention_id.id)
                botreply = demote_admin(server_id, author_id, new_admin_id)
                await message.channel.send(botreply)
            except IndexError:
                return
            
            return
            
        if message_content[1] == "set_king" and len(message_content) == 4:
            try:
                kingdom_name = message_content[2]
                kingdom_name = db.escape_string(kingdom_name)
                mention_id = message.mentions[0]
                new_king_id = str(mention_id.id)
                botreply = set_king(server_id, author_id, kingdom_name, new_king_id)
                await message.channel.send(botreply)
            except IndexError:
                return
            
            return
        
        #king commands
        if message_content[1] == "attack_region" and len(message_content) == 4:
            kingdom_name = message_content[2]
            kingdom_name = db.escape_string(kingdom_name)
            region_name = message_content[3]
            region_name = db.escape_string(region_name)
            botreply = attack_region(server_id, author_id, kingdom_name, region_name)
            await message.channel.send(botreply)
            return
        
        #king commands
        if message_content[1] == "use_workpower" and len(message_content) == 5:
            kingdom_name = message_content[2]
            kingdom_name = db.escape_string(kingdom_name)
            region_name = message_content[3]
            region_name = db.escape_string(region_name)
            amount = message_content[4]
            amount = db.escape_string(amount)
            
            try: 
                amount = int(amount)
                botreply = use_workpower(server_id, region_name, kingdom_name, author_id, amount)
                await message.channel.send(botreply)
                
            except ValueError:
                return
            
            return
            
        #citizen commands
        if message_content[1] == "join_kingdom" and len(message_content) == 4:
            kingdom_name = message_content[2]
            kingdom_name = db.escape_string(kingdom_name)
            region_name = message_content[3]
            region_name = db.escape_string(region_name)
            botreply = join_kingdom(server_id, author_id, kingdom_name, region_name)
            await message.channel.send(botreply)
            return
            
        if message_content[1] == "train":
            botreply = train(server_id, author_id)
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "work":
            botreply = work(server_id, author_id)
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "change_location" and len(message_content) == 3:
            region_name = message_content[2]
            region_name = db.escape_string(region_name)
            botreply = change_location(server_id, region_name, author_id)
            await message.channel.send(botreply)
            return
            
        if message_content[1] == "attack" and len(message_content) == 4:
            region_name = message_content[2]
            region_name = db.escape_string(region_name)
            amount = message_content[3]
            amount = db.escape_string(amount)
            
            try: 
                amount = int(amount)
                botreply = attack(server_id, region_name, author_id, amount)
                await message.channel.send(botreply)
                
            except ValueError:
                return
            
            return
        
        if message_content[1] == "defend" and len(message_content) == 4:
            region_name = message_content[2]
            region_name = db.escape_string(region_name)
            amount = message_content[3]
            amount = db.escape_string(amount)
            
            try: 
                amount = int(amount)
                botreply = defend(server_id, region_name, author_id, amount)
                await message.channel.send(botreply)
                
            except ValueError:
                return
            
            return
        
        if message_content[1] == "profile":            
            try:
                mention_id = message.mentions[0]
                user_profile_id = str(mention_id.id)
                user_profile_name = str(mention_id.name)
                botreply = profile(server_id, author_id, user_profile_id, user_profile_name)
                await message.channel.send(botreply)
            except IndexError:
                return
            
            return
        
        if message_content[1] == "show_stocks":            
            try:
                botreply = show_stocks(server_id)
                await message.channel.send(botreply)
            except IndexError:
                return
            
            return
        
        if message_content[1] == "show_wallet":            
            try:
                mention_id = message.mentions[0]
                user_profile_id = str(mention_id.id)
                user_profile_name = str(mention_id.name)
                botreply = show_wallet(server_id, user_profile_id, user_profile_name)
                await message.channel.send(botreply)
            except IndexError:
                return
            
            return
        
        if message_content[1] == "buy_stocks" and len(message_content) == 4:
            buy_stock_name = message_content[2]
            buy_stock_name = db.escape_string(buy_stock_name)
            amount = message_content[3]
            amount = db.escape_string(amount)
            
            try: 
                amount = int(amount)
                botreply = buy_stocks(server_id, author_id, buy_stock_name, amount)
                await message.channel.send(botreply)
                
            except ValueError:
                return
            
            return
        
        if message_content[1] == "sell_stocks" and len(message_content) == 4:
            buy_stock_name = message_content[2]
            buy_stock_name = db.escape_string(buy_stock_name)
            amount = message_content[3]
            amount = db.escape_string(amount)
            
            try: 
                amount = int(amount)
                botreply = sell_stocks(server_id, author_id, buy_stock_name, amount)
                await message.channel.send(botreply)
                
            except ValueError:
                return
            
            return
        
        if message_content[1] == "buy_strength" and len(message_content) == 3:
            amount = message_content[2]
            amount = db.escape_string(amount)
            
            try: 
                amount = int(amount)
                botreply = buy_strength(server_id, author_id, amount)
                await message.channel.send(botreply)
                
            except ValueError:
                return
            
            return
        
        if message_content[1] == "kingdom" and len(message_content) == 3:
            kingdom_name = message_content[2]
            kingdom_name = db.escape_string(kingdom_name)
            
            king_id = get_king_id(server_id, kingdom_name, author_id)
            
            if king_id != None:
                member = client.get_user(king_id)
                
                if member != None:
                    king_name = member.name
                else:
                    king_name = "None"
            else:
                king_name = "None"
                
            botreply = kingdom_info(server_id, kingdom_name, king_name, author_id)
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "kingdom_list":
            botreply = kingdom_list(server_id, author_id)
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "region_list" and len(message_content) == 2:
            botreply = region_list(server_id, author_id)
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "status_battle" and len(message_content) == 3:
            region_name = message_content[2]
            region_name = db.escape_string(region_name)
            
            botreply = status_battle(server_id, region_name, author_id)
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "leave_game":
            botreply = leave_game(server_id, author_id)
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "help":
            botreply = help()
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "github":
            botreply = "https://github.com/lwaw/dckingdoms"
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "quote":
            botreply = get_quote()
            await message.channel.send(botreply)
            return
        
        if message_content[1] == "stat":
            botreply = get_stat()
            await message.channel.send(botreply)
            return

client.run('')
#client.run('')#testbot

