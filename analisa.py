# -*- coding: utf-8 -*-
import MySQLdb
import sys

EXECUCAO_ID = 92

if __name__ == '__main__':

	EXECUCAO_ID = sys.argv[1]

	acertos = 0

	db = MySQLdb.connect("localhost","root","","PUC" )
	cursor = db.cursor()

	cursor.execute("""
		select origem, count(*)
		from materias
		where id_execucao = %s
		group by origem
		""", (EXECUCAO_ID) )

	materias_origem = cursor.fetchall()

	for i in materias_origem:
		cursor.execute("""
			select destino
			from materias
			where id_execucao = %s
			and origem = %s
			order by score_final desc
			limit 5
			""", (EXECUCAO_ID, i[0]) )

		res = cursor.fetchall()

		materias_destino = (', '.join('"' + x[0] + '"' for x in res))

		# import pdb; pdb.set_trace()


		sql = """
			select distinct materia_principal
			from materias_saibamais
			where id_execucao = %s
			and materia_principal = '%s'
			and materia_saibamais in (%s) ;
			""" % (EXECUCAO_ID, i[0], materias_destino)

		cursor.execute(sql)

		materias_saibamais = cursor.fetchall()

		if len(materias_saibamais) > 0:
			acertos += 1
			print i[0]
			print "  ", ", ".join(materias_saibamais[0])
	print "Acertos:", acertos



