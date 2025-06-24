npm run build
# saved to dist

# copy dist to the flask-app
mkdir -p ../flask-app/static
cp -r dist/* ../flask-app/static/