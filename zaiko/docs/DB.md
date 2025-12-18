-- users（Supabase auth.users と紐づけ）
create table if not exists public.app_users (
  id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'user',
  created_at timestamptz not null default now()
);

create table if not exists public.products (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  sku text,
  jan text unique, -- EAN-13を文字列で保持
  price_in integer not null default 0, -- 税込単価（円）
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.inventory (
  product_id uuid primary key references public.products(id) on delete cascade,
  quantity integer not null default 0,
  updated_at timestamptz not null default now()
);

create type public.inventory_move_type as enum ('in','out','adjust');

create table if not exists public.inventory_movements (
  id uuid primary key default gen_random_uuid(),
  product_id uuid not null references public.products(id) on delete cascade,
  move_type public.inventory_move_type not null,
  qty integer not null,
  reason text,
  user_id uuid references auth.users(id),
  created_at timestamptz not null default now()
);

create type public.order_status as enum ('draft','confirmed','cancelled');

create table if not exists public.orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id),
  status public.order_status not null default 'confirmed',
  ordered_at timestamptz not null default now(),
  total_amount integer not null default 0
);

create table if not exists public.order_items (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references public.orders(id) on delete cascade,
  product_id uuid not null references public.products(id),
  quantity integer not null,
  unit_price_in integer not null,
  line_total integer not null
);

-- updated_at 自動更新（雑にトリガ）
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end; $$ language plpgsql;

drop trigger if exists trg_products_updated_at on public.products;
create trigger trg_products_updated_at
before update on public.products
for each row execute function public.set_updated_at();
