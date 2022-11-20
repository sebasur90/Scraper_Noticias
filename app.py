import streamlit as st
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from scrapper_rss import Scrapper
import datetime as dt
import csv

def transforma_letras_para_wordcloud(dataframe_noticias):
    columna_analizada = list(dataframe_noticias['titulo'])
    acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
               'Á': 'A', 'E': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
    lista_palabras_para_wordcloud = []
    for palabras in columna_analizada:
        palabras_div = palabras.split(' ')
        for letras in palabras_div:
            for acen in acentos:
                if acen in letras:
                    letras = letras.replace(acen, acentos[acen])
            lista_palabras_para_wordcloud.append(letras.lower())
    return ' '.join(lista_palabras_para_wordcloud)


def genera_wordcloud(dataframe_noticias):
    palabras_para_wordcloud = transforma_letras_para_wordcloud(
        dataframe_noticias)
    palabras_ignoradas = set(['a', 'ante', 'con', 'contra', 'de', 'desde', 'durante', 'en', 'para', 'por', 'segun', 'sin', 'sobre', 'el', 'la', 'los', 'las',
                              '...', 'y', 'hoy', 'este', 'cuanto',  'un', 'del', 'las',  'que', 'con', 'todos',  'es', '¿qué',  'como', 'cada',
                              'jueves', '¿cuanto', 'hoy', 'al', 'cual', 'se', 'su', 'sus', 'lo', 'una', 'un', 'tiene',
                              'le', 'habia'])

    wordcloud = WordCloud(width=1920, height=1080, stopwords=palabras_ignoradas).generate(
        palabras_para_wordcloud)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot()




st.set_option('deprecation.showPyplotGlobalUse', False)

scrapper = Scrapper()

noticias = pd.read_csv('./diarios/diarios_historicos.csv')
noticias=noticias.drop('descripcion' ,axis=1)
fechas = pd.read_csv('./fechas.csv')


with open('./diarios.csv', 'r') as f:
    reader = csv.reader(f)
    diarios = set()
    secciones = set()
    for row in reader:
        if row[0] == 'diario':
            continue
        diarios.add(row[0])
        secciones.add(row[1])

columna_para_nube = ['titulo', 'descripcion']

st.set_page_config(
        page_title="Observatorio de noticias",        
        initial_sidebar_state="expanded"
    )

if "configurar_fuentes" not in st.session_state:
    st.session_state["configurar_fuentes"] = False



