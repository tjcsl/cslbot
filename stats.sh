files=`find -name '*.py'`
lines=`wc -l $files | tail -1 | sed s/total//`
echo $lines lines of code in IRCbot
