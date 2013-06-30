#!/usr/bin/env python
import networkx as nx
from networkx.exception import NetworkXError
import MySQLdb
import timeit
from sys import stdout

imagem_on = False
nr_triplas = 1000000
nr_materias = 10000
super_node = 100
max_path = 3
produto_global = "esportes"

data_inicio = "2013-03-01T00:00:00Z"
data_fim    = "2013-03-05T00:00:00Z"

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

def busca_materias(produto):
	materias_esporte = """
		SELECT ?s ?p ?o
		FROM <http://semantica.globo.com/esportes/>
		WHERE {?s a <http://semantica.globo.com/esportes/MateriaEsporte>;
	           <http://semantica.globo.com/base/data_da_primeira_publicacao> ?data ;
		       ?p ?o 
		filter (isURI(?o) && !isBlank(?o))
		filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
		filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
		filter (?data >= "%s"^^xsd:dateTime && ?data < "%s"^^xsd:dateTime)
		} 
		order by ?s
		limit %s
		""" % (data_inicio, data_fim, nr_materias)

	materias_G1 = """
		SELECT ?s ?p ?o
		FROM <http://semantica.globo.com/G1/>
		WHERE {?s a <http://semantica.globo.com/G1/Materia>;
		       # <http://semantica.globo.com/G1/editoria_id> "8";
	           <http://semantica.globo.com/base/data_da_primeira_publicacao> ?data ;
		       ?p ?o 
		filter (isURI(?o) && !isBlank(?o))
		filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
		filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
		filter (?data >= "%s"^^xsd:dateTime && ?data < "%s"^^xsd:dateTime)
		} 
		order by ?s
		limit %s
		""" % (data_inicio, data_fim, nr_materias)

	if produto == 'esportes':
		materias = roda_query(materias_esporte)
	elif produto == 'G1':
		materias = roda_query(materias_G1)

	materias_order = sorted(materias, key=lambda k: k['s']['value']) 

	lista_materias = {}

	old_value = ''

	for i in materias_order:
		if old_value != i["s"]["value"]:
			lista_materias[i["s"]["value"]] = [i["o"]["value"]]
			old_value = i["s"]["value"]
		else:
			lista_materias[i["s"]["value"]].append(i["o"]["value"])
	return lista_materias

def busca_entidades(produto):

	query_esportes = """
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

	query_g1 = """
		SELECT ?s ?p ?o
		FROM <http://semantica.globo.com/G1/>
		WHERE {?s ?p ?o 
		filter (isURI(?o) && !isBlank(?o))
		filter (!isBlank(?s)) 
		filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>)
		filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
	    filter not exists {?s a <http://semantica.globo.com/G1/Materia>}
	    filter not exists {?s a <http://semantica.globo.com/G1/GaleriaDeFotos>}
	    filter not exists {?s a <http://semantica.globo.com/G1/Conteudo>}
	    filter not exists {?s a <http://semantica.globo.com/G1/Foto>}
	    filter not exists {?s a <http://semantica.globo.com/base/Video>}
	    filter not exists {?s a <http://semantica.globo.com/base/ConteudoAtomico>}
	    filter not exists {?s a <http://semantica.globo.com/base/Materia>}
	    filter not exists {?s a <http://semantica.globo.com/base/ConteudoComposto>}
	    filter not exists {?s a <http://semantica.globo.com/base/Foto>}
	    filter not exists {?s a <http://semantica.globo.com/base/GaleriaDeFotos>}
	    	} limit %s
		""" % nr_triplas

	query_base = """
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

	if produto == 'esportes':
		entidades = roda_query(query_esportes)
	elif produto == 'G1':
		entidades = roda_query(query_g1)
	elif produto == 'base':
		entidades = roda_query(query_base)

	return entidades

def carrega_grafo(grafo, items):
	for i in items:
		grafo.add_node(i["s"]["value"])
		grafo.add_node(i["o"]["value"])
		grafo.add_edge(i["s"]["value"],i["o"]["value"], uri=i["p"]["value"])
	
def cria_grafo():
	return nx.Graph()

def remove_supernode(grafo, max_node):
	if max_node > 0:
		for i in grafo.nodes():
			if grafo.degree(i) > max_node:
				grafo.remove_node(i)


def calcula_path(lista_materias, G):
	uniao = {}
	scores = {}
	total = len(lista_materias.keys())

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
							# print i1, 's2:', s2,'s3:', s3,'s4:', s4, 'score:',score, i2
				if scores[m1+'.'+m2] > 0:
					# print m1, scores[m1+'.'+m2], uniao[m1+'.'+m2], m2, '\n'

					sql = """INSERT INTO materias (origem, destino, score, entidades_origem, entidades_destino, intercessao) VALUES (%s, %s, %s, %s, %s, %s);"""
					data = (m1,m2, scores[m1+'.'+m2], len(cabeca), len(lista_materias[m2]), uniao[m1+'.'+m2])
					cursor.execute(sql, data)
					db.commit()
		total -= 1
		# print "Falta processar: ", total, "materias"
		stdout.write("Materias a processar: %d   \r" % (total) )
		stdout.flush()
	print ""

if __name__ == '__main__':

	start = timeit.default_timer()

	lista_materias = busca_materias(produto_global)

	total_materias = len(lista_materias.keys())

	if total_materias == 0:
		print "Nenhuma materia retornada."
		quit()

	print "Total de materias: ", total_materias

	print "Busca triplas produto..."

	sub = busca_entidades(produto_global)

	print "Carregando o grafo produto..."

	G = cria_grafo()
	carrega_grafo(G, sub)

	print("O grafo tem %d nos com %d arestas"\
	          %(nx.number_of_nodes(G),nx.number_of_edges(G)))

	# paths = list(nx.all_simple_paths(G, source='http://semantica.globo.com/esportes/equipe/2661', target='http://semantica.globo.com/esportes/atleta/73862', cutoff=4))
	# print paths

	print "Buscando as triplas Base..."

	sub = busca_entidades("base")

	print "Carregando o grafo Base..."

	carrega_grafo(G, sub)

	print("O grafo tem %d nos com %d arestas"\
	          %(nx.number_of_nodes(G),nx.number_of_edges(G)))


	print "Remove super_nodes..."
	remove_supernode(G, super_node)
	print("O grafo tem %d nos com %d arestas"\
      %(nx.number_of_nodes(G),nx.number_of_edges(G)))

	# import pdb; pdb.set_trace()


	print "Calculando os paths..."

	db = MySQLdb.connect("localhost","root","","PUC" )
	cursor = db.cursor()

	truncate = """truncate table materias;"""
	cursor.execute(truncate)
	truncate = """truncate table individuos;"""
	cursor.execute(truncate)

	calcula_path(lista_materias, G)

	print "Update score final"

	update = """update materias set score_final = (score + intercessao) * (1 / (entidades_origem * entidades_destino) ); """

	cursor.execute(update)

	db.commit()

	cursor.close()

	if imagem_on:
		gera_imagem(G)

	stop = timeit.default_timer()

	print "fim processamento"
	print "Tempo de execucao (segundos):", stop - start 
