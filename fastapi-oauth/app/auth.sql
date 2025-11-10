CREATE TABLE IF NOT EXISTS oauth_account (
  id INT AUTO_INCREMENT PRIMARY KEY,
  provider VARCHAR(50) NOT NULL,
  provider_sub VARCHAR(255) NOT NULL,
  staff_id TINYINT UNSIGNED NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_provider_sub (provider, provider_sub),
  CONSTRAINT fk_oauth_staff
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
