# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    release = models.IntegerField(blank=True, null=True)
    duration = models.SmallIntegerField(blank=True, null=True)
    genres = ArrayField(models.CharField(max_length=128, blank=True), blank=True, null=True)
    directors = ArrayField(models.CharField(max_length=255, blank=True), blank=True, null=True)
    actors = ArrayField(models.CharField(max_length=255, blank=True), blank=True, null=True)
    plot = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # no need to create/insert/delete anything, just to lookup
        db_table = 'movies'
        unique_together = (('title', 'directors', 'release'),)


class DataSource(models.Model):
    movie = models.ForeignKey(Movie, models.DO_NOTHING)
    movie_source_uid = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    url = models.TextField(unique=True)
    page_title = models.TextField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    critic_score = models.FloatField(blank=True, null=True)
    last_crawled = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data_sources'
