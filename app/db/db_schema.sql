-- подписка
CREATE TABLE public.subscriptions (
	id uuid NOT NULL,
	"name" varchar NOT NULL,
	price int4 NULL,
	description varchar NOT NULL,
	created_on timestamptz NOT NULL,
	updated_on timestamptz NOT NULL,
	CONSTRAINT subscriptions_name_key UNIQUE (name),
	CONSTRAINT subscriptions_pkey PRIMARY KEY (id)
);

-- пользователь
CREATE TABLE public.users (
	id uuid NOT NULL,
	"name" varchar NOT NULL,
	email varchar NOT NULL,
	created_on timestamptz NOT NULL,
	updated_on timestamptz NOT NULL,
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_pkey PRIMARY KEY (id)
);

-- покупка подписки
CREATE TABLE public.user_subscriptions (
	id uuid NOT NULL,
	expired_time timestamptz NOT NULL,
	created_on timestamptz NOT NULL,
	updated_on timestamptz NOT NULL,
	user_id uuid NULL,
	sub_id uuid NULL,
	CONSTRAINT user_subscriptions_pkey PRIMARY KEY (id)
);


-- public.user_subscriptions foreign keys

ALTER TABLE public.user_subscriptions ADD CONSTRAINT user_subscriptions_sub_id_fkey FOREIGN KEY (sub_id) REFERENCES public.subscriptions(id);
ALTER TABLE public.user_subscriptions ADD CONSTRAINT user_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
