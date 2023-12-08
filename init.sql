\connect dailymotion_test;

-- Table: public.user

CREATE TABLE IF NOT EXISTS public."user"
(
    id UUID DEFAULT gen_random_uuid(),
    email character varying COLLATE pg_catalog."default" NOT NULL,
    password character varying COLLATE pg_catalog."default" NOT NULL,
    is_valid boolean NOT NULL DEFAULT false,
    created_at timestamp NOT NULL,
    updated_at timestamp,
    CONSTRAINT "user_pkey" PRIMARY KEY (id),
    CONSTRAINT unique_email UNIQUE (email)
);


-- Function: func_update_updated_at_user

CREATE OR REPLACE FUNCTION func_update_updated_at_user()
	RETURNS TRIGGER 
	  LANGUAGE PLPGSQL
	  AS
	$$
	BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
	$$;

-- Trigger: trigger_update_updated_at_user

CREATE OR REPLACE TRIGGER trigger_update_updated_at_user
    BEFORE UPDATE 
    ON public."user"
    FOR EACH ROW
    EXECUTE FUNCTION public.func_update_updated_at_user();

-- Table: public.2fa_code

CREATE TABLE IF NOT EXISTS public."2fa_code"
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    code smallint NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp NOT NULL,
    CONSTRAINT "2fa_code_pkey" PRIMARY KEY (id),
    CONSTRAINT user_id FOREIGN KEY (user_id)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)