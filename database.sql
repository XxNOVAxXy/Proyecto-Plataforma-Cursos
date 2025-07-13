-- Creación de la base de datos si no existe, con el formato de caracteres correcto para español.
CREATE DATABASE IF NOT EXISTS plataforma_cursos 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Usar la base de datos que acabamos de crear.
USE plataforma_cursos;

-- -----------------------------------------------------
-- Tabla `instructores`
-- Se crea primero porque otras tablas dependen de ella.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS instructores (
  id INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE, -- El email debe ser único para evitar duplicados
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);


-- -----------------------------------------------------
-- Tabla `cursos`
-- Depende de `instructores`.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cursos (
  id INT NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(255) NOT NULL,
  descripcion TEXT NULL,
  is_published BOOLEAN NOT NULL DEFAULT FALSE, -- Campo CRÍTICO para la regla de negocio. Por defecto, un curso no está publicado.
  instructor_id INT NULL, -- Puede ser nulo si el instructor es eliminado
  PRIMARY KEY (id),
  FOREIGN KEY (instructor_id) REFERENCES instructores (id)
    ON DELETE SET NULL -- Si se borra un instructor, el curso no se borra, solo se desvincula.
    ON UPDATE CASCADE
);


-- -----------------------------------------------------
-- Tabla `modulos`
-- Depende de `cursos`.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS modulos (
  id INT NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(255) NOT NULL,
  curso_id INT NOT NULL, -- Un módulo siempre debe pertenecer a un curso.
  PRIMARY KEY (id),
  FOREIGN KEY (curso_id) REFERENCES cursos (id)
    ON DELETE CASCADE -- Si se borra un curso, todos sus módulos se borran automáticamente.
    ON UPDATE CASCADE
);


-- -----------------------------------------------------
-- Tabla `lecciones`
-- Depende de `modulos`.
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS lecciones (
  id INT NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(255) NOT NULL,
  contenido TEXT NULL,
  modulo_id INT NOT NULL, -- Una lección siempre debe pertenecer a un módulo.
  PRIMARY KEY (id),
  FOREIGN KEY (modulo_id) REFERENCES modulos (id)
    ON DELETE CASCADE -- Si se borra un módulo, todas sus lecciones se borran automáticamente.
    ON UPDATE CASCADE
);