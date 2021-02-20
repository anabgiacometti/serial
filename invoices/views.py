import sys
import xml.dom.minidom as minidom
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from django.db.models import Q
from .models import Invoices_OUT, Invoices_OUT_PROD
from .forms import UploadFileForm, SearchInvoiceForm


def Invoices(request):
    template = loader.get_template('invoices/index.html')
    emitter_options = Invoices_OUT.objects.distinct('emitter_name').order_by('emitter_name').values('emitter_name')
    operation_options = Invoices_OUT.objects.distinct('operation').order_by('operation').values('operation')
    product_options = Invoices_OUT_PROD.objects.distinct('product').order_by('product').values('product')
    invoices = Invoices_OUT.objects.order_by('-emission_date').all()  
    if request.method == 'POST':
        form = SearchInvoiceForm(request.POST)
        if form.is_valid():
            emitter = form.cleaned_data['emitter'] or None
            receiver = form.cleaned_data['receiver'] or None 
            operation = form.cleaned_data['operation'] or None
            product = form.cleaned_data['product'] or None
            aditionalInfo = form.cleaned_data['aditionalInfo'] or None

            if emitter: 
                invoices = invoices.filter(emitter_name=emitter)
            if receiver: 
                invoices = invoices.filter(Q(receiver_name__istartswith=receiver) | Q(receiver__istartswith=receiver))
            if operation: 
                invoices = invoices.filter(operation=operation)
            if product: 
                invoice_ids = Invoices_OUT_PROD.objects.filter(product=product).values('invoice').values_list(flat=True)
                invoices = invoices.filter(Q(id__in=list(invoice_ids)))
            if aditionalInfo: 
                invoices = invoices.filter(Q(aditional_info__icontains=aditionalInfo))
                
    else: 
        form = SearchInvoiceForm()
            
    context = {
        'form': form,
        'invoices': invoices[:50],
        'emitter_options': emitter_options,
        'operation_options': operation_options,
        'product_options': product_options
    }
    return HttpResponse(template.render(context, request))
    

def Import(request):
    template = loader.get_template('invoices/import.html')
    result = []
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print(len(request.FILES.getlist('file')))
            for file in request.FILES.getlist('file'):
                try:
                    my_uploaded_file = file
                    xmldoc = minidom.parse(my_uploaded_file)
                    i = xmldoc.getElementsByTagName("infNFe")[0]
                    result.append({'name': file.name, 'result': constructInvoice(i)})
                except: 
                    result.append({'name': file.name, 'result': 'Formato Incorreto'})      
    else: 
        form = UploadFileForm()

    context = {
        'form': form,
        'result': result
    }

    return HttpResponse(template.render(context, request))


def getNodeText(node):    
    nodelist = node.childNodes
    result = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            result.append(node.data)
    return ''.join(result)

def constructInvoice(i):
    try:
        #dados da NF
        ide = i.getElementsByTagName("ide")[0]
        operation = getNodeText(ide.getElementsByTagName("natOp")[0])
        series = getNodeText(ide.getElementsByTagName("serie")[0])
        number = getNodeText(ide.getElementsByTagName("nNF")[0])
        emission_date = getNodeText(ide.getElementsByTagName("dhEmi")[0])
        #dados do emitente
        emit = i.getElementsByTagName("emit")[0]
        emitter = getNodeText(emit.getElementsByTagName("CNPJ")[0])
        emitter_name = getNodeText(emit.getElementsByTagName("xNome")[0])
        #dados do destinatario
        dest = i.getElementsByTagName("dest")[0]
        try: 
            receiver = getNodeText(dest.getElementsByTagName("CNPJ")[0])
        except:
            receiver = getNodeText(dest.getElementsByTagName("CPF")[0])
        receiver_name = getNodeText(dest.getElementsByTagName("xNome")[0])
        #informações adicionais
        infAdic = i.getElementsByTagName("infAdic")[0]
        aditional_info = getNodeText(infAdic.getElementsByTagName("infCpl")[0])
        #produtos
        products = i.getElementsByTagName('det')

        invoice_db = Invoices_OUT.objects.all().filter(series=int(series), number=int(float(number)), emitter=emitter)
        
        if len(invoice_db) == 0:
            invoice = Invoices_OUT(
            operation = operation, 
            series = int(series), 
            number = int(number), 
            emitter = emitter, 
            emitter_name = emitter_name, 
            emission_date = datetime.strptime(emission_date, '%Y-%m-%dT%H:%M:%S%z'),
            receiver = receiver, 
            receiver_name = receiver_name, 
            aditional_info = aditional_info )

            invoice.save()

            for p in products: 
                prod = p.getElementsByTagName("prod")[0]
                prod_name = getNodeText(prod.getElementsByTagName("xProd")[0])
                prod_quantity = getNodeText(prod.getElementsByTagName("qCom")[0])
                prod_price = getNodeText(prod.getElementsByTagName("vUnTrib")[0])
                product = Invoices_OUT_PROD(
                    invoice = invoice,
                    product = prod_name, 
                    quantity = int(float(prod_quantity)), 
                    value = float(prod_price))
                product.save()
            return('Importado')
        else: 
            return('Não Importado - NF Repetida')
    except OSError as err:
        print("OS error: {0}".format(err))
        return('Não Importado - Ocorreu um erro')
    except ValueError:
        print("Could not convert data to an integer.")
        return('Não Importado - Ocorreu um erro')
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return('Não Importado - Ocorreu um erro')
