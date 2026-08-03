create extension if not exists "pgcrypto";

create table public.portfolios (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    name text not null,
    base_currency char(3) not null default 'GBP',
    benchmark_ticker text not null default 'SPY',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.securities (
    id uuid primary key default gen_random_uuid(),
    ticker text not null,
    exchange text not null default '',
    name text not null,
    asset_type text not null default 'equity',
    currency char(3) not null default 'USD',
    sector text,
    country text,
    unique (ticker, exchange)
);

create table public.transactions (
    id uuid primary key default gen_random_uuid(),
    portfolio_id uuid not null references public.portfolios(id) on delete cascade,
    security_id uuid not null references public.securities(id),
    transaction_type text not null check (
        transaction_type in ('buy', 'sell', 'dividend', 'fee', 'deposit', 'withdrawal')
    ),
    quantity numeric(20, 8),
    price numeric(20, 8),
    amount numeric(20, 8),
    currency char(3) not null,
    executed_at timestamptz not null,
    created_at timestamptz not null default now()
);

create table public.daily_prices (
    security_id uuid not null references public.securities(id) on delete cascade,
    price_date date not null,
    open numeric(20, 8),
    high numeric(20, 8),
    low numeric(20, 8),
    close numeric(20, 8) not null,
    adjusted_close numeric(20, 8),
    volume bigint,
    primary key (security_id, price_date)
);

create table public.portfolio_snapshots (
    id uuid primary key default gen_random_uuid(),
    portfolio_id uuid not null references public.portfolios(id) on delete cascade,
    snapshot_date date not null,
    total_value numeric(20, 4) not null,
    cash_value numeric(20, 4) not null default 0,
    daily_return numeric(12, 8),
    unique (portfolio_id, snapshot_date)
);

create table public.risk_snapshots (
    id uuid primary key default gen_random_uuid(),
    portfolio_id uuid not null references public.portfolios(id) on delete cascade,
    calculated_at timestamptz not null default now(),
    beta numeric(12, 6),
    annualised_return numeric(12, 8),
    annualised_volatility numeric(12, 8),
    sharpe_ratio numeric(12, 6),
    maximum_drawdown numeric(12, 8),
    historical_var_95 numeric(12, 8),
    concentration_hhi numeric(12, 8),
    model_version text not null default 'v1'
);

create table public.news_articles (
    id uuid primary key default gen_random_uuid(),
    external_id text not null unique,
    source text not null,
    headline text not null,
    summary text,
    url text not null,
    published_at timestamptz not null,
    sentiment numeric(8, 6),
    raw_payload jsonb,
    created_at timestamptz not null default now()
);

create table public.article_securities (
    article_id uuid not null references public.news_articles(id) on delete cascade,
    security_id uuid not null references public.securities(id) on delete cascade,
    relevance numeric(8, 6),
    sentiment numeric(8, 6),
    primary key (article_id, security_id)
);

create table public.portfolio_article_scores (
    portfolio_id uuid not null references public.portfolios(id) on delete cascade,
    article_id uuid not null references public.news_articles(id) on delete cascade,
    relevance_score numeric(8, 6) not null,
    affected_weight numeric(8, 6) not null,
    importance text not null,
    explanation text,
    primary key (portfolio_id, article_id)
);

create table public.notification_rules (
    id uuid primary key default gen_random_uuid(),
    portfolio_id uuid not null references public.portfolios(id) on delete cascade,
    rule_type text not null,
    threshold numeric(20, 8),
    enabled boolean not null default true,
    delivery_channels text[] not null default array['in_app'],
    created_at timestamptz not null default now()
);

create table public.notifications (
    id uuid primary key default gen_random_uuid(),
    portfolio_id uuid not null references public.portfolios(id) on delete cascade,
    title text not null,
    body text not null,
    severity text not null default 'info',
    read_at timestamptz,
    created_at timestamptz not null default now()
);

alter table public.portfolios enable row level security;
alter table public.transactions enable row level security;
alter table public.portfolio_snapshots enable row level security;
alter table public.risk_snapshots enable row level security;
alter table public.portfolio_article_scores enable row level security;
alter table public.notification_rules enable row level security;
alter table public.notifications enable row level security;

create policy "Users manage their portfolios"
on public.portfolios
for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users manage transactions in their portfolios"
on public.transactions
for all
using (
    exists (
        select 1 from public.portfolios p
        where p.id = transactions.portfolio_id
          and p.user_id = auth.uid()
    )
)
with check (
    exists (
        select 1 from public.portfolios p
        where p.id = transactions.portfolio_id
          and p.user_id = auth.uid()
    )
);
