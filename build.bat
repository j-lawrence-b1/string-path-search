@echo off
set NMAKE="C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.22.27905\bin\Hostx86\x86/nmake.exe"
call %NMAKE% /F Makefile.windows %*
