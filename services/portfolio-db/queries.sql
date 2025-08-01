-- name: GetAllHoldings :many
SELECT ticker, name, weight, comment, price, updated_dt, added_dt, return
FROM portfolio_holdings
ORDER BY weight DESC;

-- name: GetHolding :one
SELECT ticker, name, weight, comment, price, updated_dt, added_dt, return
FROM portfolio_holdings
WHERE ticker = $1;

-- name: CreateHolding :one
INSERT INTO portfolio_holdings (ticker, name, weight, comment, price, return)
VALUES ($1, $2, $3, $4, $5, $6)
RETURNING ticker, name, weight, comment, price, updated_dt, added_dt, return;

-- name: UpdateHolding :one
UPDATE portfolio_holdings 
SET name = COALESCE($2, name),
    weight = COALESCE($3, weight), 
    price = COALESCE($4, price),
    comment = COALESCE($5, comment),
    return = COALESCE($6, return),
    updated_dt = now()
WHERE ticker = $1
RETURNING ticker, name, weight, comment, price, updated_dt, added_dt, return;

-- name: DeleteHolding :exec
DELETE FROM portfolio_holdings WHERE ticker = $1;

-- name: GetPortfolioSummary :one
SELECT 
    COALESCE(SUM(weight), 0) as total_weight,
    COUNT(*) as holding_count,
    COALESCE(AVG(return), 0) as avg_return
FROM portfolio_holdings;