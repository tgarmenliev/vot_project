DROP DATABASE IF EXISTS flapp;
CREATE DATABASE flapp;
use flapp;
GRANT ALL PRIVILEGES ON flapp.* TO 'fluser'@'%';

CREATE TABLE IF NOT EXISTS `urls` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `url` varchar(255) NOT NULL,
    `last_online` TIMESTAMP,
    `bounces` int(11) NOT NULL DEFAULT '0',
    `history` TEXT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `bounce_events` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `url_id` int(11) NOT NULL,
    `bounce_time` TIMESTAMP DEFAULT NULL,
    `status` varchar(255) NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `url_id_fk` FOREIGN KEY (`url_id`) REFERENCES `urls`(`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
