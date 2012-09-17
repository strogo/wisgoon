from django.db import models

class Blog(models.Model):
    PROVIDERS = (
        (1, 'blogfa.com'),
        (2, 'mihanblog.com'),
    )
    
    NI = 0
    IN = 200
    
    STATUS = (
        (NI, 'Not indexed'),
        (IN, 'indexed'),
    )
    
    title = models.CharField(max_length=300, blank=True)
    url = models.URLField()
    url_crc = models.IntegerField()
    
    email = models.EmailField(blank=True)
    provider = models.CharField(max_length=100, choices=PROVIDERS)
    
    status = models.IntegerField(choices=STATUS, default=NI)
    
class B2B(models.Model):
    from_b = models.ForeignKey(Blog, related_name="from")
    to_b = models.ForeignKey(Blog, related_name="to")
    
    
    