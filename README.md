# 手順
## requirements.txt作成
```
pip3 freeze > requirements.txt
git add requirements.txt
git commit -m requirements.txt
```

## DB
```
create table Users (
	id integer PRIMARY KEY,
	name text,
	password text
);
insert into users values (1, 'foo', 'bar');
```

## テスト
herokuでアプリケーションのセットアップ後
```
. setup_test.sh
pytest
```

***

# heroku

## 起動ファイル
* Procfile

## セットアップ
```
heroku create
heroku addons:create heroku-postgresql
git push heroku master
```

## DB接続
```
heroku pg:psql
```

## DSN
```
heroku config:get DATABASE_URL
```

## URL
```
heroku info | grep 'Web URL' | awk '{ print $3 }'
```

## ログ
```
heroku logs --tail
```

## 動作確認
```
curl $(heroku info | grep 'Web URL' | awk '{ print $3 }')'?user=foo&password=bar'
```

***

# CloudFoundry

## 起動ファイル
* manifest.yml

## セットアップ
```
cf push herokuk-aiohttp -m 64M --random-route --no-start
cf create-service a9s-postgresql10 postgresql-single-small herokuk-aiohttp-db
```

作成が終わるまで待つ
```
cf services | grep 'create succeeded'
```

```
cf bind-service herokuk-aiohttp herokuk-aiohttp-db
cf push
```

## DB接続
SSHポートフォワード
```
cf ssh herokuk-aiohttp -L 5432:$(cf env herokuk-aiohttp | grep '"host"' | awk -F: '{ print $2 }' | sed 's/ *"\(.*\)",/\1/'):5432
```

以下のコマンドで出力される内容でDBに接続し、テーブルの作成、データの投入をする
```
cf env herokuk-aiohttp
```

* host: localhost
* port: 5432
* user: "username"
* passowrd: "password"
* database: "name"

## 動作確認
```
curl http://$(cf app herokuk-aiohttp | grep '^routes:' | awk '{ print $2 }')'/?user=foo&password=bar'
```

## 削除
```
cf delete -f -r herokuk-aiohttp
cf delete-service -f herokuk-aiohttp-db
```

***

# CircleCI
* .circleci/config.yml

herokuにデプロイ後、結果をSlackに通知

***

# Actions
* .github/workflows/main.yml

***

# 参考
* https://docs.aiohttp.org/en/stable/index.html
* https://aiopg.readthedocs.io/en/stable/index.html
* https://www.sqlalchemy.org/library.html
