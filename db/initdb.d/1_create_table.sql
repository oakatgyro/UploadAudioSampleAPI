
CREATE TABLE user (
    user_id INTEGER PRIMARY KEY
);

CREATE TABLE phrase (
    phrase_id INTEGER PRIMARY KEY 
);

CREATE TABLE user_phrase_audio (
    user_id INTEGER NOT NULL,
    phrase_id INTEGER NOT NULL,
    audio_path VARCHAR(255) NOT NULL,
    created_at Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, phrase_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (phrase_id) REFERENCES phrase(phrase_id)
);