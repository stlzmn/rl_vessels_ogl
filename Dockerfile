FROM python:3.8.16

WORKDIR /app
COPY . /app
# GDAL is not installed here - install it yourself first (see README), matching
# the version/platform of your Python/libgdal setup.
RUN pip install -r dependencies/requirements.txt
CMD python ./entry_point.py