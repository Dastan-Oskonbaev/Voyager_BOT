
-- В этой таблице будем хранить пользователей, которые из телеграм или whatsapp. Просто их данные

CREATE TABLE "app"."chat_user" (
    "id" uuid NOT NULL,
    "tg_user_id" bigint NOT NULL, -- telegram user id
    "username" varchar(255),
    "first_name" varchar(255),
    "last_name" varchar(255),
    "full_name" varchar(255),
    "phone" varchar(255),
    "lang_code" varchar(5), -- 'ru', 'en', etc.
    "created_at" Timestamp DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    "updated_at" Timestamp DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    PRIMARY KEY ("id")
);

CREATE INDEX "idx_chat_user_username" ON  "app"."chat_user" USING btree( "username" Asc NULLS Last );

CREATE UNIQUE INDEX "idx_tg_unique_chat_user_tg_user_id"  ON  "app"."chat_user" USING btree( "tg_user_id" );
