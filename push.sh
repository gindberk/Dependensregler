echo Adding updated rules...
git add script/*.txt
wait
echo Done!
echo
echo Committing to repository...
git commit -m "`date` Erik"
wait
echo Done!
echo
echo Pushing to remote...
git push Dependensregler master
wait
echo Done!

echo Push complete!
