CREATE DATABASE blog_joaoguilherme;

USE blog_joaoguilherme;

CREATE TABLE users (
    idUser INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(60) NOT NULL,
    userName VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE, 
    passwordHash VARCHAR(255) NOT NULL,
    picture VARCHAR(100),
    registrationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE post (
    idPost INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    postDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idUser INT,
    FOREIGN KEY (idUser) REFERENCES users(idUser) ON DELETE CASCADE
);

-- ALTER TABLE users 
-- ADD ativo BOOLEAN NOT NULL DEFAULT 1;

-- CADASTRAR USUÁRIO DE TESTE
-- INSERT INTO users (name, userName, email, passwordHash, picture) VALUES ('teste', 'teste', 'teste');

-- PARA ZERAR A TABELA POST
-- TRUNCATE post;

DROP VIEW IF EXISTS vw_total_post;
CREATE VIEW vw_total_post AS
SELECT COUNT(*) AS total_posts FROM post p
JOIN users u ON p.idUser = u.idUser
WHERE u.ativo = 1;

DROP VIEW IF EXISTS vw_usuarios;
CREATE VIEW vw_usuarios AS
SELECT COUNT(*) AS total_usuarios FROM users u
WHERE u.ativo = 1;