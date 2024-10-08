import { createClient } from '@supabase/supabase-js'

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!)

async function createTables() {
  const { error: routinesError } = await supabase.rpc('create_routines_table')
  if (routinesError) console.error('Error creating routines table:', routinesError)

  const { error: dashboardError } = await supabase.rpc('create_dashboard_data_table')
  if (dashboardError) console.error('Error creating dashboard_data table:', dashboardError)

  console.log('Tables created successfully')
}

createTables()