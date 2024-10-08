-- Create routines table
CREATE TABLE IF NOT EXISTS public.routines (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  user_id UUID REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create dashboard_data table
CREATE TABLE IF NOT EXISTS public.dashboard_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  bot_status TEXT,
  total_tasks_completed INTEGER,
  total_rewards_earned NUMERIC,
  current_streak INTEGER,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Set up RLS for routines
ALTER TABLE public.routines ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their own routines"
ON public.routines
FOR ALL USING (auth.uid() = user_id);

-- Set up RLS for dashboard_data
ALTER TABLE public.dashboard_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their own dashboard data"
ON public.dashboard_data
FOR ALL USING (auth.uid() = user_id);