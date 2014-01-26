import unittest
from graph import *
class GraphTestCase(unittest.TestCase):
	def test_cria_grafo(self):
		g = cria_grafo()
		self.assertEqual(g.__class__.__name__, "Graph")

	def test_busca_entidade(self):
		esperado = [{u'p': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#domain'}, u's': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/genero_gramatical'}, u'o': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Organizacao'}}, {u'p': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#domain'}, u's': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/path_topico'}, u'o': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Assunto'}}]
		computado = busca_entidades("G1", 2)
		self.assertEqual(esperado, computado)

	def test_carrega_grafo(self):
		grafo = cria_grafo()
		items = [{u'p': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#domain'}, u's': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/genero_gramatical'}, u'o': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Organizacao'}}, {u'p': {u'type': u'uri', u'value': u'http://www.w3.org/2000/01/rdf-schema#domain'}, u's': {u'type': u'uri', u'value': u'http://semantica.globo.com/G1/path_topico'}, u'o': {u'type': u'uri', u'value': u'http://semantica.globo.com/base/Assunto'}}]
		carrega_grafo(grafo, items)
		self.assertEqual(len(grafo), 4)

	def test_carrega_grafo_from_mysql(self):
		grafo = cria_grafo()
		db = MySQLdb.connect("localhost","root","","PUC" )
		cursor = db.cursor()
		carrega_grafo_from_mysql(cursor, grafo)
		self.assertGreater(len(grafo), 0)

	def test_remove_supernode(self):
		grafo = cria_grafo()
		grafo.add_edges_from([(1,2),(1,3),(1,4),(1,5),(1,6),(2,3),(2,4),(2,5)])
		remove_supernode(grafo, 4)
		self.assertEqual(grafo.number_of_nodes(), 5)

	def test_calcula_path(self):
		db = MySQLdb.connect("localhost","root","","PUC" )
		lista_materias = {"a": ["1","2"],"b": ["1","5"], "c": ["4"], "d": ["7"]}
		grafo = cria_grafo()
		grafo.add_edges_from([("1","2"),("2","3"),("3","4"),("4","5"),("1","6"),("6","7")])
		calcula_path(lista_materias, grafo, 10, True, db, 999999)
		cursor = db.cursor()
		cursor.execute("""select path, tamanho
						from paths
						where id_execucao = 999999
						and origem = 'c'
						and destino = 'b'""")
		resultado = cursor.fetchone()
		cursor.execute("""delete from paths
						where id_execucao = 999999""")
		cursor.execute("""delete from materias
						where id_execucao = 999999""")
		db.commit()

		self.assertEqual(resultado[0], "4,5")
		self.assertEqual(resultado[1], 2)

	def test_busca_materias_saibamais(self):
		db = MySQLdb.connect("localhost","root","","PUC" )
		esperado = {u'http://g1.be.globoi.com/noticia/1024839': [u'http://semantica.globo.com/base/Cidade_Rio_de_Janeiro_RJ', u'http://semantica.globo.com/base/Produto_G1'], u'http://g1.be.globoi.com/noticia/1024866': [u'http://semantica.globo.com/base/Cidade_Rio_de_Janeiro_RJ', u'http://semantica.globo.com/base/Produto_G1']}
		computado = busca_materias_saibamais("2013-01-01 00:00:00", "2013-01-10 00:00:00", 42, 4, db, 999999)
		self.assertEqual(esperado, computado)

	def test_grava_execucao(self):
		db = MySQLdb.connect("localhost","root","","PUC" )
		grava_execucao("TESTE", "2013-01-01 00:00:00", "2013-01-10 00:00:00", 5, 10, 42, db)
		cursor = db.cursor()
		cursor.execute("""select count(*) from execucao
						where produto = 'TESTE'""")
		resultado = cursor.fetchone()
		cursor.execute("""delete from execucao
						where produto = 'TESTE'""")
		db.commit()
		self.assertEqual(resultado[0], 1)

	def test_atualiza_execucao(self):
		db = MySQLdb.connect("localhost","root","","PUC" )
		cursor = db.cursor()
		cursor.execute("""INSERT INTO execucao (id, produto, editoria, dt_inicio, dt_fim, supernode, max_path, materias, max_recomendacoes_por_materia, acertos, nos, arestas, tempo_execucao)
							VALUES
							(999999, 'TESTE', '42', '2013-01-01 00:00:00', '2013-01-10 00:00:00', 5, 10, NULL, NULL, NULL, NULL, NULL, NULL);
						""")
		db.commit()
		atualiza_execucao(999999, 10, 20, 30, db)
		cursor = db.cursor()
		cursor.execute("""select materias, nos, arestas from execucao
						where id = 999999""")
		resultado = cursor.fetchone()
		cursor.execute("""delete from execucao
						where id = 999999""")
		db.commit()
		self.assertEqual(resultado[0], 10)
		self.assertEqual(resultado[1], 20)
		self.assertEqual(resultado[2], 30)

	def test_analisa_resultado(self):
		db = MySQLdb.connect("localhost","root","","PUC" )
		cursor = db.cursor()
		cursor.execute("""INSERT INTO materias_saibamais (id_execucao, materia_principal, materia_saibamais)
							VALUES
								(999999, 'a', 'b');
						""")
		cursor.execute("""INSERT INTO paths (id_execucao, origem, destino, path, tamanho)
							VALUES
								(999999, 'a', 'c', '1,2,3,4', 4),
								(999999, 'a', 'c', '2,3,4', 3),
								(999999, 'a', 'b', '1,2,3,4,5', 5),
								(999999, 'a', 'b', '2,1', 2),
								(999999, 'a', 'b', '2,3,4,5', 4),
								(999999, 'a', 'd', '1,6,7', 3),
								(999999, 'a', 'd', '2,1,6,7', 4),
								(999999, 'c', 'b', '4,5', 2),
								(999999, 'c', 'd', '4,3,2,1,6,7', 6),
								(999999, 'b', 'd', '5,4,3,2,1,6,7', 7);
						""")
		cursor.execute("""INSERT INTO materias (id_execucao, origem, destino, score, entidades_origem, entidades_destino, intercessao, score_final)
							VALUES
								(999999, 'a', 'c', 0.1875, 2, 1, 0, 0.09375),
								(999999, 'a', 'b', 0.3125, 2, 2, 1, 0.328125),
								(999999, 'a', 'd', 0.1875, 2, 1, 0, 0.09375),
								(999999, 'c', 'b', 0.25, 1, 2, 0, 0.125),
								(999999, 'c', 'd', 0, 1, 1, 0, 0),
								(999999, 'b', 'd', 0, 2, 1, 0, 0);
						""")
		db.commit()		
		self.assertEqual(analisa_resultado(999999, 10, db), 1)
		cursor.execute("""delete from materias_saibamais
						where id_execucao = 999999""")
		cursor.execute("""delete from paths
						where id_execucao = 999999""")
		cursor.execute("""delete from materias
						where id_execucao = 999999""")
		db.commit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
