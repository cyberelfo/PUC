Instalação
----------

É necessário tem instalado na sua máquina o Openlink Virtuoso e o MySQL.

Instale as dependencias do programa com o pip:

pip install MySQL-python
pip install networkx
pip install lxml
sudo STATIC_DEPS=true /usr/bin/easy_install-2.7 lxml
pip install BeautifulSoup
pip install SPARQLWrapper

Em seguida, crie as tabelas no MySQL com o script modelo.sql.

Por fim copie o programa para o seu computador.

Execução
--------

O programa é executado via linha de comando, conforme abaixo:

python graph.py <editoria> <data_inicio> <data_fim>

Para executar para todas as editorias do G1 no intervalo de 01 à 10 de janeiro de 2013 rode o script run.sh.