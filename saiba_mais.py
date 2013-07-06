# -*- coding: utf-8 -*-
import MySQLdb
from lxml import etree
import lxml.html as lh
from BeautifulSoup import BeautifulSoup, Tag

if __name__ == '__main__':

	db = MySQLdb.connect("localhost","root","","g1" )
	cursor = db.cursor()
	cursor.execute("""select id, corpo from materia where corpo like '%<div class="saibamais componente_materia">%'  limit 10;""")
	# materias = cursor.fetchall()
	# for linha in materias:
	# 	print linha[0]

	materia = cursor.fetchone()
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

	for ref in referencias:
		print ref[0], "->", ref[1]

	#print referencias
		
