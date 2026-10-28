-- Cartrack RM System: is the database actually locked down?
-- Run in the Supabase SQL editor for project govvmqgpxzbqghzgcitb (cartrack-rm-system):
--   https://supabase.com/dashboard/project/govvmqgpxzbqghzgcitb/sql/new
-- Read the three results together. Query 1 alone does not tell you the answer.

-- 1. Is row level security switched on for each table?
--    rls_enabled must be TRUE on every row, especially payroll.
--    FALSE on payroll means anyone holding the anon key (it is in the page
--    source of the app) can read every salary in it.
select c.relname                as table_name,
       c.relrowsecurity         as rls_enabled,
       c.relforcerowsecurity    as rls_forced
from   pg_class c
join   pg_namespace n on n.oid = c.relnamespace
where  n.nspname = 'public'
and    c.relkind = 'r'
order  by c.relname;

-- 2. What do the policies actually allow, and for which role?
--    This is the one that matters. A policy on payroll whose roles include
--    'anon' or '{public}' and whose qual is 'true' means RLS is on but open:
--    it permits exactly what having no RLS would permit.
select tablename,
       policyname,
       cmd,          -- SELECT / INSERT / UPDATE / DELETE / ALL
       roles,        -- look for anon or public
       qual,         -- the read rule
       with_check    -- the write rule
from   pg_policies
where  schemaname = 'public'
order  by tablename, policyname;

-- 3. Table level grants to the anon role, underneath the policies.
--    If anon holds no grant on payroll, the table is closed to the app
--    regardless of policies. If it holds SELECT, only a policy is stopping it.
select table_name, privilege_type
from   information_schema.role_table_grants
where  grantee = 'anon'
and    table_schema = 'public'
order  by table_name, privilege_type;

-- Reading the answer
-- The app signs in nobody: it calls Supabase with the anon key and no Supabase
-- Auth session, so every request arrives as the anon role. Any policy loose
-- enough for the app to work is loose enough for anyone who opens the page
-- source, copies the key and calls the same URL. That is a property of the
-- design, not a misconfiguration, and it cannot be closed by editing policies
-- alone. Closing it properly means Supabase Auth (roadmap, about 20 hours),
-- after which payroll can be restricted to the handful of signed-in accounts
-- that are allowed to see salaries.
