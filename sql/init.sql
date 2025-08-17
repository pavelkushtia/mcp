-- Initialize the MCP Tasks Database
-- This creates a simple task management system for our MCP server demo

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date TIMESTAMP WITH TIME ZONE,
    assigned_to VARCHAR(100),
    tags TEXT[] DEFAULT '{}'
);

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6B7280', -- hex color code
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create task_categories junction table (many-to-many)
CREATE TABLE IF NOT EXISTS task_categories (
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, category_id)
);

-- Create comments table
CREATE TABLE IF NOT EXISTS task_comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    author VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_task_comments_task_id ON task_comments(task_id);

-- Insert sample data
INSERT INTO categories (name, description, color) VALUES
    ('Work', 'Work-related tasks', '#3B82F6'),
    ('Personal', 'Personal tasks and reminders', '#10B981'),
    ('Shopping', 'Shopping lists and purchases', '#F59E0B'),
    ('Health', 'Health and wellness tasks', '#EF4444'),
    ('Learning', 'Learning and development', '#8B5CF6')
ON CONFLICT (name) DO NOTHING;

-- Insert sample tasks
INSERT INTO tasks (title, description, status, priority, assigned_to, due_date, tags) VALUES
    ('Setup MCP Server', 'Build and configure the MCP server for PostgreSQL integration', 'in_progress', 'high', 'developer', NOW() + INTERVAL '2 days', ARRAY['development', 'mcp']),
    ('Database Schema Design', 'Design the initial database schema for the task management system', 'completed', 'high', 'developer', NOW() - INTERVAL '1 day', ARRAY['database', 'design']),
    ('Write Documentation', 'Create comprehensive documentation for the MCP server', 'pending', 'medium', 'developer', NOW() + INTERVAL '1 week', ARRAY['documentation']),
    ('Buy Groceries', 'Weekly grocery shopping', 'pending', 'low', 'user', NOW() + INTERVAL '3 days', ARRAY['shopping', 'weekly']),
    ('Review Pull Requests', 'Review pending pull requests in the repository', 'pending', 'medium', 'developer', NOW() + INTERVAL '1 day', ARRAY['code-review', 'development'])
ON CONFLICT DO NOTHING;

-- Link tasks to categories
INSERT INTO task_categories (task_id, category_id) 
SELECT t.id, c.id 
FROM tasks t, categories c 
WHERE (t.title LIKE '%MCP%' OR t.title LIKE '%Database%' OR t.title LIKE '%Documentation%' OR t.title LIKE '%Pull Request%') AND c.name = 'Work'
ON CONFLICT DO NOTHING;

INSERT INTO task_categories (task_id, category_id) 
SELECT t.id, c.id 
FROM tasks t, categories c 
WHERE t.title LIKE '%Groceries%' AND c.name = 'Shopping'
ON CONFLICT DO NOTHING;

-- Add some sample comments
INSERT INTO task_comments (task_id, comment, author) 
SELECT t.id, 'Started working on the basic server structure', 'developer'
FROM tasks t 
WHERE t.title = 'Setup MCP Server';

INSERT INTO task_comments (task_id, comment, author) 
SELECT t.id, 'Schema looks good, includes all necessary tables and relationships', 'reviewer'
FROM tasks t 
WHERE t.title = 'Database Schema Design';

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_tasks_updated_at 
    BEFORE UPDATE ON tasks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
