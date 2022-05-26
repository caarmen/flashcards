root=$(pwd)
for lang in en fr
do
  cd $root/locales/$lang/LC_MESSAGES
  msgfmt -o base.mo base
done
cd $root
