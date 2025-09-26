
who

ls /
ls /home
ls /home/user
ls /home/user/projects

cd /home
ls
cd user
ls
cd projects
ls
cd ../..
ls
cd /

cat /root/file1.txt
cat /home/user/document.txt
cat /home/user/projects/project1.py
cat /home/user/projects/readme.md

tail /home/user/projects/readme.md
tail -n 3 /home/user/projects/readme.md
tail -n 1 /home/user/projects/readme.md

ls /invalid/path
cd /home/user/nonexistent
cat /home/user/nonexistent.txt
tail -n abc /home/user/projects/readme.md

exit