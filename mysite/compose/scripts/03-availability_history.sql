CREATE TABLE IF NOT EXISTS AVAILABILITY_HISTORY(
    ID INT NOT NULL,
    LISTING_ID INT NOT NULL,
    IS_AVAILABLE TINYINT,
    CHANGED_AT DATETIME,

    PRIMARY KEY (ID),
    FOREIGN KEY (LISTING_ID) references LISTING(ID)
);

