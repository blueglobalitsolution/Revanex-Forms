@echo off
cd /d "C:\Program Files\MySQL\MySQL Server 8.0\bin"
start /B mysqld.exe --skip-grant-tables --skip-networking
