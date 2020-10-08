# Debezium Quickstart

## 1. Setting up databases
### MySQL: https://debezium.io/documentation/reference/connectors/mysql.html#setup-the-mysql-server
### Postgresql: https://debezium.io/documentation/reference/connectors/postgresql.html#setting-up-postgresql
- Postgres plugins installation: https://debezium.io/documentation/reference/postgres-plugins.html

#### Prepare Postgres Tables
```(sql)
create table ws_order
(
	order_id serial not null,
	item_name varchar default 'item name',
	item_price numeric not null,
	shop_id int default 0 not null,
	created_at timestamp without time zone default current_timestamp not null
);

create unique index ws_order_order_id_uindex on ws_order (order_id);

alter table ws_order
	add constraint ws_order_pk
		primary key (order_id);

INSERT INTO public.ws_order (order_id, item_name, item_price, shop_id, created_at) VALUES (default, 'nama barang 1', 1000, 1, current_timestamp);
INSERT INTO public.ws_order (order_id, item_name, item_price, shop_id, created_at) VALUES (default, 'nama barang 2', 2000, 2, current_timestamp);
INSERT INTO public.ws_order (order_id, item_name, item_price, shop_id, created_at) VALUES (default, 'nama barang 3', 3000, 3, current_timestamp);
INSERT INTO public.ws_order (order_id, item_name, item_price, shop_id, created_at) VALUES (default, 'nama barang 4', 4000, 4, current_timestamp);

```
&nbsp;
## 2. Start services
```(bash)
# Zookeper
docker run -it --rm --name zookeeper -p 2181:2181 -p 2888:2888 -p 3888:3888 debezium/zookeeper:1.3

# Kafka
docker run -it --rm --name kafka -p 9092:9092 --link zookeeper:zookeeper debezium/kafka:1.3

# Debezium connector
docker run -it --rm --name connect -p 8083:8083 \
-e GROUP_ID=1 \
-e CONFIG_STORAGE_TOPIC=de_connect_configs \
-e OFFSET_STORAGE_TOPIC=de_connect_offsets \
-e STATUS_STORAGE_TOPIC=de_connect_statuses \
--link zookeeper:zookeeper \
--link kafka:kafka debezium/connect:1.3
```
&nbsp;
## 3. Deploying connector
Rest API docs: https://docs.confluent.io/current/connect/references/restapi.html
```(bash)
curl --request POST \
  --url http://10.199.92.47:8083/connectors \
  --header 'accept: application/json' \
  --header 'content-type: application/json' \
  --data '{
  "name": "de-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.server.name": "dbzserver1",
    "database.dbname": "dbz",
    "database.hostname": "10.199.92.47",
    "database.port": "5432",
    "database.user": "dbz",
    "database.password": "dbz",
    "slot.name": "dbz_slot",
    "table.include.list": "public.ws_order",
    "snapshot.mode": "exported",
    "plugin.name": "wal2json"
  }
}'
```
&nbsp;
## 4. Starting consumer
```(bash)
# Consumer to local txt file
docker run -it --rm --name watcher \
--link zookeeper:zookeeper \
--link kafka:kafka debezium/kafka:1.3 watch-topic \
-a dbzserver1.public.ws_order \
| grep --line-buffered '^{' | $PWD/stream_txt.py > ws_order.txt

# Consumer to bigquery
pip install google-cloud-bigquery

docker run -it --rm --name watcher \
--link zookeeper:zookeeper \
--link kafka:kafka debezium/kafka:1.3 watch-topic \
-a dbzserver1.public.ws_order \
| grep --line-buffered '^{' | $PWD/stream_bq.py

# Or only watcher for kafka topic
docker run -it --rm --name watcher \
--link zookeeper:zookeeper \
--link kafka:kafka debezium/kafka:1.3 watch-topic \
-a -k dbzserver1.public.ws_order 
```