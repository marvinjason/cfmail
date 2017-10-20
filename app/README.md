# Setting Up

Clone the repository
```bash
$ git clone https://github.com/marvinjason/cfmail.git
```

Activate the virtual environment
```bash
# for Ubuntu
$ source cfmail/ubuntu/bin/activate

# for Windows
$ cd cfmail/windows/Scripts
$ activate
```

Install the dependencies using `pip`
```bash
$ pip install -r requirements.txt -t lib
```

Run the app in the test server
```bash
$ dev_appserver.py app.yaml --admin_port=9000
```
