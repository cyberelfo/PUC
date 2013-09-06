#!/usr/bin/env python
# -*- coding: utf-8 -*-
import timeit
from SPARQLWrapper import SPARQLWrapper, JSON

query = """
SELECT ?s ?p ?o
WHERE {?s ?p ?o 
} limit 100
		"""


start = timeit.default_timer()

_sparql = SPARQLWrapper("http://cittavld635.globoi.com:10035/repositories/globo")
_sparql.setCredentials(user = "super", passwd = "super")
_sparql.setQuery(query)
_sparql.setReturnFormat(JSON)
results = _sparql.query().convert()
entidades = results["results"]["bindings"]

stop = timeit.default_timer()

tempo_execucao = stop - start 

print tempo_execucao, "segundos"

for i in entidades:
	s = i['s']['value']
	p = i['p']['value']
	o = i['o']['value']
	print s, p, o
