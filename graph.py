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
SUPER_NODE = 500
MAX_PATH = 3
SALVA_PATHS = False
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
		# print "Entidades M1:", len(lista_materias[m1])
		# stdout.write("Entidades M2: ")
		destino.remove(m1)
		for m2 in destino:
			# stdout.write(str(len(lista_materias[m2]))) 
			if not _uniao.has_key(m1+'.'+m2):
				_uniao[m1+'.'+m2] = 0
				_scores[m1+'.'+m2] = 0			
			for e1 in lista_materias[m1]:
				for e2 in lista_materias[m2]:
					# stdout.write(".")
					stdout.write("\n" + e1 + " " + e2)
					stdout.flush()
					search += 1
					if e1 == e2:
						stdout.write(" Same\n")
						_uniao[m1+'.'+m2] += 1
						_paths[e1+'.'+e2] = []
					elif _paths.has_key(e1+'.'+e2):
						stdout.write(" Hit\n")
						hit += 1
					else:
						stdout.write(" Search ")	
						try:							
							start_p = timeit.default_timer()
							_paths[e1+'.'+e2] = list(nx.all_simple_paths(G, source=e1, target=e2, cutoff=max_path))
							_paths[e2+'.'+e1] = _paths[e1+'.'+e2]
							stop_p = timeit.default_timer()
							stdout.write(" " + str(stop_p - start_p) + " ")
							stdout.write(str(len(_paths[e1+'.'+e2])) + "\n")
						except NetworkXError:
							_paths[e1+'.'+e2] = []
							_paths[e2+'.'+e1] = _paths[e1+'.'+e2]

						s2 = 0
						s3 = 0
						s4 = 0
						for _path in _paths[e1+'.'+e2]:
							stdout.write(".")
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


def busca_materias_saibamais():
	from lxml import etree
	import lxml.html as lh
	from BeautifulSoup import BeautifulSoup, Tag

	_materias = []
	materia_nao_encontrada = False

	db_g1 = MySQLdb.connect("localhost","root","","g1" )
	cursor_g1 = db_g1.cursor()
	cursor_g1.execute("""
					select permalink, corpo from materia m, materia_folder mf
					where m.primeira_publicacao >= '2013-03-07 00:00:00'
					and m.primeira_publicacao < '2013-03-11 00:00:00'
					and m.id = mf.materia_id
					and mf.folder_id = 42
					and corpo like '%<div class="saibamais componente_materia">%';
					""")

	materias = cursor_g1.fetchall()
	for materia in materias:
		myparser = etree.HTMLParser(encoding="utf-8")
		tree = etree.HTML(materia[1], parser=myparser)
		
		# doc=lh.fromstring(html)
		# for elem in tree.xpath('.//ul[@class="saibamais componente_materia"]/li'):
			# print elem.text_content()
		
		text = etree.tostring(tree, pretty_print=True)
		text_a_partir_da_div = text[text.find('''<div class="saibamais componente_materia">'''):] #slicing
		soup = BeautifulSoup(text_a_partir_da_div)


		try:
			# list comprehension
			referencias = [(li.text,li.a['href']) for li in soup.ul if type(li) == Tag]
		except:
			referencias = []
			print "Com erro no saiba mais:", materia[0]

		_materias_G1 = """ 
		SELECT ?s 
		FROM <http://semantica.globo.com/G1/>
		WHERE {?s a <http://semantica.globo.com/G1/Materia> .
		       ?s <http://semantica.globo.com/base/permalink> "%s" .
		} 
		""" % ("http://g1.globo.com" + materia[0])
		
		triplas = roda_query(_materias_G1)

		_materia_principal = ''
		_lista_materias = []

		if len(triplas) > 0:

			_materia_principal = triplas[0]['s']['value']
			_lista_materias = [("http://g1.globo.com" + materia[0])]

		for ref in referencias:
			_lista_materias.append(ref[1])

		for i in _lista_materias:

			_materias_G1 = """ 
			SELECT ?s 
			FROM <http://semantica.globo.com/G1/>
			WHERE {?s a <http://semantica.globo.com/G1/Materia> .
			       ?s <http://semantica.globo.com/base/permalink> "%s" .
			} 
			""" % (i)
			
			triplas = roda_query(_materias_G1)

			if len(triplas) == 0:
				print "Matéria", i, "não encontrada"
				db.rollback()
				break

			_materia_saibamais = triplas[0]['s']['value']

			if _materia_principal != _materia_saibamais:
				_sql = """INSERT INTO materias_saibamais (id_execucao, materia_principal, materia_saibamais) VALUES (%s, %s, %s);"""
				_data = (id_execucao, _materia_principal, _materia_saibamais)
				print _data
				cursor.execute(_sql, _data)

			_materias_tmp = []
			_materias_G1 = """ 
			SELECT ?s ?p ?o
			FROM <http://semantica.globo.com/G1/>
			WHERE {?s a <http://semantica.globo.com/G1/Materia> .
			       ?s <http://semantica.globo.com/base/permalink> "%s" .
			       ?s ?p ?o 
			filter (isURI(?o) && !isBlank(?o))
			filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
			filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
			} 
			order by ?s
			""" % (i)
			
			triplas = roda_query(_materias_G1)

			_materias_tmp = _materias_tmp + triplas
		
		db.commit()
		_materias = _materias + _materias_tmp

	db_g1.close()

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

	stdout.write("Produto: " + NOME_PRODUTO + '\n')

	db = MySQLdb.connect("localhost","root","","PUC" )
	cursor = db.cursor()

	id_execucao = grava_execucao(NOME_PRODUTO, DATA_INICIO, DATA_FIM, SUPER_NODE, MAX_PATH)

	print "Busca materias..."

	# lista_materias = busca_materias(NOME_PRODUTO, DATA_INICIO, DATA_FIM, MAX_MATERIAS)
	lista_materias = busca_materias_saibamais()

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
