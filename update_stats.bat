@echo off
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d amcheck -c "SELECT public.update_site_statistics();"
exit