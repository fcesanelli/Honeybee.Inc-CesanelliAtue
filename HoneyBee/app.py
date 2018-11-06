#!/usr/bin/env python
import csv
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
import pandas as pd
from flask_script import Manager
from forms import LoginForm, RegistrarForm, ProductoForm,ClienteForm
import re 

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'un string que funcione como llave'


#_________________________BLOQUE FUNCIONES______________________________________________________

#funcion que lee el csv y lo mete en una lista
def ListaCSV():
    with open('datos.csv', 'r') as ventas:
        leearch = csv.reader(ventas)
        archlist= list(leearch)
    return archlist
#funcion que abre el csv en un diccionario key=categoria y lo almacena en una lista
def DiccionarioCSV():
    abrdir = csv.DictReader(open('datos.csv', 'r'))
    listadir = list(abrdir)
    return(listadir)
#Funcion de abre el csv con pd
def AbrirPD():
    csva = 'datos.csv' 
    pda = pd.read_csv(csva)
    return(pda)
#almacena los clientes en una lista 
def ListaCli():
    with open('datos.csv', 'r') as datos:
        dictr = csv.DictReader(datos)
        dicl = list(dictr)
        clil = []
        for l in dicl:                              
            if l['CLIENTE'] not in clil:
                clil.append(l['CLIENTE'])
    return clil
#almacena los productos en una lista
def ListaPro():
    with open('datos.csv', 'r') as datos:
        dictr = csv.DictReader(datos)
        dicl = list(dictr)
        prol = []
        for l in dicl:
            if l['PRODUCTO'] not in prol:
                prol.append(l['PRODUCTO'])
    return prol


#=========================VALIDACIONES=========================================================
def Validar_codigo():
    recdic=DiccionarioCSV()
    for l in recdic:
        camp=len(l['CODIGO'])
        if camp == 6:
            msj="Todos los codigos estan completos"
            return(msj)
        elif camp < 6:
            nmsj="Por lo menos un codigo aparece de manera incompleta"
            return(nmsj)
 
def VAlidar_Forma_Codigo():
	with open('datos.csv', 'r') as datos:
	    recdic=DiccionarioCSV()
	    for l in recdic:
	        cam =(l['CODIGO'])
	        let = cam[0:3]
	        num = cam[3:6]
	        if num.isnumeric() and let.isalpha():
	            msj="La composicion de los CODIGOS es valida"
	            return(msj)
	        else:
	            nmsj="Al menos uno de los CODIGOS no es valido"
	            return(nmsj)


def Validar_cant_campos():
    lista = ListaCSV()
    i=0
    enc = 0
    fila = 0
    while i<len(lista):

        D=lista[i]
        if len(D) == 5:
            i=i+1
        else:
            enc = 1
            fila = i+1
            break
    if enc == 0:
        msj="Todos los registros tienen la cantidad correcta de campos."
    else:
        msj="El registro {} contiene una cantidad invalida de campos.".format(fila)
    return(msj)    


def Validar_Cantidad():
    with open('datos.csv', 'r') as datos:
        dictr = csv.DictReader(datos)
        dicl = list(dictr)
        prol = []
        for l in dicl:
            if l['CANTIDAD'] not in prol:
                prol.append(l['CANTIDAD'])
                for f in prol:
                	try:
                		int(f)
                		msj='Todos los campos de CANTIDAD contien un valor entero'
                		return(msj)
                	except:
                		nmsj='Al menos un campo de CANTIDAD contien un valor que no es entero'
                		return(nmsj)

def Validar_Precio():
    with open('datos.csv', 'r') as datos:
        dictr = csv.DictReader(datos)
        dicl = list(dictr)
        prol = []
        for l in dicl:
            if l['PRECIO'] not in prol:
                prol.append(l['PRECIO'])
                for f in prol:
                	if '.' not in f:
                		msj='Al menos un campo de PRECIO contien un valor que no es decimal'
                		return(msj)
                	else:
                		nmsj='Todos los campos de PRECIO contien un valor decimal'
                		return(nmsj)

#_________________________BLOQUE RUTAS__________________________________________________________
#inicio
@app.route('/')
def index():
    return render_template('index.html', fecha_actual=datetime.utcnow(),)


#listar los n productos mas vendidos
@app.route('/ranking_productos')
def RankingPro():
    try: 
        apd = AbrirPD()
        respuesta = apd.groupby(by=['PRODUCTO'], as_index=False).sum()
        respuesta = respuesta.sort_values(by=['CANTIDAD'], ascending = False) 
        return render_template('rankingprod.html', rankpro=respuesta)
    except FileNotFoundError:
        return render_template('archnoenexiste.html')

