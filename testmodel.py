# dove facciamo le prove del grafo

from model.model import Model
from model.fermata import Fermata

model=Model()
#proviamo a stampare nodi e archi prima di aver costrito (riempito) il grafo
print("Numero nodi:", model.get_numnodi())
print("Numero archi:", model.get_numarchi())
# e dopo
model.buildGraph()
print("Numero nodi:", model.get_numnodi())
print("Numero archi:", model.get_numarchi())

source = Fermata(2, "Abbesses", 2.33855, 48.8843)

# il contenuto e la lunghezza sarà uguale, ma l'ordine diverso perchè l'esplorazione è diversa
nodiBFS = model.getBFSNodesFromEdges(source)
print(len(nodiBFS))
for i in range(0,10): #stampo solo i primi dieci perchè la lista è lunga
    print(nodiBFS[i])

nodiDFS = model.getDFSNodesFromEdges(source)
print(len(nodiDFS))
for i in range(0,10):
    print(nodiDFS[i])



model.buildGraphPesato()
print("===========================================")

print("Archi con peso 2")
archiMaggiori = model.getArchiPesoMaggiore()
for a in archiMaggiori:
    print(a[0], "->", a[1], ":", a[2]["weight"])