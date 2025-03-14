CREATE TABLE IF NOT EXISTS USER_WATCHLIST(
    ID INT NOT NULL,
    LISTING_ID INT NOT NULL,
    USER_EMAIL VARCHAR(255),
    NOTIFY_ON_PRICE_CHANGE TINYINT,
    NOTIFY_ON_AVAILABILITY_CHANGE TINYINT,
    CREATED_AT DATETIME,

    PRIMARY KEY (ID),
    FOREIGN KEY (LISTING_ID) references LISTING(ID)
);