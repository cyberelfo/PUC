-- Create syntax for TABLE 'execucao'
CREATE TABLE `execucao` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `produto` varchar(50) DEFAULT NULL,
  `editoria` varchar(255) DEFAULT NULL,
  `dt_inicio` datetime DEFAULT NULL,
  `dt_fim` datetime DEFAULT NULL,
  `supernode` int(11) DEFAULT NULL,
  `max_path` int(11) DEFAULT NULL,
  `materias` int(11) DEFAULT NULL,
  `max_recomendacoes_por_materia` int(11) DEFAULT NULL,
  `acertos` int(11) DEFAULT NULL,
  `nos` int(11) DEFAULT NULL,
  `arestas` int(11) DEFAULT NULL,
  `tempo_execucao` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'grafo'
CREATE TABLE `grafo` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `s` varchar(750) DEFAULT NULL,
  `p` varchar(750) DEFAULT NULL,
  `o` varchar(750) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

-- Create syntax for TABLE 'materias'
CREATE TABLE `materias` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `id_execucao` int(11) DEFAULT NULL,
  `origem` varchar(750) DEFAULT NULL,
  `destino` varchar(750) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `entidades_origem` int(11) DEFAULT NULL,
  `entidades_destino` int(11) DEFAULT NULL,
  `intercessao` int(11) DEFAULT NULL,
  `score_final` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_execucao` (`id_execucao`),
  KEY `id_execucao` (`id_execucao`,`origem`(255))
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'materias_saibamais'
CREATE TABLE `materias_saibamais` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `id_execucao` int(11) DEFAULT NULL,
  `materia_principal` varchar(750) DEFAULT NULL,
  `materia_saibamais` varchar(750) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'paths'
CREATE TABLE `paths` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `id_execucao` int(11) DEFAULT NULL,
  `origem` varchar(750) DEFAULT NULL,
  `destino` varchar(750) DEFAULT NULL,
  `path` text,
  `tamanho` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_execucao` (`id_execucao`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;