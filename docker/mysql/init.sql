REVOKE ALL PRIVILEGES ON *.* FROM 'markdawn_svc'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON markdawn.* TO 'markdawn_svc'@'%';
FLUSH PRIVILEGES;

CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NULL,
    oauth_provider VARCHAR(20) NULL, -- Ex: 'google'
    oauth_id VARCHAR(255) NULL,      -- ig google
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_oauth (oauth_provider, oauth_id)
);


CREATE TABLE workspaces (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    folder_path VARCHAR(500) NOT NULL UNIQUE,
    created_by CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE TABLE workspace_members (
    workspace_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    role ENUM('ADMIN', 'EDITOR', 'VIEWER') NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id),
    FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE TABLE documents (
    id CHAR(36) PRIMARY KEY,
    workspace_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    markdown_content LONGTEXT NOT NULL,
    file_path VARCHAR(500) NOT NULL UNIQUE,
    created_by CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id)
        ON DELETE CASCADE,
    FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE TABLE refresh_tokens (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);