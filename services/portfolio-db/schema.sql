-- Portfolio holdings table
CREATE TABLE portfolio_holdings (
    ticker      text PRIMARY KEY,          -- e.g. 'AAPL'
    name        text        NOT NULL,      -- full security name
    weight      numeric(6,3) NOT NULL      -- store as percent: 0 – 100
                 CHECK (weight > 0),
    comment     text,
    price       numeric(18,4) NOT NULL
                 CHECK (price >= 0),       -- last quote currency
    updated_dt  timestamptz NOT NULL
                 DEFAULT now(),            -- last price/weight touch
    added_dt    timestamptz NOT NULL
                 DEFAULT now(),            -- first time in table
    return      numeric(10,4)              -- cumulative return
);