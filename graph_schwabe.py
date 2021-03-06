#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Versão com alterações do Schwabe
import networkx as nx
import math
from networkx.exception import NetworkXError
import MySQLdb
import timeit
from sys import stdout, argv
from conf import *

EDITORIA 	= argv[1]

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
		filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> && ?p != <http://www.w3.org/2000/01/rdf-schema#subClassOf>)
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
		filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> && ?p != <http://www.w3.org/2000/01/rdf-schema#subClassOf>)
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
		filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> && ?p != <http://www.w3.org/2000/01/rdf-schema#subClassOf>)
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
		filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> && ?p != <http://www.w3.org/2000/01/rdf-schema#subClassOf>)
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
		filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> && ?p != <http://www.w3.org/2000/01/rdf-schema#subClassOf>)
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


def busca_schema(produto):

	# import pdb; pdb.set_trace()

	_query_base = """
		SELECT ?s ?p ?o
		from <http://semantica.globo.com/>
		WHERE {
		  {
		  graph <http://semantica.globo.com/> {?s a owl:Class; rdfs:subClassOf ?o}
		  {?o a owl:Class BIND (rdfs:subClassOf AS ?p)}
		  filter (?o != owl:Thing )
		  }
		  union
		  {
		  graph <http://semantica.globo.com/> {?s a owl:Class}
		  {?p rdfs:range ?o; rdfs:domain ?super.
		    ?s rdfs:subClassOf ?super
		    OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0) )}.
		    ?o a owl:Class
		  }
		filter (?s != <http://semantica.globo.com/base/Video>)
		filter (?s != <http://semantica.globo.com/base/ConteudoAtomico>)
		filter (?s != <http://semantica.globo.com/base/Materia>)
		filter (?s != <http://semantica.globo.com/base/ConteudoComposto>)
		filter (?s != <http://semantica.globo.com/base/Foto>)
		filter (?s != <http://semantica.globo.com/base/GaleriaDeFotos>)
		}
		"""

	_query_esportes = """
		SELECT ?s ?p ?o
		WHERE {
		  {
		  graph <http://semantica.globo.com/esportes/> {?s a owl:Class; rdfs:subClassOf ?o}
		  {?o a owl:Class BIND (rdfs:subClassOf AS ?p)}
		  filter (?o != owl:Thing )
		  }
		  union
		  {
		  graph <http://semantica.globo.com/esportes/> {?s a owl:Class}
		  {?p rdfs:range ?o; rdfs:domain ?super.
		    ?s rdfs:subClassOf ?super
		    OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0) )}.
		    ?o a owl:Class
		  }
		filter (?s != <http://semantica.globo.com/esportes/MateriaEsporte>)
		filter (?s != <http://semantica.globo.com/esportes/GaleriaDeFotos>)
		filter (?s != <http://semantica.globo.com/esportes/Guia>)
		filter (?s != <http://semantica.globo.com/esportes/Foto>)
		filter (?o != <http://semantica.globo.com/esportes/MateriaEsporte>)
		filter (?o != <http://semantica.globo.com/esportes/GaleriaDeFotos>)
		filter (?o != <http://semantica.globo.com/esportes/Guia>)
		filter (?o != <http://semantica.globo.com/esportes/Foto>)
		}
		""" 

	_query_g1 = """
		SELECT ?s ?p ?o
		WHERE {
		  {
		  graph <http://semantica.globo.com/G1/> {?s a owl:Class; rdfs:subClassOf ?o}
		  {?o a owl:Class BIND (rdfs:subClassOf AS ?p)}
		  filter (?o != owl:Thing )
		  }
		  union
		  {
		  graph <http://semantica.globo.com/G1/> {?s a owl:Class}
		  {?p rdfs:range ?o; rdfs:domain ?super.
		    ?s rdfs:subClassOf ?super
		    OPTION (TRANSITIVE, t_distinct, t_step('step_no') as ?n, t_min (0) )}.
		    ?o a owl:Class
		  }
	    filter (?s != <http://semantica.globo.com/G1/Materia>)
	    filter (?s != <http://semantica.globo.com/G1/GaleriaDeFotos>)
	    filter (?s != <http://semantica.globo.com/G1/Conteudo>)
	    filter (?s != <http://semantica.globo.com/G1/Foto>)
	    filter (?o != <http://semantica.globo.com/G1/Materia>)
	    filter (?o != <http://semantica.globo.com/G1/GaleriaDeFotos>)
	    filter (?o != <http://semantica.globo.com/G1/Conteudo>)
	    filter (?o != <http://semantica.globo.com/G1/Foto>)
		}
		""" 

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
	
