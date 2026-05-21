FROM postgres:15

WORKDIR /postgres

COPY /postgres .

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]