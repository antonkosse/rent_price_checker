CREATE TABLE IF NOT EXISTS EMAIL_VERIFICATION_TOKENS (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    EMAIL VARCHAR(255) NOT NULL,
    TOKEN VARCHAR(64) NOT NULL,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    EXPIRES_AT TIMESTAMP NOT NULL,
    USED BOOLEAN DEFAULT FALSE,

        -- Fields for tracking email status
--      claude generated it, not sure if it should be in a single table
--      or if it should be at all
    status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    error_message TEXT,
    retry_count INT DEFAULT 0,

    INDEX (token),
    INDEX (email),
    INDEX (status)
);