def carrega_grafo_from_mysql(grafo):
	cursor.execute("""
					select s, p, o 
					from grafo;
					""")

	items = cursor.fetchall()
	for i in items:
		grafo.add_node(i[0])
		grafo.add_node(i[2])
		grafo.add_edge(i[0],i[2])

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
		# print "Materia M1:", m1
		destino.remove(m1)
		for m2 in destino:
			# print "  Materia M2:", m2
			if not _uniao.has_key(m1+'.'+m2):
				_uniao[m1+'.'+m2] = 0
				_scores[m1+'.'+m2] = 0			
			for e1 in lista_materias[m1]:
				# print "    ", e1
				for e2 in lista_materias[m2]:
					# print "      ", e2
					search += 1
					if e1 == e2:
						_uniao[m1+'.'+m2] += 1
						_paths[e1+'.'+e2] = []
						# print _uniao[m1+'.'+m2]
					elif _paths.has_key(e1+'.'+e2):
						hit += 1
					else:
						try:							
							# start_p = timeit.default_timer()
							_paths[e1+'.'+e2] = list(nx.all_simple_paths(G, source=e1, target=e2, cutoff=max_path))
							_paths[e2+'.'+e1] = _paths[e1+'.'+e2]
							# stop_p = timeit.default_timer()
							# stdout.write(" " + str(stop_p - start_p) + " ")
							# stdout.write(str(len(_paths[e1+'.'+e2])) + "\n")
						except NetworkXError:
							_paths[e1+'.'+e2] = []
							_paths[e2+'.'+e1] = _paths[e1+'.'+e2]

						s2 = 0
						s3 = 0
						s4 = 0
						for _path in _paths[e1+'.'+e2]:
							# stdout.write(".")
							if salva_paths:
								_sql = """INSERT INTO paths (id_execucao, origem, destino, path, tamanho) VALUES (%s, %s, %s, %s, %s);"""
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

			# if _scores[m1+'.'+m2] > 0:
			_score_final = (_scores[m1+'.'+m2] + _uniao[m1+'.'+m2]) * (1.0 / (len(lista_materias[m1]) * len(lista_materias[m2])) )
			_sql = """INSERT INTO materias (id_execucao, origem, destino, score, entidades_origem, entidades_destino, intercessao, score_final) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
			_data = (id_execucao, m1, m2, _scores[m1+'.'+m2], len(lista_materias[m1]), len(lista_materias[m2]), _uniao[m1+'.'+m2], _score_final)
			cursor.execute(_sql, _data)
			db.commit()

	print ""
	print "Search:", search, "Hit:", hit


def busca_materias_saibamais(data_inicio, data_fim, editoria, max_materias):
	""" Busca as materias relacionadas à matéria principal pelo componente "Saiba Mais" """
	from lxml import etree
	import lxml.html as lh
	from BeautifulSoup import BeautifulSoup, Tag

	_entidades = []

	# Busca as matérias do MySQL que tem o componente "Saiba Mais"
	db_g1 = MySQLdb.connect("localhost","root","","g1" )
	cursor_g1 = db_g1.cursor()

	_sql_materias = """
					select permalink, corpo from materia m, materia_folder mf
					where m.primeira_publicacao >= '%s'
					and m.primeira_publicacao < '%s'
					and m.id = mf.materia_id
					and mf.folder_id = %s
					and corpo like '%%<div class="saibamais componente_materia">%%'
					limit %s;
					""" % (data_inicio, data_fim, editoria, max_materias)

	cursor_g1.execute(_sql_materias)

	materias = cursor_g1.fetchall()


	print "buscando dados no Virtuoso..."

	# Para cada corpo de matéria vai extrair os links "Saiba Mais"
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
			# print "Com erro no saiba mais:", materia[0]

		# Pega a URI da matéria principal no Virtuoso
		_materias_G1 = """ 
		SELECT ?s 
		FROM <http://semantica.globo.com/G1/>
		WHERE {?s a <http://semantica.globo.com/G1/Materia> .
		       ?s <http://semantica.globo.com/base/permalink> "%s" .
		} 
		""" % ("http://g1.globo.com" + materia[0])
		
		triplas = roda_query(_materias_G1)

		_uri_materia_principal = ''
		_entidades_materias = []
		_entidades_tmp = []

		# cria uma lista para guardar todas as matérias, começando pela principal
		if len(triplas) > 0:
			_uri_materia_principal = triplas[0]['s']['value']
			_materias_G1 = """ 
				SELECT ?s ?p ?o
				FROM <http://semantica.globo.com/G1/>
				WHERE {?s a <http://semantica.globo.com/G1/Materia> .
				       ?s <http://semantica.globo.com/base/permalink> "%s" .
				       ?s ?p ?o 
				filter (isURI(?o) && !isBlank(?o))
				filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
				filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> && ?p != <http://www.w3.org/2000/01/rdf-schema#subClassOf>)
				} 
			""" % ("http://g1.globo.com" + materia[0])
			
			triplas = roda_query(_materias_G1)
			_entidades_tmp = triplas
			# _entidades_materias = [("http://g1.globo.com" + materia[0])]
			# print "_uri_materia_principal:", _uri_materia_principal
			for ref in referencias:
				_entidades_materias.append(ref[1])
		# else:
		# 	print ">>> Materia principal não está no virtuoso"

		for i in _entidades_materias:

			_materias_G1 = """ 
			SELECT ?s 
			FROM <http://semantica.globo.com/G1/>
			WHERE {?s a <http://semantica.globo.com/G1/Materia> .
			       ?s <http://semantica.globo.com/base/permalink> "%s" .
			} 
			""" % (i)
			
			triplas = roda_query(_materias_G1)

			# import pdb; pdb.set_trace()

			if len(triplas) == 0:
				# print "não encontrada"
				_entidades_tmp = []
				db.rollback()
				break

			_uri_materia_saibamais = triplas[0]['s']['value']
			# print "_uri_materia_saibamais:", _uri_materia_saibamais

			_sql = """INSERT INTO materias_saibamais (id_execucao, materia_principal, materia_saibamais) VALUES (%s, %s, %s);"""
			_data = (id_execucao, _uri_materia_principal, _uri_materia_saibamais)
			cursor.execute(_sql, _data)

			# _materias_tmp = []
			_materias_G1 = """ 
			SELECT ?s ?p ?o
			FROM <http://semantica.globo.com/G1/>
			WHERE {?s a <http://semantica.globo.com/G1/Materia> .
			       ?s <http://semantica.globo.com/base/permalink> "%s" .
			       ?s ?p ?o 
			filter (isURI(?o) && !isBlank(?o))
			filter ( ?o != <http://www.w3.org/2002/07/owl#DatatypeProperty> && ?o != <http://www.w3.org/1999/02/22-rdf-syntax-ns#Property> && ?o != <http://www.w3.org/2002/07/owl#Class> && ?o != <http://www.w3.org/2002/07/owl#ObjectProperty>) 
			filter (?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> && ?p != <http://www.w3.org/2000/01/rdf-schema#subClassOf>)
			} 
			""" % (i)
			
			triplas = roda_query(_materias_G1)
			# print ""
			# print _uri_materia_saibamais
			# print "  ", [x['s']['value'] + " >>> " + x['o']['value'] for x in triplas]


			_entidades_tmp = _entidades_tmp + triplas

			# print ""
			# print "  ", [x['s']['value'] + " >>> " + x['o']['value'] for x in _entidades_tmp]

			# print len(_entidades_tmp)
		
		db.commit()
		_entidades = _entidades + _entidades_tmp

		# print "  ", len(_entidades)

	db_g1.close()

	_materias_order = sorted(_entidades, key=lambda k: k['s']['value']) 

	# print "      ", len(_materias_order)

	_lista_materias = {}

	_old_value = ''

	for i in _materias_order:
		if _old_value != i["s"]["value"]:
			_lista_materias[i["s"]["value"]] = [i["o"]["value"]]
			_old_value = i["s"]["value"]
		else:
			_lista_materias[i["s"]["value"]].append(i["o"]["value"])

	# Remove valores duplicados nas
	for i in _lista_materias:
		_lista_materias[i] = list(set(_lista_materias[i]))

	# import pdb; pdb.set_trace()

	return _lista_materias



def grava_execucao(produto, dt_inicio, dt_fim, supernode, max_path, editoria):
	_sql = """INSERT INTO execucao (produto, dt_inicio, dt_fim, supernode, max_path, editoria) VALUES (%s, %s, %s, %s, %s, %s);"""
	_data = (produto, dt_inicio, dt_fim, supernode, max_path, editoria)
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

def analisa_resultado(id_execucao, max_recomendacoes_por_materia):
	_acertos = 0
	cursor.execute("""
		select origem, count(*)
		from materias
		where id_execucao = %s
		group by origem
		""", (id_execucao) )

	materias_origem = cursor.fetchall()

	for i in materias_origem:
		cursor.execute("""
			select destino
			from materias
			where id_execucao = %s
			and origem = %s
			order by score_final desc
			limit %s
			""", (id_execucao, i[0], max_recomendacoes_por_materia))

		res = cursor.fetchall()

		materias_destino = (', '.join('"' + x[0] + '"' for x in res))

		# import pdb; pdb.set_trace()

		sql = """
			select distinct materia_saibamais
			from materias_saibamais
			where id_execucao = %s
			and materia_principal = '%s'
			and materia_saibamais in (%s);
			""" % (id_execucao, i[0], materias_destino) 

		cursor.execute(sql)

		materias_saibamais = cursor.fetchall()

		if len(materias_saibamais) > 0:
			_acertos += 1
			print i[0]
			print "  ", ", ".join(materias_saibamais[0])

	update = """update execucao set max_recomendacoes_por_materia = %s, acertos = %s where id = %s; """
	data = (max_recomendacoes_por_materia, _acertos, id_execucao )
	cursor.execute(update, data)
	db.commit()

	return _acertos

		

##########################
### Inicio do programa ###

if __name__ == '__main__':

	start = timeit.default_timer()

	print "\nProduto: " + NOME_PRODUTO + "\n"

	db = MySQLdb.connect("localhost","root","","PUC" )
	cursor = db.cursor()

	cursor.execute(""" select name_txt from g1.folder where folder_id = %s ;""" % (EDITORIA))
	editoria = cursor.fetchone()

	id_execucao = grava_execucao(NOME_PRODUTO, DATA_INICIO, DATA_FIM, SUPER_NODE, MAX_PATH, "sem editoria")

	print "Busca materias ..."

	lista_materias = busca_materias(NOME_PRODUTO, DATA_INICIO, DATA_FIM, MAX_MATERIAS)
	# lista_materias = busca_materias_saibamais(DATA_INICIO, DATA_FIM, EDITORIA, MAX_MATERIAS)

	# import pdb; pdb.set_trace()

	total_materias = len(lista_materias.keys())

	if total_materias == 0:
		print "Nenhuma materia retornada."
		quit()

	print "Total de materias: ", total_materias

	G = cria_grafo()

	if CARREGA_GRAFO_MYSQL:
		print "Carregando o grafo salvo no MySQL..."
		carrega_grafo_from_mysql(G)
	else:

		print "Busca triplas produto..."

		entidades = busca_entidades(NOME_PRODUTO, MAX_TRIPLAS)

		print "Carregando o grafo produto..."

		carrega_grafo(G, entidades)

		print("O grafo tem %d nos com %d arestas"\
		          %(nx.number_of_nodes(G),nx.number_of_edges(G)))

		print "Buscando as triplas Base..."

		entidades = busca_entidades("base", MAX_TRIPLAS)

		print "Carregando o grafo Base..."

		carrega_grafo(G, entidades)

	print("O grafo tem %d nos com %d arestas"\
	          %(nx.number_of_nodes(G),nx.number_of_edges(G)))



	if CARREGA_GRAFO_MYSQL:
		F = nx.DiGraph()
		print "Carregando o grafo salvo no MySQL..."
		cursor.execute("""
						select a, b, cluster, idf, combinado
						from grafo_schwabe ;
						""")

		items = cursor.fetchall()
		for i in items:
			F.add_edge(i[0], i[1], cluster = i[2], idf = i[3], combinado = i[4])
	else:

		S = cria_grafo()

		print "Carregando schema produto..."

		entidades = busca_schema(NOME_PRODUTO)

		carrega_grafo(S, entidades)

		print "Carregando schema Base..."

		entidades = busca_schema("base")

		carrega_grafo(S, entidades)

		print("O grafo tem %d nos com %d arestas"\
		          %(nx.number_of_nodes(S),nx.number_of_edges(S)))

		node_list = nx.nodes(S)

		DI = nx.DiGraph()

		print "Carregando o schema..."

		while len(node_list) > 1:
			x = node_list.pop(0)
			neighbors_x = set(nx.all_neighbors(S, x))
			x_size = len(neighbors_x)
			for y in node_list:
				if y in neighbors_x:
					neighbors_y = set(nx.all_neighbors(S, y))
					y_size = len(neighbors_y)
					x_y = len(list(set(neighbors_x) & set(neighbors_y)))
					if x_y > 0:
						c = float(x_y) / (x_size - 1)
						p = 1 / math.sqrt(y_size)
						cxp = c * p
						DI.add_edge(x,y, cluster = c, idf = p, combinado = cxp)
						c = float(x_y) / (y_size - 1)
						p = 1 / math.sqrt(x_size)
						cxp = c * p
						DI.add_edge(y,x, cluster = c, idf = p, combinado = cxp)

		print("O grafo tem %d nos com %d arestas"\
		          %(nx.number_of_nodes(DI),nx.number_of_edges(DI)))

		F = nx.DiGraph()

		query = """
		select ?s where {?s a <%s>}
		"""
		for edg in DI.edges_iter(nbunch=None, data=True):
			print edg[0], edg[1], "%.2f" % edg[2]['cluster'], "%.2f" % edg[2]['idf'], "%.2f" % edg[2]['combinado']
			print "Query 1"
			edg0 = roda_query(query % edg[0])
			print "Query 2"
			edg1 = roda_query(query % edg[1])
			print "Roda loop"
			for e0 in edg0:
				for e1 in edg1:
					x = e0["s"]["value"]
					y = e1["s"]["value"]
					if G.has_edge(x, y):
						F.add_edge(x, y, edg[2])
						sql = """INSERT INTO grafo_schwabe (produto, a, b, cluster, idf, combinado) VALUES (%s, %s, %s, %s, %s, %s);"""
						data = (NOME_PRODUTO, x, y, edg[2]['cluster'], edg[2]['idf'], edg[2]['combinado'])
						cursor.execute(sql, data)
						db.commit()


	print("O grafo tem %d nos com %d arestas"\
      %(nx.number_of_nodes(F),nx.number_of_edges(F)))
		# import pdb; pdb.set_trace()


	materias = lista_materias.keys()
	combinado = {}

	while len(materias) > 1:
		# import pdb; pdb.set_trace()
		m0 = materias.pop(0)
		for m1 in materias:
			print m0, m1
			for e0 in lista_materias[m0]:
				for e1 in lista_materias[m1]:
					if F.has_edge(e0, e1):
						if not combinado.has_key(m0+'.'+m1):
							combinado[m0+'.'+m1] = 0
						combinado[m0+'.'+m1] += F[e0][e1]["combinado"]
			if combinado.has_key(m0+'.'+m1): 
				query = """
				insert into materias_schwabe (id_execucao, origem, destino, combinado)
				values (%s, '%s', '%s', %s);
				""" % (id_execucao, m0, m1, combinado[m0+'.'+m1])
				cursor.execute(query)
				db.commit()

	stop = timeit.default_timer()
	tempo_execucao = stop - start 

	cursor.close()

	print "fim processamento"
	print "Tempo de execucao (segundos):", tempo_execucao
