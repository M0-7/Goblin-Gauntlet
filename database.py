import sqlite3

def parse():
    with open("./assets/Database/init.sql") as f:
        creation = f.read().split("\n")
    with open("./assets/Database/insert.sql") as f:
        insertion = f.read().split("\n")
    return creation, insertion 

class Database:
    def __init__(self):
        self.commit = False

    # Context manager creates the database if it doesn't exist when enteriing
    def __enter__(self):
        self.commit = False
        try:
            self.__connection = sqlite3.connect("./assets/Database/database.db")
            self.__cursor = self.__connection.cursor()
            #self.__createTable()
            return self
        except Exception as e:
            print(f"Error in creating the table. Error: {e}")

    # Closes the database when exiting
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.commit:
                self.__connection.commit()
            if self.__connection:
                self.__connection.close()
        except Exception as e:
            print(f"Error with the database. {e}")
    
    def getDamageEnemy(self, enemy):
        self.__cursor.execute(f"SELECT Damage FROM Enemies WHERE Animal = ?",(enemy,))
        result = self.__cursor.fetchone()
        return (result[0])
    
    def __createTable(self):
        # Creating tables
        creation,insertion = parse()
        for _ in creation:
            self.__cursor.execute(_)
        
        self.__connection.commit()
        
        # Inserting enemy damage
        try:
            for _ in insertion:
                self.__cursor.execute(_)
            self.__connection.commit()
        except sqlite3.IntegrityError:
            pass

        # Checking if there's ony one row
        self.__cursor.execute("SELECT COUNT(*) FROM Settings")
        row_count = self.__cursor.fetchone()[0]
        if row_count == 0:
            try:
                self.__cursor.execute("INSERT INTO Settings DEFAULT VALUES") # This is to ensure there's only one value in the character table
                self.__connection.commit()
            except sqlite3.IntegrityError:
                pass
    
    def getDamageTrap(self, trap):
        self.__cursor.execute(f"SELECT Damage FROM Traps WHERE Type = ?",(trap,))
        result = self.__cursor.fetchone()
        return (result[0])
    
    def updateCharacter(self, character):
        self.__cursor.execute(f"UPDATE Settings Set Character = ?;", (character,))
        self.commit = True

    def getCharacter(self):
        self.__cursor.execute("SELECT Character FROM Settings")
        result = self.__cursor.fetchone()
        return result[0]
    
    def updateNumberofEnemies(self,number):
        self.__cursor.execute(f"UPDATE Settings SET NumberEnemies = ?;",(number,))
        self.commit = True

    def getNumberofEnemies(self):
        self.__cursor.execute("SELECT NumberEnemies FROM Settings")
        result = self.__cursor.fetchone()
        return result[0]
    
    def getEffectsState(self):
        self.__cursor.execute("SELECT Effects FROM Settings")
        result = self.__cursor.fetchone()
        return result[0]
    
    def updateEffectsState(self,value):
        self.__cursor.execute(f"UPDATE Settings SET Effects = ?;",(value,))
        self.commit = True