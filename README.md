# 手順
```
pip3 freeze > requirements.txt
git add requirements.txt
git commit -m requirements.txt

heroku create
heroku addons:create heroku-postgresql
git push heroku master
```

# DB
```
heroku pg:psql

create table Users (
	id integer PRIMARY KEY,
	name text,
	password text
);
insert into users values (1, 'foo', 'bar');
```

# DSN
```
heroku config:get DATABASE_URL
```

# URL
```
heroku info | grep 'Web URL' | awk '{ print $3 }'
```

# ログ
```
heroku logs --tail
```

# 動作確認
```
curl $(heroku info | grep 'Web URL' | awk '{ print $3 }')'?user=foo&password=bar'
```

# テスト(local)
```
. setup_test.sh
pytest
```

# 参考
* https://docs.aiohttp.org/en/stable/index.html
* https://aiopg.readthedocs.io/en/stable/index.html
* https://www.sqlalchemy.org/library.html
