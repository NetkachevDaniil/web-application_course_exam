INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id) VALUES
    ('admin', 'pbkdf2:sha256:600000$tTDCwLblaluojqXl$1db3e52e652f22fd5ca941cf8c16c79e524a27b651702cfef382359db5348c5e', 'Неткачев', 'Даниил', 'Евгеньевич', 1),
    ('moderator', 'pbkdf2:sha256:600000$tTDCwLblaluojqXl$1db3e52e652f22fd5ca941cf8c16c79e524a27b651702cfef382359db5348c5e', 'Модеров', 'Модер', 'Модерович', 2),
    ('user1', 'pbkdf2:sha256:600000$tTDCwLblaluojqXl$1db3e52e652f22fd5ca941cf8c16c79e524a27b651702cfef382359db5348c5e', 'Петров', 'Пётр', 'Петрович', 3);

INSERT INTO reviews (book_id, user_id, rating, text, status_id) VALUES
    (1, 3, 5, E'**Шедевр** антиутопической литературы!\n\nОбязательно к прочтению.', 2),
    (4, 3, 4, 'Отличная книга для детей и взрослых.', 1),
    (5, 3, 3, 'Классический детектив, но предсказуемый.', 1);

INSERT INTO covers (filename, mime_type, md5_hash, book_id) VALUES
    ('1.png', 'image/png', '296f5ff741ea2c3d25fd48f6e49b78de', 1),
    ('2.png', 'image/png', '10b7c67ff219ceec955affd8626f3749', 2),
    ('3.png', 'image/png', '031f204090e28ee386e3383fbf110c94', 3),
    ('4.png', 'image/png', '3aa7439c609c888f0f073d0c04f5ff4b', 4),
    ('5.png', 'image/png', '06289d936f5447f88997d9fd03061a7c', 5),
    ('6.png', 'image/png', 'da0b2ece75e2c9ba3f4983a1f32adb03', 6),
    ('7.png', 'image/png', '24d8f3b237dca0fa5c4b2bac06b65e04', 7),
    ('8.png', 'image/png', '3d327ca27ba04cc04b94242ae6c6ad65', 8),
    ('9.png', 'image/png', '2cff69f1b952ecdb41f529954faf57e8', 9),
    ('10.png', 'image/png', 'dc525a7390703b982ead7dfaa0ab5299', 10),
    ('11.png', 'image/png', '274c18eeb5f00360b5be78b2df765939', 11),
    ('12.png', 'image/png', '13d616d0a8f364e8fd2542fc3b614780', 12);