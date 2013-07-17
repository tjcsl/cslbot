for i in `find -name '*.py'`; do cat $i | wc -l; done > lines.txt
echo `python -c "print sum([int(i) if i != '' else 0 for i in open('lines.txt').read().split('\n')])"` lines of code in IRCbot
rm lines.txt
