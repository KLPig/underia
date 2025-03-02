source /Users/kl/PycharmProjects/venv/bin/activate
echo 'Running with higher priority, enter the password to continue:'
sudo -S nice -n 20 python ./main.py