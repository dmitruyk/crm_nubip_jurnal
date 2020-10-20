
##Steps to run project

##Install docker & docker-compose (cli)
```
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
##Pull the progect from github
```
git clone https://github.com/dmitruyk/main2.git

Enter in project root
Run command docker-compose up -d --build
Create superuser docker-compose exec -it id_app_container python manage.py createsuperuser
```


##Steps to run project

```
Enter in project root
Run command docker-compose up -d --build
Create superuser docker-compose exec -it id_app_container python manage.py createsuperuser
```

## Example /src/.env

```

DEBUG=on|off
SECRET_KEY=0%n@sp=2a5bf*%xfdqlc$j2(p!=-c8$5qgk5^7hei#nbx-8_p0
DATABASE_URL=postgres://test:test@postgres:5432/db

ADMIN_EMAIL=<dmitruyk@gmail.com>
```

## Create superuser account:
```
enter in dokcer container, run command "python manage.py createsuperuser"
input user data
user: admin
passwd: admin
```

## API_requests:
```
Create application
/api/v1/application/create

## API_requests data accept from remote source:
```
reqest type = POST
Content-Type = application/json
basic auth 
body = {
	"creation_date": "2019-05-10",
	"send": "2019-05-10",
	"customer": {
		"first_name": "testuser",
		"last_name": "user_test",
		"add_name": "test",
		"date_of_birth": "2010-05-10",
		"passport": {
			"number": 111111,
			"issue_date": "2019-05-10"
		},
		"phone_number": {
			"country_code": "380",
			"area_code": 88,
			"number": 1231212,
			"type": "main"
		}
	},
	"scoring_score": 99
}
```
