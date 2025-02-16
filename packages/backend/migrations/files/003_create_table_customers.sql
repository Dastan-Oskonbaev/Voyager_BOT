CREATE TABLE "app"."customers" (
    "id" uuid NOT NULL,
    "username" varchar(255),
    "email" varchar(255),
    "created_at" Timestamp DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    "updated_at" Timestamp DEFAULT timezone('utc'::text, CURRENT_TIMESTAMP) NOT NULL,
    PRIMARY KEY ("id")
);

CREATE INDEX "idx_customers_username" ON "app"."customers" USING btree("username" ASC NULLS LAST);

CREATE UNIQUE INDEX "idx_customers_email_unique" ON "app"."customers" USING btree("email");
