CREATE TABLE "app"."letters" (
    "id" uuid NOT NULL,
    "title" VARCHAR(255),
    "text" TEXT,
    "created_at" TIMESTAMP DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    "updated_at" TIMESTAMP DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    PRIMARY KEY ("id")
);


INSERT INTO app.letters(id, title, text)
VALUES(
       gen_random_uuid(),
       'Файл для вас',
       'Здравствуйте! Высылаем вам запрошенный файл.'
      )