-- Генерация тестовых данных для парфюмерной системы

-- Очистка таблиц (если нужно)
-- TRUNCATE TABLE ratings, perfume_notes, perfumes, brands, notes, users CASCADE;

-- 1. Концентрации
INSERT INTO concentration (concentration_title) VALUES
('Eau Fraiche (ароматическая вода)'),
('Eau de Cologne (одеколон)'),
('Eau de Toilette (туалетная вода)'),
('Eau de Parfum (парфюмированная вода)'),
('Parfum (духи)'),
('Extrait de Parfum (экстракт духов)');

-- 2. Пользователи (5 пользователей)
INSERT INTO users (nickname, password_enc, email, reg_date) VALUES
('Анна_Иванова', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'anna@example.com', '2023-01-15'),
('Петр_Смирнов', '01c4c0092dc6f090f2d58115c9df6aaebdd5adc595df12bd5dffcc8eaae33006', 'petr@example.com', '2023-02-20'),
('Мария_Петрова', '3deff660926494dc46d9fb6b56c3fcb766d2e00c6ddf818729c3536606867164', 'maria@example.com', '2023-03-10'),
('Иван_Сидоров', 'bd94dcda26fccb4e68d6a31f9b5aac0b571ae266d822620e901ef7ebe3a11d4f', 'ivan@example.com', '2023-04-05'),
('Ольга_Кузнецова', '869e75776f6b3e950a66793b6e5b8e53d533d3297290c5c7c431491ffa5a2844', 'olga@example.com', '2023-05-12');

-- 3. Бренды (5 брендов)
INSERT INTO brands (name) VALUES
('Chanel'),
('Dior'),
('Tom Ford'),
('Yves Saint Laurent'),
('Guerlain');

-- 4. Заметки (ароматические ноты) - 20 заметок
INSERT INTO notes (note_name) VALUES
('Цитрус'),
('Цветочные'),
('Древесные'),
('Пряные'),
('Фруктовые'),
('Зеленые'),
('Восточные'),
('Мускусные'),
('Морские'),
('Ванильные'),
('Кожаные'),
('Табачные'),
('Кедровые'),
('Сандаловые'),
('Жасминовые'),
('Розовые'),
('Лавандовые'),
('Амбровые'),
('Пачули'),
('Ирисовые');

INSERT INTO note_types (note_type_data) VALUES
('top'),
('middle'),
('base');

-- 5. Духи (10 духов, по 2 на бренд)
-- Для концентраций: 3 - EDT, 4 - EDP, 5 - PAR
INSERT INTO perfumes (name, brand_id, photo, concentration_id, price) VALUES
('Chanel No. 5', 1, 'chanel_no5.jpg', 4, 12500),           -- EDP
('Chance Eau Tendre', 1, 'chance_tendre.jpg', 3, 9500),    -- EDT
('Miss Dior', 2, 'miss_dior.jpg', 4, 11500),                -- EDP
('Sauvage', 2, 'sauvage.jpg', 3, 10500),                    -- EDT
('Black Orchid', 3, 'black_orchid.jpg', 5, 18500),          -- PAR
('Tobacco Vanille', 3, 'tobacco_vanille.jpg', 4, 22000),   -- EDP
('Black Opium', 4, 'black_opium.jpg', 4, 9800),             -- EDP
('Libre', 4, 'libre.jpg', 4, 12000),                        -- EDP
('Shalimar', 5, 'shalimar.jpg', 4, 13500),                  -- EDP
('Mon Guerlain', 5, 'mon_guerlain.jpg', 4, 12800);          -- EDP

-- 5. Связь духов и нот (perfume_notes) - 3-4 ноты на каждый парфюм
INSERT INTO perfume_notes (perfume_id, note_id, note_type_id) VALUES
-- Chanel No. 5
(1, 15, 1),     -- Жасмин
(1, 16, 2),  -- Роза
(1, 19, 3),    -- Пачули

-- Chance Eau Tendre
(2, 5, 1),      -- Фруктовые
(2, 2, 2),   -- Цветочные
(2, 10, 3),    -- Ванильные

-- Miss Dior
(3, 16, 1),     -- Роза
(3, 15, 2),  -- Жасмин
(3, 3, 3),     -- Древесные

-- Sauvage
(4, 1, 1),      -- Цитрус
(4, 4, 2),   -- Пряные
(4, 12, 3),    -- Табачные

-- Black Orchid
(5, 17, 1),     -- Лаванда
(5, 7, 2),   -- Восточные
(5, 11, 3),    -- Кожаные

-- Tobacco Vanille
(6, 12, 1),     -- Табачные
(6, 10, 2),  -- Ванильные
(6, 8, 3),     -- Мускусные

-- Black Opium
(7, 10, 1),     -- Ванильные
(7, 14, 2),  -- Сандаловые
(7, 7, 3),     -- Восточные

-- Libre
(8, 15, 1),     -- Жасмин
(8, 14, 2),  -- Сандаловые
(8, 3, 3),     -- Древесные

-- Shalimar
(9, 1, 1),      -- Цитрус
(9, 2, 2),   -- Цветочные
(9, 18, 3),    -- Амбровые

-- Mon Guerlain
(10, 16, 1),    -- Роза
(10, 10, 2), -- Ванильные
(10, 3, 3);    -- Древесные

-- 6. Рейтинги (каждый пользователь оценил 3-4 парфюма)
INSERT INTO ratings (user_id, perfume_id, rate, rate_date) VALUES
-- Анна оценила 3 парфюма
(1, 1, 5, '2023-06-10'),
(1, 3, 4, '2023-06-12'),
(1, 7, 5, '2023-06-15'),

-- Петр оценил 4 парфюма
(2, 2, 3, '2023-07-01'),
(2, 4, 5, '2023-07-05'),
(2, 6, 4, '2023-07-08'),
(2, 8, 3, '2023-07-10'),

-- Мария оценила 3 парфюма
(3, 1, 4, '2023-08-03'),
(3, 5, 5, '2023-08-05'),
(3, 9, 4, '2023-08-07'),

-- Иван оценил 4 парфюма
(4, 2, 4, '2023-09-01'),
(4, 4, 5, '2023-09-03'),
(4, 6, 3, '2023-09-05'),
(4, 10, 4, '2023-09-07'),

-- Ольга оценила 3 парфюма
(5, 3, 5, '2023-10-01'),
(5, 7, 4, '2023-10-03'),
(5, 9, 5, '2023-10-05');
