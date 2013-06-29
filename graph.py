#!/usr/bin/env python
import networkx as nx
from networkx.exception import NetworkXError
import MySQLdb

imagem_on = False
nr_triplas = 1000000
nr_materias = 1000
super_node = 100
max_path = 3

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

print "Buscando as triplas Esportes..."

my_query = """
	SELECT ?s ?p ?o
	FROM <http://semantica.globo.com/esportes/>
	WHERE {?s ?p ?o 
	filter (isURI(?o) && !isBlank(?o))
	filter (!isBlank(?s)) 
	filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
	filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
    filter not exists {?s a <http://semantica.globo.com/esportes/MateriaEsporte>}	
    filter not exists {?s a <http://semantica.globo.com/esportes/GaleriaDeFotos>}	
    filter not exists {?s a <http://semantica.globo.com/esportes/Guia>}	
    filter not exists {?s a <http://semantica.globo.com/esportes/Foto>}	
    filter not exists {?s a <http://semantica.globo.com/base/Video>}	
    filter not exists {?s a <http://semantica.globo.com/base/ConteudoAtomico>}	
    filter not exists {?s a <http://semantica.globo.com/base/Materia>}	
    filter not exists {?s a <http://semantica.globo.com/base/ConteudoComposto>}	
    filter not exists {?s a <http://semantica.globo.com/base/Foto>}	
    filter not exists {?s a <http://semantica.globo.com/base/GaleriaDeFotos>}	
    	} limit %s
	""" % nr_triplas

sub = roda_query(my_query)

print "Carregando o grafo Esportes..."

G=nx.Graph()

for i in sub:
	# print i["s"]["value"], i["p"]["value"], i["o"]["value"]
	G.add_node(i["s"]["value"])
	G.add_node(i["o"]["value"])
	G.add_edge(i["s"]["value"],i["o"]["value"], uri=i["p"]["value"])

print("graph has %d nodes with %d edges"\
          %(nx.number_of_nodes(G),nx.number_of_edges(G)))
print(nx.number_connected_components(G),"connected components")

# paths = list(nx.all_simple_paths(G, source='http://semantica.globo.com/esportes/equipe/2661', target='http://semantica.globo.com/esportes/atleta/73862', cutoff=4))
# print paths

print "Buscando as triplas Base..."

my_query = """
	SELECT ?s ?p ?o
	FROM <http://semantica.globo.com/>
	WHERE {?s ?p ?o 
	filter (isURI(?o) && !isBlank(?o))
	filter (!isBlank(?s)) 
	filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
	filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
    filter not exists {?s a <http://semantica.globo.com/esportes/MateriaEsporte>}	
    filter not exists {?s a <http://semantica.globo.com/esportes/GaleriaDeFotos>}	
    filter not exists {?s a <http://semantica.globo.com/esportes/Guia>}	
    filter not exists {?s a <http://semantica.globo.com/esportes/Foto>}	
    filter not exists {?s a <http://semantica.globo.com/base/Video>}	
    filter not exists {?s a <http://semantica.globo.com/base/ConteudoAtomico>}	
    filter not exists {?s a <http://semantica.globo.com/base/Materia>}	
    filter not exists {?s a <http://semantica.globo.com/base/ConteudoComposto>}	
    filter not exists {?s a <http://semantica.globo.com/base/Foto>}	
    filter not exists {?s a <http://semantica.globo.com/base/GaleriaDeFotos>}	
    	} limit %s
	""" % nr_triplas

sub = roda_query(my_query)

print "Carregando o grafo Base..."

for i in sub:
	# print i["s"]["value"], i["p"]["value"], i["o"]["value"]
	G.add_node(i["s"]["value"])
	G.add_node(i["o"]["value"])
	G.add_edge(i["s"]["value"],i["o"]["value"], uri=i["p"]["value"])

print("graph has %d nodes with %d edges"\
          %(nx.number_of_nodes(G),nx.number_of_edges(G)))
print(nx.number_connected_components(G),"connected components")

for i in G.nodes():
	if G.degree(i) > super_node:
		G.remove_node(i)

print("graph has %d nodes with %d edges"\
          %(nx.number_of_nodes(G),nx.number_of_edges(G)))
print(nx.number_connected_components(G),"connected components")

# import pdb; pdb.set_trace()

print "Buscando as materias..."


# Preciso buscar as matérias publicadas em datas próximas

my_query = """
	SELECT ?s ?p ?o
	FROM <http://semantica.globo.com/esportes/>
	WHERE {?s a <http://semantica.globo.com/esportes/MateriaEsporte>;
	       ?p ?o 
	filter (isURI(?o) && !isBlank(?o))
	filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
	filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
	} 
	limit %s
	""" % nr_materias

materias = roda_query(my_query)

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

db = MySQLdb.connect("localhost","root","","PUC" )
cursor = db.cursor()

uniao = {}
scores = {}

for m1 in lista_materias.keys():
	cabeca = lista_materias[m1]
	del lista_materias[m1]
	for i1 in cabeca:
		for m2 in lista_materias.keys():
			if not m1+'.'+m2 in uniao:
				uniao[m1+'.'+m2] = 0
				scores[m1+'.'+m2] = 0
			for i2 in lista_materias[m2]:
				if i1 == i2:
					uniao[m1+'.'+m2] += 1
				elif i1 != i2:
					try:
						paths = list(nx.all_simple_paths(G, source=i1, target=i2, cutoff=max_path))
					except NetworkXError:
						continue
					if len(paths) > 0:
						s2 = 0
						s3 = 0
						s4 = 0
						for path in paths:
							sql = """INSERT INTO individuos (origem, destino, path, tamanho) VALUES (%s, %s, %s, %s);"""
							data = (m1,m2, ','.join(path), str(len(path)))
							cursor.execute(sql, data)
							db.commit()
							if   len(path) == 2:
								s2 += 1
							elif len(path) == 3:
								s3 += 1
							elif len(path) == 4:
								s4 += 1
						score = (0.5 ** 2 * s2) + (0.5 ** 3 * s3) + (0.5 ** 4 * s4) 
						scores[m1+'.'+m2] += score
						print i1, 's2:', s2,'s3:', s3,'s4:', s4, 'score:',score, i2
			if scores[m1+'.'+m2] > 0:
				print m1, scores[m1+'.'+m2], uniao[m1+'.'+m2], m2, '\n'
				sql = """INSERT INTO materias (origem, destino, score, intercessao) VALUES (%s, %s, %s, %s);"""
				data = (m1,m2, scores[m1+'.'+m2], uniao[m1+'.'+m2])
				cursor.execute(sql, data)
				db.commit()



cursor.close()

print "Fim do processo"

if imagem_on:
	gera_imagem(G)
