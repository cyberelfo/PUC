#!/usr/bin/env python
import networkx as nx
from networkx.exception import NetworkXError

def gera_imagem(G):
	import matplotlib.pyplot as plt
	nx.draw(G, with_labels=False)
	plt.savefig("path.png")

def roda_query(query):
	from SPARQLWrapper import SPARQLWrapper, JSON
	sparql = SPARQLWrapper("http://localhost:8890/sparql/")
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	return results["results"]["bindings"]

imagem_on = False

print "Buscando as triplas..."

sub = roda_query("""
	SELECT ?s ?p ?o
	FROM <http://semantica.globo.com/esportes/>
	WHERE {?s ?p ?o 
	filter (isURI(?o) && !isBlank(?o))
	filter (!isBlank(?s)) 
	filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
	filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
    filter not exists {?s a <http://semantica.globo.com/esportes/MateriaEsporte>}	
	} limit 70000
	""")

print "Carregando o grafo..."

G=nx.Graph()

for i in sub:
	# print i["s"]["value"], i["p"]["value"], i["o"]["value"]
	G.add_node(i["s"]["value"])
	G.add_node(i["o"]["value"])
	G.add_edge(i["s"]["value"],i["o"]["value"], uri=i["p"]["value"])

print("graph has %d nodes with %d edges"\
          %(nx.number_of_nodes(G),nx.number_of_edges(G)))
print(nx.number_connected_components(G),"connected components")

import pdb; pdb.set_trace()

print "Buscando as materias..."

materias = roda_query("""
	SELECT ?s ?p ?o
	FROM <http://semantica.globo.com/esportes/>
	WHERE {?s a <http://semantica.globo.com/esportes/MateriaEsporte>;
	       ?p ?o 
	filter (isURI(?o) && !isBlank(?o))
	filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
	filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
	} 
	limit 10 offset 0
	""")

materias_order = sorted(materias, key=lambda k: k['s']['value']) 

lista_materias = {}

old_value = ''

for i in materias_order:
	# print i["s"]["value"], i["p"]["value"], i["o"]["value"]
	if old_value != i["s"]["value"]:
		lista_materias[i["s"]["value"]] = [i["o"]["value"]]
		old_value = i["s"]["value"]
	else:
		lista_materias[i["s"]["value"]].append(i["o"]["value"])


print "Calculando os paths..."

for m1 in lista_materias.keys():
	cabeca = lista_materias[m1]
	del lista_materias[m1]
	for i1 in cabeca:
		for m2 in lista_materias.keys():
			for i2 in lista_materias[m2]:
				try:
					paths = list(nx.all_simple_paths(G, source=i1, target=i2, cutoff=4))
					if len(paths) > 0:
						t1 = 0
						t2 = 0
						t3 = 0
						t4 = 0
						for path in paths:
							if len(path) - 2 == 1:
								t1 += 1
							elif len(path) - 2 == 2:
								t2 += 1
							elif len(path) - 2 == 3:
								t3 += 1
							elif len(path) - 2 == 4:
								t4 += 1
						print i1, 't1:', t1,'t2:', t2,'t3:', t3,'t4:', t4, i2
				except NetworkXError:
					pass

print "Fim do processo"

if imagem_on:
	gera_imagem(G)
