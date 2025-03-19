CREATE TYPE app.user_state_enum AS ENUM ('main-page', 'enter-password', 'send-email', 'contragents', 'add_agent_email',
    'add_agent_name', 'delete_agent', 'redact_agent', 'redact_agent_email', 'redact_agent_username',
    'change_letter_text', 'change_letter_title', 'send_test_email', 'add_tester', 'delete_tester');
-- Таблица для конкретно чата телеграм. Здесь не учитываются сообщения с ИИ. Только чисто для настроек.
CREATE TABLE "app"."chat" (
    "id" uuid NOT NULL,
    "tg_chat_id" bigint NOT NULL, -- telegram chat id
    "user_id" uuid NOT NULL,
    "lang_code" varchar(5) NOT NULL DEFAULT 'ru', -- ru, en, etc. На каком языке выбрано общение с человеком
    "state" app.user_state_enum, -- На каком этапе находится чат. TODO: add enum
    "created_at" Timestamp DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    "updated_at" Timestamp DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    PRIMARY KEY ("id"),

    CONSTRAINT fk_chat_user_id FOREIGN KEY ("user_id")
        REFERENCES "app"."chat_user" ("id")
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX "idx_app_chat_tg_chat_id"  ON  "app"."chat" USING btree( "tg_chat_id" Asc NULLS Last );
CREATE INDEX "idx_tg_chat_state"           ON  "app"."chat" USING btree( "state" Asc NULLS Last );
CREATE UNIQUE INDEX "idx_tg_chat_user_id"  ON  "app"."chat" USING btree( "user_id" Asc NULLS Last );