with st.sidebar:
    st.write("Creado por [sebasur90](https://www.linkedin.com/in/sebastian-rodriguez-9b417830/)")
    diarios_select = st.multiselect('Selecciona los  diarios',
                                    diarios, default=diarios)
    secciones_select = st.multiselect('Selecciona las secciones',
                                      secciones, default=secciones)
    palabra_buscada = st.text_input('Buscar palabra', 'Ninguna')

    if st.button('Actualizar Diarios'):
        dia_str = str(dt.datetime.today().date())
        if fechas.iloc[-1]['dia'] == dia_str:
            st.success("Las noticias ya estan actualizadas")
            pass
        else:
            with st.spinner('Actualizando los siguientes diarios..'):            
                scrapper.run()
                st.success("Se actualizaron las noticias")
            
    if st.button('Configurar Fuentes'):
        st.session_state["configurar_fuentes"] = True
        st.write("configurar fuentes")
    
    if st.button('Reiniciar Fechas'):
        with open('fechas.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['dia'])
            writer.writerow(['2022-05-29'])
        st.success("Se reiniciaron las fechas")

if st.session_state["configurar_fuentes"]:
    st.header("Configurar Fuentes")
    st.write("Agrega las fuentes que quieras")
    diario = st.text_input('Diario', 'Diario')
    seccion = st.text_input('Seccion', 'Seccion')
    rss = st.text_input('RSS', 'RSS')
    filas = []
    eliminables = []
    with open('./diarios.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            filas.append(row)
            if row[0] == 'diario':
                continue
            eliminables.append([row[0], row[1]])
    
    if st.button('Agregar'):
        if diario == 'Diario' and seccion == 'Seccion' and rss == 'RSS':
            st.error("No se puede agregar una fila vacia")
        else:
            for element in filas:
                if element[0] == diario and element[1] == seccion:
                    st.error("Ya existe esa fuente")
                    break
            else:  #no break       
                with open('./diarios.csv', 'w') as f:
                    filas.append([diario, seccion, rss])
                    eliminables.append([diario, seccion])
                    writer = csv.writer(f)
                    writer.writerows(filas)
                with open('fechas.csv', 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(['dia'])
                    writer.writerow(['2022-05-29'])
                st.success("Se agrego la fuente")
    eliminar = st.selectbox('Eliminar', eliminables)
    if st.button('Eliminar'):
        if len(filas) > 2:
            with open('./diarios.csv', 'w') as f:
                writer = csv.writer(f)
                for row in filas:
                    if row[0] == eliminar[0] and row[1] == eliminar[1]:
                        filaAEliminar = row
                    else:
                        writer.writerow(row)
                    
            st.experimental_rerun()
        else:
            st.error("No se puede eliminar la ultima fuente")
    if st.button('Volver'):
        st.session_state["configurar_fuentes"] = False
        st.experimental_rerun()
    st.dataframe(filas)
else:

    if (palabra_buscada == "Ninguna" or palabra_buscada == ""):
        st.title("Observatorio de Noticias")
        st.write("""            

                Hola! Bienvenido a la aplicación de análisis de sentimientos en las noticias. Esta aplicación extrae las noticias de algunos de los diarios mas
                importantes del país ( a traves del RSS) y realiza un analisis de sentimientos sobre los titulos de cada una.
                La app permite filtrar por palabra clave y generar una nube de palabras con los resultados 

                De acuerdo al sentimiento analizado sobre cada noticia encontraremos 3 grupos: 
                
                **Sentimiento Positivo:** "YPF aumentó la distribución de gasoil y aseguró que el campo tiene garantizado el abastecimiento" 
                *Probabilidades: NEGATIVA=0.008 ---  NEUTRA 0.43  ---    POSITIVA 0.56 (GANADOR --> POSITIVA)* 
                
                
                **Sentimiento Neutro:** "El aeroclub de Comodoro Rivadavia celebró su 87° aniversario"
                *Probabilidades: NEGATIVA=0.02 ---  NEUTRA 0.67  ---    POSITIVA 0.30 (GANADOR --> NEUTRA)* 
                
                **Sentimiento Negativo:** "Crecen las expectativas de inflación del mercado"
                *Probabilidades: NEGATIVA=0.60 ---  NEUTRA 0.37  ---    POSITIVA 0.15 (GANADOR --> NEGATIVA)* 
                
                """)
        
    else:
        #st.title("Observatorio de Noticias")
        st.header(f"Resultados para : {palabra_buscada}")
        
        noticias = noticias[noticias['titulo'].str.contains(palabra_buscada)]    

    st.session_state['dataframe_filtrado'] = noticias[(noticias.diario.isin(
        diarios_select)) & (noticias.seccion.isin(secciones_select))]

    st.subheader("Muestra aleatoria de noticias")
    st.dataframe(st.session_state['dataframe_filtrado'].sample(frac=1))
    st.session_state['dataframe_agrupado'] = st.session_state['dataframe_filtrado'].groupby(
        'diario')[['pond_negativos', 'pond_neutro', 'pond_positivo']].mean().reset_index()

    if not st.session_state['dataframe_agrupado'].empty:
        fig = px.bar(st.session_state['dataframe_agrupado'], x="diario", y=['pond_neutro', "pond_negativos", 'pond_positivo'], text_auto=True,
                    title=f"Analisis de sentimientos para las noticias seleccionadas según el diario"
                    )

        newnames = {'pond_neutro':'NEUTRAL', 'pond_negativos': 'NEGATIVA','pond_positivo': 'POSITIVA'}
        fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                            legendgroup = newnames[t.name],
                                            hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                            )
                        )
        fig.update_layout(
            xaxis_title="Diarios",
            yaxis_title="Probabilidades (de 0 a 1)",
            
        )                  
        fig.update_layout(legend_title_text='Probabilidades')

        st.plotly_chart(fig)
        if st.button('Generar Nube'):
            genera_wordcloud(st.session_state['dataframe_filtrado'])
        else:
            pass



