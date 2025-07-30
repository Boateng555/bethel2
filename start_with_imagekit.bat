@echo off
echo 🔧 Setting up ImageKit environment variables...

set IMAGEKIT_PUBLIC_KEY=public_Y1VNbHgFpCqBL6FhEcr7oCdkQNU=
set IMAGEKIT_PRIVATE_KEY=private_Dnsrj2VW7uJakaeMaNYaav+P784=
set IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/9buar9mbp

echo ✅ ImageKit environment variables set
echo    PUBLIC_KEY: %IMAGEKIT_PUBLIC_KEY:~0,20%...
echo    PRIVATE_KEY: %IMAGEKIT_PRIVATE_KEY:~0,20%...
echo    URL_ENDPOINT: %IMAGEKIT_URL_ENDPOINT%

echo.
echo 🚀 Starting Django server with ImageKit...
python manage.py runserver

pause 