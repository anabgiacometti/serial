from django.db import models
from datetime import date

class Invoices_OUT(models.Model): 
    operation = models.CharField(max_length=100) # natureza da operação
    series = models.IntegerField() # serie
    number = models.IntegerField() # numero
    emission_date = models.DateField(default=date.today) # data de emissão
    emitter = models.CharField(max_length=100) # emissor CPF ou CNPJ
    emitter_name = models.CharField(max_length=100) # emissor
    receiver = models.CharField(max_length=100) # destinatario CPF ou CNPJ
    receiver_name = models.CharField(max_length=100) # destinatario 
    aditional_info = models.CharField(max_length=1000) # informações adicionais


class Invoices_OUT_PROD(models.Model):
    invoice = models.ForeignKey(Invoices_OUT, on_delete=models.CASCADE)
    product = models.CharField(max_length=100) # produto
    quantity = models.IntegerField() # quantidade
    value = models.DecimalField(decimal_places=2, max_digits=100) # preço

