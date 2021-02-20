from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Arquivos', error_messages={'required': 'Preencha este campo'})

class SearchInvoiceForm(forms.Form):
    emitter = forms.CharField(label='Emissor', max_length=255, required=False)
    receiver = forms.CharField(label='Destinatário', max_length=255, required=False)
    operation = forms.CharField(label='Natireza de Operação', max_length=255, required=False)
    product = forms.CharField(label='Produto', max_length=255, required=False)
    aditionalInfo = forms.CharField(label='Informação Adicional', max_length=255, required=False)