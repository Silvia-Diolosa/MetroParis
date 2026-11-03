from database.DAO import DAO
import networkx as nx
import geopy.distance

def getPesoTempoPercorrenza(u, v, vel):
    dist = geopy.distance.distance((u.coordX, u.coordY),
                                   (v.coordX, v.coordY)).km  #poichè è in coordinate, con il metodo geopy convertiamo distanza in km
    time = dist / vel * 60 # minuti
    return time


class Model:
    def __init__(self):
        self._fermate = DAO.getAllFermate()
        self._grafo = nx.DiGraph() #variabile visibile a tutta e sola la classe, quindi la mettiamo nell'init (grafo semplice e orientato)
        self._idMapFermate = {} # dizionario che io interrogo (sotto) con uno dei valori della connessione (o fermata partenza o arrivo)
        # e mi ritorna il valore corrispondente della fermata (dato un id come chiave, ha come valore un oggetto fermata)
        for f in self._fermate:
            self._idMapFermate[f.id_fermata] = f
            # quindi lo inzializzo, ovvero per ogni fermata contenuta, crea dizionario chivae= id_fermata, valore= fermata


    def buildGraph(self): #costriamo il grafo (inizializzato a grafo vuoto in init)
        self._grafo.clear() #puliamo il grafo ad ogni chiamata
        self._grafo.add_nodes_from(self._fermate) #popolo il grafo con la lista di oggetti che sono le fermate (aggiungo i nodi che sono le fermate)
        self.addedges3() #chiamiamo la funzione che aggiunge gli archi


    # fare così è molto lungo e lento
    def addedges(self): # per aggiungere gli archi
        # due cicli for sulle fermate così che verifica tutte le possibili coppie di fermate
        # e vedere dal dao se esiste una connessione tra di loro. ed eventualmente aggiungere arco
        self._grafo.clear_edges()
        for u in self._fermate:
            for v in self._fermate:
                if DAO.hasconn(u, v):
                    self._grafo.add_edge(u, v)

    def addedges2(self):
        self._grafo.clear_edges()
        for u in self._fermate: # per ogni fermata vado a vedere i suoi vicini (vicini: tutti i nodi con il quale è connesso il nostro nodo considerato)
        #ovvero: per ogni fermata chiamo il metodo del dao, il quale mi restituisce le connessioni che quella stazione ha
        #ovvero, il dao tra le connessioni, seleziona tutte quelle che hanno la fermata considerata (come ad esempio stazione partenza)
        # quindi mi ritorna tutte le connessioni trovate per quella fermata
        # e per ogni connessione vado a prendere la fermata di arrivo e creo una connessione con la fermata di partenza che avevo
            for conn in DAO.getvicini(u):
                v = self._idMapFermate[conn.id_stazA] # dal dizionario che ha id fermata (chiave) e fermata (valore)
                                                # returna la fermata corrispondente (valore) alla chiave id
                self._grafo.add_edge(u, v)

    # per farla più veloce:
    def addedges3(self):
        self._grafo.clear_edges()
        alledges = DAO.getAllEdges() # semplicemente leggo tutte le connessioni dal dao
        for conn in alledges: # e per ciascuna connessione, leggo id partenza e id fermata (conn.id_staP e conn..id_stazA)
            u = self._idMapFermate[conn.id_stazP]  # aggiungo al dizionario la fermata corrispondente all'id partenza
            v = self._idMapFermate[conn.id_stazA]
            self._grafo.add_edge(u, v) # salvo la connessione
            #(p.s. add_edge è un metodo di grafo, oggetto = a nx.DiGraph() )

    # sono tutti metodi che leggono e restituiscono al controller. non voglio che il altri accedano direttamente al grafo, può solo model
    def get_numnodi(self): # funzione che ritorna il numero di nodi
        return len(self._grafo.nodes())

    def get_numarchi(self):# funzione che restituisce il numero di archi
        return len(self._grafo.edges())

    @property
    def fermate(self):
        return self._fermate





    def getBFSNodesFromEdges(self, source): # source è l'elemento da cui voglio partire, ovvero in questo caso la stazione
        archi = nx.bfs_edges(self._grafo, source) #creo archi bfs a partire da un grafo e da un punto di partenza
        nodiBFS = []
        for u, v in archi: # spacchetto la tupla in nodo di partenza u e di arrivo v
            nodiBFS.append(v) # appendo i nodi di arrivo
        return nodiBFS

    # stessa struttura di BFS ma usando DFS
    def getDFSNodesFromEdges(self, source):
        archi = nx.dfs_edges(self._grafo, source)
        nodiDFS = []
        for u, v in archi:
            nodiDFS.append(v)
        return nodiDFS

    # il contenuto e la lunghezza sarà uguale, ma l'ordine diverso perchè l'esplorazione è diversa

    #differenza tra BFS e DFS:
    # BFS: punto partenza ---> vado dai immediatamente vicini a lui (tutti i nodi direttamente a lui collegati) --->
    # ---> per ognuno di lor, a sua volta vado dai direttamente vicini a loro (quindi il secondo livello rispetto al punto partenza)
    # ---> finchè nessuno ha pià vicini

    # DFS: punto partenza (punto partenza è immediatamente vicino a punto x e y)
    # ---> scelgo un nodo immediatamente vicino a lui (es punto x) --> a sua volta scelgo un nodo immediatamente
    # vicino a lui (ovvero x) (quindi secondo vicino per punto partenza) ---> finchè non ha più nessun vicino
    # ---> a quel punto torno indietro e vado ad esempio al secondo vicino (ovvero punto y)
    # (prima avevo considerato solo un nodo immediatamente vicino, ma lui ne aveva vicini 2)
    # e continuo fino a che non sono stati tutti presi (però questo secondo vicino y magari era già stato considerato perchè vicino dei suoi successori)
    # in realtà torno indietro ricorsivamente, non direttamente al primo, dall'ultimo vado a quello prima di lui e vedo se ha altri vicini
    # e così via finche non arrivo al punto partenza, e valuto quindi se anche lui ha vicini


    # uguale a quelli sopra (ci restituiscono tutti e quattro la stessa cosa ma in maniera diversa)
    # rispetto a sopra qui cambia che ci viene restituito sotto forma di tree (albero) e sopra sotto forma di archi
    # ovvero:
    # EDGES
    # Quando usi le funzioni che terminano con _edges, NetworkX non ti restituisce un grafo o una struttura dati completa,
    # ma ti restituisce un generatore di tuple di archi (u, v)
    # Cosa contiene: Una sequenza di "passi" o "spostamenti" (es. ('Stazione A', 'Stazione B'), ('Stazione B', 'Stazione C'))
    # (infatti per creare la lista completa in fila, prendavamo ciclicamente soltanto l'ultimo elemento della tupla)
    # TREE
    # Quando usi le funzioni che terminano con _tree, NetworkX costruisce e ti restituisce un vero e proprio oggetto grafo (un sotto-grafo orientato)
    # che rappresenta l'albero di visita. Non è una semplice lista di coppie, ma un oggetto grafo a tutti gli effetti che possiede
    # già al suo interno tutti i nodi e tutti gli archi della visita. (quindi semplicemente estraiamo nodi e archi da tree)
    def getBFSNodesFromTree(self, source):
        tree = nx.bfs_tree(self._grafo, source)
        archi = list(tree.edges())
        nodi = list(tree.nodes())
        return nodi


    def getDFSNodesFromTree(self, source):
        tree = nx.dfs_tree(self._grafo, source)
        archi = list(tree.edges())
        nodi = list(tree.nodes())
        return nodi




    # GRAFO PESATO

    def buildGraphPesato(self):
        self._grafo.clear()
        self._grafo.add_nodes_from(self._fermate)
        # self.addEdgesPesati()
        self.addEdgesPesatiTempi()

    def addEdgesPesati(self):
        # riutilizzare il principio di funzionamento del metodo addEdges3,
        # ma contando quante volte provo ad aggiungere l'arco
        # (conto quante volte una connessione ha la stessa stazione partenza e la stessa arrivo)
        self._grafo.clear_edges()
        alledges = DAO.getAllEdges()
        for conn in alledges:
            u = self._idMapFermate[conn.id_stazP]
            v = self._idMapFermate[conn.id_stazA]

            if self._grafo.has_edge(u, v):
                self._grafo[u][v]["weight"] += 1 # spiegato sotto
            else:
                self._grafo.add_edge(u, v, weight=1)
        # In NetworkX, un grafo si comporta in modo simile a un dizionario nidificato.
        # self._grafo[u] seleziona il nodo di partenza u e restituisce tutti i suoi vicini collegati.
        # [v]: Specificando il secondo nodo v, stiamo puntando direttamente all'arco specifico che collega u a v.
        # Questo restituisce un dizionario contenente tutti gli attributi associati a quell'arco (es. colore, distanza, peso, ecc.).
        # ["weight"]: Accede alla chiave specifica chiamata "weight" (che rappresenta il peso dell'arco).


    def addEdgesPesatiV2(self):
        # Delega il calcolo del peso alla query sql, per semplificarci la vita in python
        # (lì conto quante volte una connessione ha la stessa stazione partenza e la stessa arrivo)
        self._grafo.clear_edges()
        allEdgesWPeso = DAO.getAllEdgesPesati()
        # (id_stazP, id_stazA, peso)

        for e in allEdgesWPeso:
            u = self._idMapFermate[e[0]]  # la fermata che ha come id e[0]
            v = self._idMapFermate[e[1]]
            peso = e[2]

            self._grafo.add_edge(u, v, weight=peso)

    # usato in tstModel (prova)
    def getArchiPesoMaggiore(self):
        edges = self._grafo.edges(data=True) # con data = True salvo le connessioni con tutti gli attributi loro (tra cui peso)

        edgesMaggiori = []
        for e in edges:
            if self._grafo.get_edge_data(e[0], e[1])["weight"] > 1:
                # self._grafo[e[0]][e[1]]["weight"]
                edgesMaggiori.append(e)
        return edgesMaggiori



    def addEdgesPesatiTempi(self):
        """Questo metodo crea degli archi, in cui il peso è pari al tempo di percorrenza di quell'arco,
        ottenuto come rapporto fra la distanza fra due stazioni e la velocità di percorrenza"""
        self._grafo.clear_edges()
        allEdgesVel = DAO.getAllEdgesVel()
        for e in allEdgesVel:
            u = self._idMapFermate[e[0]]
            v = self._idMapFermate[e[1]]
            peso = getPesoTempoPercorrenza(u, v, e[2]) #calcolato con funzione esterna
            self._grafo.add_edge(u, v, weight=peso)


    def getShorterstPath(self, u, v):
        return nx.single_source_dijkstra(self._grafo, u, v)
    # ci restituisce tupla di: lunghezza, che è la somma dei pesi, e la successione dei nodi
    # calcola il cammino minimo (shortest path) tra due nodi specifici (u e v)