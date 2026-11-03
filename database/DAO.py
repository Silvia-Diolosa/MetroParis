from Grafi.metro_paris.model.fermata import Fermata
from database.DB_connect import DBConnect
#from model.fermata import Fermata

from model.connessione import Connesione


class DAO():

    @staticmethod
    def getAllFermate():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM fermata"
        cursor.execute(query)

        for row in cursor:
            result.append(Fermata(**row))
        cursor.close()
        conn.close()
        return result

    @staticmethod # verifichiamo se tra due fermate esiste una connessione, quindi un arco
    def hasconn(u: Fermata, v: Fermata):
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = ("select * "
                 "from connessione c "
                 "where c.id_stazP = %s "
                 "and c.id_stazA = %s")
        cursor.execute(query, (u.id_fermata, v.id_fermata))

        for row in cursor: # cursor contiene tutte le connessioni trovate per quelle stazioni
            result.append(row) # non c'è bisogno creare oggetti di tipo connessione, mi interessa solo sapere se c'è connesione
        cursor.close()
        conn.close()
        return len(result) > 0 # se ha trovato connessioni, vuol dire che result contiene elementi

    @staticmethod
    def getvicini(u: Fermata):
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = ("select * "
                 "from connessione c "
                 "where c.id_stazP = %s")
        # tutte le connessioni dove la stazione di partenza è x, quindi così trovo tutti i vicini (i connessi) a stazione x
        cursor.execute(query, (u.id_fermata,))

        for row in cursor:
            result.append(Connesione(**row)) # restituisce connessioni trovate
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdges():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = ("SELECT * "
                 "FROM connessione c ") # tutte le connessioni
        cursor.execute(query)

        for row in cursor:
            result.append(Connesione(**row))
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdgesPesati():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT id_stazP , id_stazA , count(*) as peso
                       FROM connessione c
                       group by id_stazP , id_stazA  
                       order by peso desc"""
        # raggruppi per coppie (per tuple) dove ogni coppia ha stesso id_prtenza e arrivo
        # e conti quante volte una stessa coppia compare
        cursor.execute(query)

        for row in cursor:
            result.append((row["id_stazP"], row["id_stazA"], row["peso"]))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdgesVel():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """SELECT c.id_stazP , c.id_stazA , max(l.velocita) as v
                        FROM connessione c , linea l 
                        WHERE l.id_linea = c.id_linea 
                        group by c.id_stazP , c.id_stazA 
                        order by v asc"""

        # cioe: per ogni coppia di tupla trovata che ha stesso id_partenza e id_destionazione
        # (come sopra più coppie uguali, vuol dire che più linee fanno quella tratta)
        # selezioni la tupla che ha velocità massima, ovvero la linea più veloce che fa per "percorso" da lineaP a lineaA

        cursor.execute(query)

        for row in cursor:
            result.append((row["id_stazP"], row["id_stazA"], row["v"]))

        cursor.close()
        conn.close()
        return result

