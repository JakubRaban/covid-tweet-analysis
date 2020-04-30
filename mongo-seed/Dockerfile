FROM mongo:4.2.6
COPY init.json /init.json
CMD mongoimport --host mongodb --db tweets --collection test1 --type json --file /init.json --jsonArray