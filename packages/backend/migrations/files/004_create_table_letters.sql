CREATE TABLE "app"."letters" (
    "id" uuid NOT NULL,
    "title" varchar(255),
    "text" varchar(255),
    "created_at" Timestamp DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    "updated_at" Timestamp DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    PRIMARY KEY ("id")
);


INSERT INTO app.letters(id, title, text)
VALUES(
       gen_random_uuid(),
       'Файл для вас',
       'Здравствуйте! Высылаем вам запрошенный файл.'
      )