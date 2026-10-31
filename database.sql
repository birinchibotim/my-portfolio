-- ============================================================
--  TechZone — MySQL Ma'lumotlar Bazasi Strukturasi
--  Versiya: 1.0  |  Charset: utf8mb4
-- ============================================================

CREATE DATABASE IF NOT EXISTS techzone
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE techzone;

-- ──────────────────────────────────────────────────
--  1. KATEGORIYALAR
-- ──────────────────────────────────────────────────
CREATE TABLE categories (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  parent_id   INT DEFAULT NULL,              -- ichki kategoriya uchun
  name        VARCHAR(100) NOT NULL,
  slug        VARCHAR(120) NOT NULL UNIQUE,
  icon        VARCHAR(50),
  image       VARCHAR(255),
  sort_order  INT DEFAULT 0,
  is_active   TINYINT(1) DEFAULT 1,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- ──────────────────────────────────────────────────
--  2. BRENDLAR
-- ──────────────────────────────────────────────────
CREATE TABLE brands (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  slug       VARCHAR(120) NOT NULL UNIQUE,
  logo       VARCHAR(255),
  is_active  TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ──────────────────────────────────────────────────
--  3. MAHSULOTLAR
-- ──────────────────────────────────────────────────
CREATE TABLE products (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  category_id   INT NOT NULL,
  brand_id      INT,
  name          VARCHAR(255) NOT NULL,
  slug          VARCHAR(280) NOT NULL UNIQUE,
  sku           VARCHAR(100) UNIQUE,
  description   TEXT,
  price         DECIMAL(15,2) NOT NULL,
  discount_pct  TINYINT UNSIGNED DEFAULT 0,       -- foiz chegirma (0–90)
  price_final   DECIMAL(15,2)                     -- avtomatik hisoblash
    AS (price * (1 - discount_pct / 100)) STORED,
  stock         INT UNSIGNED DEFAULT 0,
  sold_count    INT UNSIGNED DEFAULT 0,
  rating        DECIMAL(3,2) DEFAULT 0.00,
  review_count  INT UNSIGNED DEFAULT 0,
  status        ENUM('active','inactive','low_stock','out_of_stock') DEFAULT 'active',
  is_featured   TINYINT(1) DEFAULT 0,
  is_new        TINYINT(1) DEFAULT 0,
  thumbnail     VARCHAR(255),
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id),
  FOREIGN KEY (brand_id)    REFERENCES brands(id) ON DELETE SET NULL,
  INDEX idx_price   (price_final),
  INDEX idx_status  (status),
  INDEX idx_cat     (category_id),
  FULLTEXT idx_search (name, description)
);

-- ──────────────────────────────────────────────────
--  4. MAHSULOT RASMLARI
-- ──────────────────────────────────────────────────
CREATE TABLE product_images (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  image_url  VARCHAR(255) NOT NULL,
  alt_text   VARCHAR(200),
  sort_order INT DEFAULT 0,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────
--  5. MAHSULOT XUSUSIYATLARI (spec)
-- ──────────────────────────────────────────────────
CREATE TABLE product_specs (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  spec_key   VARCHAR(100) NOT NULL,    -- "RAM", "Protsessor"
  spec_value VARCHAR(255) NOT NULL,   -- "16 GB", "Intel i7"
  sort_order INT DEFAULT 0,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────
--  6. FOYDALANUVCHILAR
-- ──────────────────────────────────────────────────
CREATE TABLE users (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  name           VARCHAR(150) NOT NULL,
  email          VARCHAR(180) NOT NULL UNIQUE,
  phone          VARCHAR(20),
  password_hash  VARCHAR(255) NOT NULL,
  avatar         VARCHAR(255),
  role           ENUM('customer','admin','superadmin') DEFAULT 'customer',
  is_active      TINYINT(1) DEFAULT 1,
  email_verified TINYINT(1) DEFAULT 0,
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login     TIMESTAMP,
  INDEX idx_email (email),
  INDEX idx_role  (role)
);

-- ──────────────────────────────────────────────────
--  7. FOYDALANUVCHI MANZILLARI
-- ──────────────────────────────────────────────────
CREATE TABLE user_addresses (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  label      VARCHAR(60) DEFAULT 'Uy',   -- "Uy", "Ish", "Boshqa"
  full_name  VARCHAR(150),
  phone      VARCHAR(20),
  region     VARCHAR(100),
  city       VARCHAR(100),
  address    TEXT,
  is_default TINYINT(1) DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────
--  8. BUYURTMALAR
-- ──────────────────────────────────────────────────
CREATE TABLE orders (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT,                              -- NULL = mehmon
  address_id      INT,
  order_number    VARCHAR(30) NOT NULL UNIQUE,      -- #TZ-2025-4821
  status          ENUM(
                    'pending','confirmed','processing',
                    'shipped','delivered','cancelled','refunded'
                  ) DEFAULT 'pending',
  payment_method  ENUM('card','cash','payme','click','uzum') DEFAULT 'card',
  payment_status  ENUM('unpaid','paid','refunded') DEFAULT 'unpaid',
  subtotal        DECIMAL(15,2) NOT NULL,
  discount_amount DECIMAL(15,2) DEFAULT 0,
  delivery_cost   DECIMAL(10,2) DEFAULT 0,
  total           DECIMAL(15,2) NOT NULL,
  note            TEXT,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)    REFERENCES users(id)          ON DELETE SET NULL,
  FOREIGN KEY (address_id) REFERENCES user_addresses(id) ON DELETE SET NULL,
  INDEX idx_status (status),
  INDEX idx_user   (user_id)
);

-- ──────────────────────────────────────────────────
--  9. BUYURTMA TARKIBI
-- ──────────────────────────────────────────────────
CREATE TABLE order_items (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  order_id    INT NOT NULL,
  product_id  INT NOT NULL,
  product_name VARCHAR(255) NOT NULL,   -- snapshot (o'zgarmaydi)
  unit_price  DECIMAL(15,2) NOT NULL,
  quantity    INT UNSIGNED NOT NULL DEFAULT 1,
  total_price DECIMAL(15,2)
    AS (unit_price * quantity) STORED,
  FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

-- ──────────────────────────────────────────────────
--  10. KORZINA (SAVAT)
-- ──────────────────────────────────────────────────
CREATE TABLE cart (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT,                    -- NULL = session orqali
  session_id VARCHAR(128),
  product_id INT NOT NULL,
  quantity   INT UNSIGNED DEFAULT 1,
  added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────
--  11. SEVIMLILAR
-- ──────────────────────────────────────────────────
CREATE TABLE wishlist (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  product_id INT NOT NULL,
  added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_wish (user_id, product_id),
  FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────
--  12. SHARHLAR (REVIEWS)
-- ──────────────────────────────────────────────────
CREATE TABLE reviews (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  user_id    INT NOT NULL,
  rating     TINYINT UNSIGNED NOT NULL CHECK (rating BETWEEN 1 AND 5),
  title      VARCHAR(200),
  body       TEXT,
  is_verified TINYINT(1) DEFAULT 0,  -- tasdiqlangan xaridor
  is_visible  TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_review (product_id, user_id),
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE
);

-- ──────────────────────────────────────────────────
--  13. PROMO KODLAR
-- ──────────────────────────────────────────────────
CREATE TABLE coupons (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  code            VARCHAR(50) NOT NULL UNIQUE,
  type            ENUM('percent','fixed') DEFAULT 'percent',
  value           DECIMAL(10,2) NOT NULL,
  min_order_amount DECIMAL(15,2) DEFAULT 0,
  usage_limit     INT DEFAULT NULL,
  used_count      INT DEFAULT 0,
  is_active       TINYINT(1) DEFAULT 1,
  expires_at      DATETIME,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ──────────────────────────────────────────────────
--  14. BANNERLAR (SLIDER)
-- ──────────────────────────────────────────────────
CREATE TABLE banners (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  title      VARCHAR(200),
  subtitle   VARCHAR(300),
  image      VARCHAR(255) NOT NULL,
  link_url   VARCHAR(255),
  sort_order INT DEFAULT 0,
  is_active  TINYINT(1) DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ──────────────────────────────────────────────────
--  15. SAYT SOZLAMALARI
-- ──────────────────────────────────────────────────
CREATE TABLE settings (
  id    INT AUTO_INCREMENT PRIMARY KEY,
  key_  VARCHAR(100) NOT NULL UNIQUE,
  value TEXT,
  group_ VARCHAR(50) DEFAULT 'general'
);

-- Dastlabki sozlamalar
INSERT INTO settings (key_, value, group_) VALUES
  ('site_name',        'TechZone',            'general'),
  ('site_email',       'info@techzone.uz',    'general'),
  ('site_phone',       '+998 90 000 00 00',   'general'),
  ('currency',         'UZS',                 'general'),
  ('free_delivery_min','50000',               'delivery'),
  ('delivery_cost',    '15000',               'delivery');

-- ──────────────────────────────────────────────────
--  NAMUNAVIY MA'LUMOTLAR
-- ──────────────────────────────────────────────────

-- Kategoriyalar
INSERT INTO categories (name, slug, icon) VALUES
  ('Noutbuklar',    'noutbuklar',    '💻'),
  ('Smartfonlar',   'smartfonlar',   '📱'),
  ('Kompyuterlar',  'kompyuterlar',  '🖥️'),
  ('Monitorlar',    'monitorlar',    '🖥'),
  ('Audio',         'audio',         '🎧'),
  ('Gaming',        'gaming',        '🎮'),
  ('Kameralar',     'kameralar',     '📷'),
  ('Aksessuarlar',  'aksessuarlar',  '🔌');

-- Brendlar
INSERT INTO brands (name, slug) VALUES
  ('Apple',   'apple'),
  ('Samsung', 'samsung'),
  ('ASUS',    'asus'),
  ('HP',      'hp'),
  ('Lenovo',  'lenovo'),
  ('Sony',    'sony'),
  ('Xiaomi',  'xiaomi'),
  ('MSI',     'msi');

-- Admin foydalanuvchi (parol: admin123 — bcrypt hash)
INSERT INTO users (name, email, password_hash, role) VALUES
  ('Alibek Karimov', 'admin@techzone.uz',
   '$2y$12$ExampleHashHere', 'superadmin');
