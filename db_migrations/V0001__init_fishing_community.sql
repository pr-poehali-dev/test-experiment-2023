
-- Участники сообщества
CREATE TABLE t_p53092451_test_experiment_2023.members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    joined_year INTEGER,
    location VARCHAR(100),
    favorite_fish VARCHAR(100),
    trips_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Водоёмы
CREATE TABLE t_p53092451_test_experiment_2023.spots (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    region VARCHAR(100),
    fish_types TEXT,
    difficulty VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Выезды
CREATE TABLE t_p53092451_test_experiment_2023.trips (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    spot_id INTEGER REFERENCES t_p53092451_test_experiment_2023.spots(id),
    date DATE NOT NULL,
    participants_count INTEGER DEFAULT 0,
    organizer VARCHAR(100),
    status VARCHAR(20) DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Тестовые участники
INSERT INTO t_p53092451_test_experiment_2023.members (name, role, joined_year, location, favorite_fish, trips_count) VALUES
('Алексей Громов', 'Основатель', 2012, 'Москва', 'Щука', 87),
('Сергей Ильин', 'Организатор выездов', 2015, 'Подмосковье', 'Судак', 64),
('Виктор Смолов', 'Эксперт по снастям', 2018, 'Тверь', 'Окунь', 41),
('Николай Петров', 'Участник', 2019, 'Рязань', 'Карп', 28),
('Дмитрий Козлов', 'Участник', 2020, 'Москва', 'Лещ', 19),
('Игорь Федоров', 'Старший участник', 2016, 'Ярославль', 'Форель', 55),
('Андрей Волков', 'Участник', 2021, 'Тула', 'Плотва', 12),
('Максим Соколов', 'Участник', 2022, 'Калуга', 'Карась', 7);

-- Тестовые водоёмы
INSERT INTO t_p53092451_test_experiment_2023.spots (name, region, fish_types, difficulty) VALUES
('Озеро Сенеж', 'Подмосковье', 'Щука, Окунь, Лещ', 'easy'),
('Река Ока', 'Рязанская обл.', 'Судак, Сом, Жерех', 'medium'),
('Рыбинское водохранилище', 'Ярославская обл.', 'Щука, Судак, Налим', 'hard'),
('Озеро Плещеево', 'Переславль', 'Ряпушка, Окунь, Щука', 'medium'),
('Река Угра', 'Калужская обл.', 'Форель, Хариус, Голавль', 'hard'),
('Пруд Истра', 'Подмосковье', 'Карп, Карась, Плотва', 'easy');

-- Тестовые выезды
INSERT INTO t_p53092451_test_experiment_2023.trips (title, spot_id, date, participants_count, organizer, status) VALUES
('Открытие сезона 2026', 1, '2026-04-20', 14, 'Сергей Ильин', 'planned'),
('Весенний выезд на Оку', 2, '2026-05-10', 8, 'Алексей Громов', 'planned'),
('Рыбалка на Рыбинке', 3, '2026-03-15', 12, 'Игорь Федоров', 'completed'),
('Зимняя форелевая', 5, '2026-02-08', 6, 'Виктор Смолов', 'completed'),
('Летний сбор на Плещеево', 4, '2026-07-05', 20, 'Сергей Ильин', 'planned');
