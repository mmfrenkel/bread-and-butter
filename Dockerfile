FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY . .

# cache disabled to keep image size small
# use --virtual to temporarily install packages required to instlal program, but not execute it
RUN apk update && \
	apk add --no-cache postgresql-libs && \
	apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
	pip install --no-cache-dir -r requirements.txt && \
	apk del .build-deps

# port number the container should be running on
EXPOSE 5000

# RUN APPLICATION
CMD ["flask", "run"]

