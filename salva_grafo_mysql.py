#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import timeit

MAX_TRIPLAS = 1000000
# NOME_PRODUTO = "G1"
NOME_PRODUTO = "esportes"

def roda_query(query):
	from SPARQLWrapper import SPARQLWrapper, JSON
	_sparql = SPARQLWrapper("http://localhost:8890/sparql/")
	_sparql.setQuery(query)
	_sparql.setReturnFormat(JSON)
	results = _sparql.query().convert()
	return results["results"]["bindings"]	


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


if __name__ == '__main__':


	db = MySQLdb.connect("localhost","root","","PUC" )
	cursor = db.cursor()

	cursor.execute(""" truncate table grafo ; """ )

	start = timeit.default_timer()

	print "Produto:", NOME_PRODUTO 

	print "Buscando triplas produto..."

	entidades = busca_entidades(NOME_PRODUTO, MAX_TRIPLAS)

	print "Salvando no MySQL..."

	for i in entidades:
		s = i['s']['value']
		p = i['p']['value']
		o = i['o']['value']
		sql = """INSERT INTO grafo (s, p, o) VALUES (%s, %s, %s);"""
		data = (s, p, o)
		cursor.execute(sql, data)
		db.commit()

	print "Buscando as triplas Base..."

	entidades = busca_entidades("base", MAX_TRIPLAS)

	for i in entidades:
		s = i['s']['value']
		p = i['p']['value']
		o = i['o']['value']
		sql = """INSERT INTO grafo (s, p, o) VALUES (%s, %s, %s);"""
		data = (s, p, o)
		cursor.execute(sql, data)
		db.commit()

	stop = timeit.default_timer()

	tempo_execucao = stop - start 

	print "fim processamento"
	print "Tempo de execucao (segundos):", tempo_execucao


