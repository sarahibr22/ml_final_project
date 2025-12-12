# Database Dockerfile
FROM postgres:16-alpine
ENV POSTGRES_DB=med_db
ENV POSTGRES_USER=med_user
ENV POSTGRES_PASSWORD=med_pass

# Install pgvector extension
RUN apk add --no-cache postgresql16-pgvector

COPY init.sql /docker-entrypoint-initdb.d/
EXPOSE 5432
