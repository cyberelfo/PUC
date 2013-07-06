# -*- coding: utf-8 -*-
import MySQLdb
from lxml import etree
import lxml.html as lh
from BeautifulSoup import BeautifulSoup, Tag

if __name__ == '__main__':

	lista_materias = []

	db_g1 = MySQLdb.connect("localhost","root","","g1" )
	cursor = db_g1.cursor()
	cursor.execute("""
					select permalink, corpo from materia m, materia_folder mf
					where m.primeira_publicacao >= '2013-03-07 00:00:00'
					and m.primeira_publicacao < '2013-03-10 00:00:00'
					and m.id = mf.materia_id
					and mf.folder_id = 42
					and corpo like '%<div class="saibamais componente_materia">%';
					""")
	# materias = cursor.fetchall()
	# for linha in materias:
	# 	print linha[0]

	materias = cursor.fetchall()
	for materia in materias:
		myparser = etree.HTMLParser(encoding="utf-8")
		tree = etree.HTML(materia[1], parser=myparser)
		
		# doc=lh.fromstring(html)
	#	for elem in tree.xpath('.//ul[@class="saibamais componente_materia"]/li'):
	#		print elem.text_content()
		
		text = etree.tostring(tree, pretty_print=True)
		text_a_partir_da_div = text[text.find('''<div class="saibamais componente_materia">'''):] #slicing
		soup = BeautifulSoup(text_a_partir_da_div)

		# list comprehension
		referencias = [(li.text,li.a['href']) for li in soup.ul if type(li) == Tag]

		lista_materias.append("http://g1.globo.com" + materia[0])
		print "\n>>> http://g1.globo.com" + materia[0]
		for ref in referencias:
			lista_materias.append(ref[1])
			print ref[1]

	# print lista_materias

	db_g1.close()

	#print referencias
		
