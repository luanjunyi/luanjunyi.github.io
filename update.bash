cd export_google_calendar
python export.py > ../index.html
cd ..
cat index.html
git add .
git ci -m "update at `date`"
git push origin master
