#!/usr/bin/env python
# -*- coding: utf-8 -*-
import networkx as nx
from networkx.exception import NetworkXError
import MySQLdb
import timeit
from sys import stdout

IMAGEM_ON = False
MAX_TRIPLAS = 1000000
MAX_MATERIAS = 10000
SUPER_NODE = 100
MAX_PATH = 3
SALVA_PATHS = True
NOME_PRODUTO = "G1"
# NOME_PRODUTO = "esportes"

DATA_INICIO = "2013-03-01T00:00:00Z"
DATA_FIM    = "2013-03-02T00:00:00Z"

def gera_imagem(G):
	import matplotlib.pyplot as plt
	nx.draw(G, with_labels=False)
	plt.savefig("path.png")

def roda_query(query):
	from SPARQLWrapper import SPARQLWrapper, JSON
	_sparql = SPARQLWrapper("http://localhost:8890/sparql/")
	_sparql.setQuery(query)
	_sparql.setReturnFormat(JSON)
	results = _sparql.query().convert()
	return results["results"]["bindings"]	

def busca_materias(produto, data_inicio, data_fim, max_materias):
	_materias_esporte = """
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
		""" % (data_inicio, data_fim, max_materias)

	_materias_G1 = """
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
		""" % (data_inicio, data_fim, max_materias)

	if produto == 'esportes':
		_materias = roda_query(_materias_esporte)
	elif produto == 'G1':
		_materias = roda_query(_materias_G1)

	_materias_order = sorted(_materias, key=lambda k: k['s']['value']) 

	_lista_materias = {}

	_old_value = ''

	for i in _materias_order:
		if _old_value != i["s"]["value"]:
			_lista_materias[i["s"]["value"]] = [i["o"]["value"]]
			_old_value = i["s"]["value"]
		else:
			_lista_materias[i["s"]["value"]].append(i["o"]["value"])
	return _lista_materias

def busca_entidades(produto, max_triplas):

	_query_esportes = """
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
		""" % max_triplas

	_query_g1 = """
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
		""" % max_triplas

	_query_base = """
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
		""" % max_triplas

	if produto == 'esportes':
		_entidades = roda_query(_query_esportes)
	elif produto == 'G1':
		_entidades = roda_query(_query_g1)
	elif produto == 'base':
		_entidades = roda_query(_query_base)

	return _entidades

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


def calcula_path(lista_materias, G, max_path, salva_paths):
	_uniao = {}
	_scores = {}
	_paths = {}
	_total = len(lista_materias.keys())
	_processando = 0
	search = 0
	hit = 0
	origem = lista_materias.keys()
	destino = lista_materias.keys()

	for m1 in origem:
		_processando += 1
		print "Processando matéria", _processando, "de", _total
		print "Entidades M1:", len(lista_materias[m1])
		print "Entidades M2:",
		destino.remove(m1)
		for m2 in destino:
			if not _uniao.has_key(m1+'.'+m2):
				_uniao[m1+'.'+m2] = 0
				_scores[m1+'.'+m2] = 0			
			print len(lista_materias[m2]),
			for e1 in lista_materias[m1]:
				for e2 in lista_materias[m2]:
					search += 1
					if e1 == e2:
						_uniao[m1+'.'+m2] += 1
						_paths[e1+'.'+e2] = []
					elif _paths.has_key(e1+'.'+e2):
						hit += 1
					else:
						try:
							_paths[e1+'.'+e2] = list(nx.all_simple_paths(G, source=e1, target=e2, cutoff=max_path))
							_paths[e2+'.'+e1] = _paths[e1+'.'+e2]
						except NetworkXError:
							_paths[e1+'.'+e2] = []
							_paths[e2+'.'+e1] = _paths[e1+'.'+e2]

						s2 = 0
						s3 = 0
						s4 = 0
						for _path in _paths[e1+'.'+e2]:
							if salva_paths:
								_sql = """INSERT INTO individuos (id_execucao, origem, destino, path, tamanho) VALUES (%s, %s, %s, %s, %s);"""
								_data = (id_execucao, m1, m2, ','.join(_path), str(len(_path)))
								cursor.execute(_sql, _data)
								db.commit()
							if   len(_path) == 2:
								s2 += 1
							elif len(_path) == 3:
								s3 += 1
							elif len(_path) == 4:
								s4 += 1
						_score = (0.5 ** 2 * s2) + (0.5 ** 3 * s3) + (0.5 ** 4 * s4)
						if _scores.has_key(m1+'.'+m2) :
							_scores[m1+'.'+m2] += _score
						else:
							_scores[m1+'.'+m2] = _score

			if _scores[m1+'.'+m2] > 0:
				_score_final = (_scores[m1+'.'+m2] + _uniao[m1+'.'+m2]) * (1.0 / (len(lista_materias[m1]) * len(lista_materias[m2])) )
				_sql = """INSERT INTO materias (id_execucao, origem, destino, score, entidades_origem, entidades_destino, intercessao, score_final) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
				_data = (id_execucao, m1, m2, _scores[m1+'.'+m2], len(lista_materias[m1]), len(lista_materias[m2]), _uniao[m1+'.'+m2], _score_final)
				cursor.execute(_sql, _data)
				db.commit()
		print ""

	print ""
	print "Search:", search, "Hit:", hit





def calcula_path_old(lista_materias, G, max_path, salva_paths):
	_uniao = {}
	_scores = {}
	_paths = {}
	_total = len(lista_materias.keys())
	search = 0
	hit = 0

	for m1 in lista_materias.keys():
		_cabeca = lista_materias[m1]
		del lista_materias[m1]
		print "\nFaltam processar: ", _total, "materias"
		for i1 in _cabeca:
			for m2 in lista_materias.keys():
				if not m1+'.'+m2 in _uniao:
					_uniao[m1+'.'+m2] = 0
					_scores[m1+'.'+m2] = 0
				_percentual_completo = 0
				_completo = 0
				for i2 in lista_materias[m2]:
					search += 1
					if i1 == i2:
						_uniao[m1+'.'+m2] += 1
						_paths[i1+'.'+i2] = []
					elif _paths.has_key(i1+'.'+i2):
						hit += 1
					else:
						try:
							_paths[i1+'.'+i2] = list(nx.all_simple_paths(G, source=i1, target=i2, cutoff=max_path))
							_paths[i2+'.'+i1] = _paths[i1+'.'+i2]
						except NetworkXError:
							_paths[i1+'.'+i2] = []
							_paths[i2+'.'+i1] = _paths[i1+'.'+i2]

					if len(_paths[i1+'.'+i2]) > 0:
						s2 = 0
						s3 = 0
						s4 = 0
						for _path in _paths[i1+'.'+i2]:

							if salva_paths:
								_sql = """INSERT INTO individuos (id_execucao, origem, destino, path, tamanho) VALUES (%s, %s, %s, %s, %s);"""
								_data = (id_execucao, m1,m2, ','.join(_path), str(len(_path)))
								cursor.execute(_sql, _data)
								db.commit()

							if   len(_path) == 2:
								s2 += 1
							elif len(_path) == 3:
								s3 += 1
							elif len(_path) == 4:
								s4 += 1

						_score = (0.5 ** 2 * s2) + (0.5 ** 3 * s3) + (0.5 ** 4 * s4) 
						_scores[m1+'.'+m2] += _score

					# _completo += 1
					# _percentual_completo = _completo / len(lista_materias[m2]) * 100.0
					# print _percentual_completo
					# print i1, i2
				print m1, m2
				if _scores[m1+'.'+m2] > 0:
					_score_final = (_scores[m1+'.'+m2] + _uniao[m1+'.'+m2]) * (1.0 / (len(_cabeca) * len(lista_materias[m2])) )
					_sql = """INSERT INTO materias (id_execucao, origem, destino, score, entidades_origem, entidades_destino, intercessao, score_final) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
					_data = (id_execucao, m1, m2, _scores[m1+'.'+m2], len(_cabeca), len(lista_materias[m2]), _uniao[m1+'.'+m2], _score_final)
					cursor.execute(_sql, _data)
					db.commit()
		_total -= 1
		# stdout.write("Materias a processar: %d    %d    \r" % (_total, _percentual_completo) )
		# stdout.flush()
	print ""
	print "Search:", search, "Hit:", hit

