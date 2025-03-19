CREATE TABLE "app"."testers" (
    "id" uuid NOT NULL,
    "email" VARCHAR(255),
    "created_at" TIMESTAMP DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    "updated_at" TIMESTAMP DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    PRIMARY KEY ("id")
);
