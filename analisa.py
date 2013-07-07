# -*- coding: utf-8 -*-
import MySQLdb
EXECUCAO_ID = 55

if __name__ == '__main__':

	db = MySQLdb.connect("localhost","root","","PUC" )
	cursor = db.cursor()

	cursor.execute("""
		select origem, count(*)
		from materias
		where id_execucao = %s
		group by origem
		""", (56) )

	materias_origem = cursor.fetchall()

	for i in materias_origem:
		cursor.execute("""
			select destino
			from materias
			where id_execucao = %s
			and origem = %s
			order by score_final desc
			limit 5
			""", (56, i[0]) )
		
		materias_destino = cursor.fetchall()

		import pdb; pdb.set_trace()

		cursor.execute("""
			select destino
			from materias
			where id_execucao = %s
			and origem = %s
			order by score_final desc
			limit 5
			""", (56, i[0]) )
		materias_destino = cursor.fetchall()
		



