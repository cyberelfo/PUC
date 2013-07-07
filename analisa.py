# -*- coding: utf-8 -*-
import MySQLdb
import sys

if __name__ == '__main__':

	db = MySQLdb.connect("localhost","root","","PUC" )
	cursor = db.cursor()

	max_recomendacoes_por_materia = 10

	id_execucao = sys.argv[1]

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
			""", (id_execucao, i[0], max_recomendacoes_por_materia) )

		res = cursor.fetchall()

		materias_destino = (', '.join('"' + x[0] + '"' for x in res))

		# import pdb; pdb.set_trace()

		sql = """
			select distinct materia_principal
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

	print "Acertos:", _acertos




