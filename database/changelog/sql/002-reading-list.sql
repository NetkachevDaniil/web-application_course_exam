--liquibase formatted sql

--changeset netkachev:002-reading-list
--comment: Список «Хочу прочитать» пользователя и представление для его вывода
CREATE TABLE reading_list (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, book_id)
);

CREATE INDEX idx_reading_list_user ON reading_list (user_id);

CREATE VIEW reading_list_details AS
SELECT rl.id, rl.user_id, rl.added_at, b.id AS book_id, b.title, b.author, b.year
FROM reading_list rl
JOIN books b ON b.id = rl.book_id;
--rollback DROP VIEW reading_list_details;
--rollback DROP TABLE reading_list;
