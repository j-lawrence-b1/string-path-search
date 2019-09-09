rem Assumes MS Visual Studio is installed and the path to nmake.exe is in your execution PATH.
@echo off
call nmake /F Makefile.windows %*
