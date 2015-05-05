files=`find -name '*.py' -not -path "./build/*"`
lines=`wc -l $files | tail -1 | sed s/total//`
echo $lines lines of code in CslBot
