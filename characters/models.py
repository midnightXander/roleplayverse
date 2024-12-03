from django.db import models
#from django.contrib.postgres.fields import ArrayField
import json

class Character(models.Model):
    name = models.CharField(max_length=50)
    #image = models.ImageField(upload_to="characters/")
    #jutsu = ArrayField(models.CharField(max_length=100))
    image_link = models.TextField(default='https://static.wikia.nocookie.net/naruto/images/e/e6/Ten-Tails_emerges.png')
    jutsu = models.TextField(blank=True)

    def set_justu_field(self,jutsu):
        self.jutsu = json.dumps(jutsu)

    def get_justu_field(self):
        return json.loads(self.jutsu)

    def __str__(self):
        return self.name