#listar los n clientes que mas plata gastaron
@app.route('/ranking_clientes')
def RankingCLi():
    try:   
        apd = AbrirPD()
        apd['GASTO'] = apd['CANTIDAD']*apd['PRECIO']
        cocli = apd.groupby(by=['CLIENTE'], as_index=False).sum() 
        result = cocli.sort_values(by=['GASTO'], ascending = False)
        return render_template('rankingcli.html', rankcli = result )
    except FileNotFoundError:
        return render_template('archnoenexiste.html')


#listar todos los clientes que compraron un determinado producto:
@app.route('/consulta_producto',methods=['GET', 'POST'])
def Consulta_Producto():
    try:
        formulario = ProductoForm()
        var=str(formulario.consulta.data) 
        par=len(var)                      
        lce = []
        if par >= 3:         
            listacli = ListaPro()
            lfo = []   
            lfo.append(var.upper())   
            for l in listacli:  
                l=l.upper()
                if lfo[0] == l[:par]:
                    pto = l     
                    lce.append(pto)
        else:
            flash('ingrese por lo menos 3 letras')    
        if len(lce) == 1:
            cna = ['CODIGO','CLIENTE','PRODUCTO','CANTIDAD'] 
            apd = AbrirPD()    
            for l in lce:
                W=l
                procli = apd[apd.PRODUCTO.str.upper() == W.upper()] 
                tabla = procli.groupby(by=cna, as_index=False).sum()
                return render_template('consultaproducto.html', tabla = tabla, form=formulario)
        else:
            return render_template('opcionespro.html',D=lce,form=formulario)
    except FileNotFoundError:
        return render_template('archnoenexiste.html')

#listar todos los productos que compro un cliente:
@app.route('/consulta_cliente',methods=['GET', 'POST'])
def Consulta_Cliente():
    try:
        formulario = ClienteForm()
        var=str(formulario.consulta.data) 
        par=len(var)                      
        lce = []
        if par >= 3:         
            listacli = ListaCli()
            lfo = []
            lfo.append(var.upper())   
            for l in listacli:  
                l=l.upper()
                if lfo[0] == l[:par]:
                    pto = l     
                    lce.append(pto)
        else:
            flash('ingrese por lo menos 3 letras')    
        if len(lce) == 1:
            cna = ['CODIGO','CLIENTE','PRODUCTO','CANTIDAD']  
            apd = AbrirPD()
            for l in lce:
                W=l
                clipro = apd[apd.CLIENTE.str.upper() == W.upper()] 
                tabla = clipro.groupby(by=cna, as_index=False).sum()
                return render_template('consultacliente.html', tabla = tabla, form=formulario)
        else:
            return render_template('opcionescli.html',D=lce,form=formulario)
    except FileNotFoundError:
        return render_template('archnoenexiste.html')
#errores
@app.errorhandler(404)
def no_encontrado(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error_interno(e):
    return render_template('500.html'), 500


#ingresar
@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    formulario = LoginForm()
    if formulario.validate_on_submit():
        with open('usuarios') as archivo:
            archivo_csv = csv.reader(archivo)
            registro = next(archivo_csv)
            while registro:
                if formulario.usuario.data == registro[0] and formulario.password.data == registro[1]:
                    session['username'] = formulario.usuario.data
                    return redirect(url_for('ingresado'))
                registro = next(archivo_csv, None)
            else:
                flash('Revisá nombre de usuario y contraseña')
                return redirect(url_for('ingresar'))
    return render_template('login.html', formulario=formulario)


#Pagina de consulta + ultimas ventas y las validaciones
@app.route('/ingresado', methods=['GET'])
def ingresado():
    try:    
        try:
            A=Validar_Precio()
            B=Validar_Cantidad()
            C=Validar_codigo()
            D=Validar_cant_campos()
            E=VAlidar_Forma_Codigo()
            usuario = ('username' in session)
            vent =ListaCSV()
            ventas=vent[0:11]
            nombre = session['username']
            return render_template('ingresado.html', miListado=ventas, name=nombre,A=A,B=B,C=C,D=D,E=E)
        except FileNotFoundError:
            return render_template('archnoenexiste.html')
    except KeyError:
        return redirect(url_for('ingresar'))

#registrar
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    formulario = RegistrarForm()
    if formulario.validate_on_submit():
        if formulario.password.data == formulario.password_check.data:
            with open('usuarios', 'a+') as archivo:
                archivo_csv = csv.writer(archivo)
                registro = [formulario.usuario.data, formulario.password.data]
                archivo_csv.writerow(registro)
            flash('Usuario creado correctamente')
            return redirect(url_for('ingresar'))
        else:
            flash('Las passwords no matchean')
    return render_template('registrar.html', form=formulario)


@app.route('/secret', methods=['GET'])
def secreto():
    if 'username' in session:
        return render_template('private.html', username=session['username'])
    else:
        return render_template('sin_permiso.html')

#salida
@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        return render_template('logged_out.html')
    else:
        return redirect(url_for('index'))


if __name__ == "__main__":
    manager.run()