def grava_execucao(produto, dt_inicio, dt_fim, supernode, max_path):
	_sql = """INSERT INTO execucao (produto, dt_inicio, dt_fim, supernode, max_path) VALUES (%s, %s, %s, %s, %s);"""
	_data = (produto, dt_inicio, dt_fim, supernode, max_path)
	cursor.execute(_sql, _data)
	_id = cursor.lastrowid
	db.commit()
	return _id

def atualiza_execucao(id_execucao, materias, g_nos, g_arestas):
	_sql = """UPDATE execucao  SET materias = %s, nos = %s, arestas = %s where id = %s;"""
	_data = (materias, g_nos, g_arestas, id_execucao)
	cursor.execute(_sql, _data)
	_id = cursor.lastrowid
	db.commit()

##########################
### Inicio do programa ###

if __name__ == '__main__':

	start = timeit.default_timer()

	print "Produto:", NOME_PRODUTO

	db = MySQLdb.connect("localhost","root","","PUC" )
	cursor = db.cursor()

	id_execucao = grava_execucao(NOME_PRODUTO, DATA_INICIO, DATA_FIM, SUPER_NODE, MAX_PATH)

	lista_materias = busca_materias(NOME_PRODUTO, DATA_INICIO, DATA_FIM, MAX_MATERIAS)

	# import pdb; pdb.set_trace()

	total_materias = len(lista_materias.keys())

	if total_materias == 0:
		print "Nenhuma materia retornada."
		quit()

	print "Total de materias: ", total_materias

	print "Busca triplas produto..."

	entidades = busca_entidades(NOME_PRODUTO, MAX_TRIPLAS)

	print "Carregando o grafo produto..."

	G = cria_grafo()
	carrega_grafo(G, entidades)

	print("O grafo tem %d nos com %d arestas"\
	          %(nx.number_of_nodes(G),nx.number_of_edges(G)))

	print "Buscando as triplas Base..."

	entidades = busca_entidades("base", MAX_TRIPLAS)

	print "Carregando o grafo Base..."

	carrega_grafo(G, entidades)

	print("O grafo tem %d nos com %d arestas"\
	          %(nx.number_of_nodes(G),nx.number_of_edges(G)))

	print "Remove super_nodes..."
	remove_supernode(G, SUPER_NODE)
	print("O grafo tem %d nos com %d arestas"\
      %(nx.number_of_nodes(G),nx.number_of_edges(G)))

	# import pdb; pdb.set_trace()

	atualiza_execucao(id_execucao, total_materias, nx.number_of_nodes(G), nx.number_of_edges(G))

	print "Calculando os paths..."

	calcula_path(lista_materias, G, MAX_PATH, SALVA_PATHS)


	if IMAGEM_ON:
		gera_imagem(G)

	stop = timeit.default_timer()
	tempo_execucao = stop - start 

	update = """update execucao set tempo_execucao = %s where id = %s; """
	data = (tempo_execucao, id_execucao)
	cursor.execute(update, data)
	db.commit()

	# import pdb; pdb.set_trace()

	cursor.close()

	print "fim processamento"
	print "Tempo de execucao (segundos):", tempo_execucao
