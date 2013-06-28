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
	} limit 100000
	""")

print "Buscando as materias..."

materias = roda_query("""
	SELECT ?s
	FROM <http://semantica.globo.com/esportes/>
	WHERE {?s a <http://semantica.globo.com/esportes/MateriaEsporte>
	} limit 100 offset 0
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

lista_materias = []

for i in materias:
	# print i["s"]["value"], i["p"]["value"], i["o"]["value"]
	lista_materias.append(i["s"]["value"])

print "Calculando os paths..."

for i in range(len(lista_materias)):
	for j in range(i+1, len(lista_materias)):
		try:
			paths = list(nx.all_simple_paths(G, source=lista_materias[i], target=lista_materias[j], cutoff=4))
			# paths = nx.all_shortest_paths(G, source=lista_materias[i], target=lista_materias[j])
			if len(paths) > 0:
				print  lista_materias[i], len(paths),lista_materias[j]
				# for path in paths:
				# 	print path
				# 	# print "Tamanho path:", len(path)
		except NetworkXError:
			pass

print "Fim do processo"

if imagem_on:
	gera_imagem(G)
