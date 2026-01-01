-- Database initialization script

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    username VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    user_level VARCHAR(20) DEFAULT 'beginner',
    main_system_id VARCHAR(100) UNIQUE
);

-- Ledger for points
CREATE TABLE ledger (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    transaction_type VARCHAR(50),
    amount DECIMAL(15, 4),
    balance_after DECIMAL(15, 4),
    description TEXT,
    reference_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wallet balances
CREATE TABLE wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    points_balance DECIMAL(15, 4) DEFAULT 1000.0000,
    interest_rate DECIMAL(5, 4) DEFAULT 0.0010,
    last_interest_calc TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_earned DECIMAL(15, 4) DEFAULT 0.0000,
    total_spent DECIMAL(15, 4) DEFAULT 0.0000
);

-- Lottery predictions
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    lottery_type VARCHAR(50),
    prediction_numbers JSONB,
    actual_numbers JSONB,
    prediction_date DATE,
    lottery_date DATE,
    points_awarded DECIMAL(10, 4),
    accuracy DECIMAL(5, 2),
    is_correct BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lottery results (synced from external sources)
CREATE TABLE lottery_results (
    id SERIAL PRIMARY KEY,
    lottery_type VARCHAR(50),
    draw_date DATE,
    winning_numbers JSONB,
    bonus_numbers JSONB,
    prize_pool DECIMAL(15, 2),
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100)
);

-- Barter marketplace listings
CREATE TABLE barter_listings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200),
    description TEXT,
    category VARCHAR(50),
    asking_price DECIMAL(15, 4),
    points_price DECIMAL(15, 4),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    views INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT false
);

-- Barter transactions
CREATE TABLE barter_transactions (
    id SERIAL PRIMARY KEY,
    listing_id INTEGER REFERENCES barter_listings(id),
    buyer_id INTEGER REFERENCES users(id),
    seller_id INTEGER REFERENCES users(id),
    transaction_amount DECIMAL(15, 4),
    fee_amount DECIMAL(15, 4),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    buyer_rating INTEGER,
    seller_rating INTEGER,
    dispute_resolved BOOLEAN DEFAULT false
);

-- Interest calculation history
CREATE TABLE interest_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    calculation_date DATE,
    points_before DECIMAL(15, 4),
    interest_earned DECIMAL(15, 4),
    points_after DECIMAL(15, 4),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activity log
CREATE TABLE activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    activity_type VARCHAR(50),
    points_change DECIMAL(10, 4),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_ledger_user_id ON ledger(user_id);
CREATE INDEX idx_predictions_user_id ON predictions(user_id);
CREATE INDEX idx_predictions_date ON predictions(prediction_date);
CREATE INDEX idx_barter_user_id ON barter_listings(user_id);
CREATE INDEX idx_wallets_user_id ON wallets(user_id);
CREATE INDEX idx_interest_history_user_id ON interest_history(user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE
ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
