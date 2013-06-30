-- Create syntax for '(null)'

-- Create syntax for TABLE 'individuos'
CREATE TABLE `individuos` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `origem` varchar(255) DEFAULT NULL,
  `destino` varchar(255) DEFAULT NULL,
  `path` text,
  `tamanho` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=533343 DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'materias'
CREATE TABLE `materias` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `origem` varchar(255) DEFAULT NULL,
  `destino` varchar(255) DEFAULT NULL,
  `score` float DEFAULT NULL,
  `entidades_origem` int(11) DEFAULT NULL,
  `entidades_destino` int(11) DEFAULT NULL,
  `intercessao` int(11) DEFAULT NULL,
  `score_final` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50813 DEFAULT CHARSET=utf8;
