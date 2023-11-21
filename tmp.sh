docker run -d \
	--name tmp-db \
	-e POSTGRES_PASSWORD=postgres \
	-p 5432:5432 \
	postgres
