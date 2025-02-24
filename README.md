## Set up development environment

- Create new venv and install all the requirements from the requirements.txt file:
```bash
$ python3 -m venv venv 
$ source venv/bin/activate 
$ pip3 install -r requirements.txt

```
- Finally start up the server:
```bash
$ uvicorn main:app --reload  

```