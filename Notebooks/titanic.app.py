# --------------------LIBRERÍAS---------------------------------------------------#

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import streamlit as st


# --------------------CONFIGURACIÓN DE LA PÁGINA----------------------------------#

# layout="centered" or "wide".
st.set_page_config(page_title='Informe sobre Titanic', layout='wide', page_icon='🚢')

logo1 = "img/logo_main.png"
logo2 = "img/logo_sidebar.jpg"

st.write(f"<p style='font-size:40px; text-align:center; margin-top:-490px; font-weight: bold; text-decoration: underline;'>INFORME TITANIC</p>", unsafe_allow_html=True)
st.image(logo1, width=1000)


# Descripción
descripcion = """El hundimiento del Titanic es uno de los eventos más trágicos y emblemáticos en la historia marítima.<Br>
En la noche de abril de 1912, este majestuoso transatlántico chocó contra un iceberg en su viaje inaugural desde Southampton hacia Nueva York.<Br>
En este proyecto de análisis de datos, analizaremos a sus pasajeros, quiénes eran, qué edad tenían, de qué clase social venían y
quiénes lograron sobrevivir.<br>
Los invito a que naveguemos juntos por los datos del Titanic, buscando respuestas y revelaciones.""" 
st.write(f"<p style='font-size:14px; text-align:center;'>{descripcion}</p>", unsafe_allow_html=True)

# --------------------SIDEBAR------------------------------------------------------#

# Contenido adicional del sidebar

st.sidebar.image(logo2, use_column_width=True)
st.sidebar.title('Filtros')
st.sidebar.write('-------')

# --------------------COSAS QUE VAMOS A USAR EN TODA LA APP------------------------#
df = pd.read_csv(r"Data//titanic.csv")

# Para reemplazar los valores nulos de las edades voy a usar un enfoque de agrupación.
# Voy a agrupar los datos por las columnas "Embarked" y "Pclass" y luego calcular la mediana de la columna "Age" dentro de cada grupo.
# Luego, voy a usar estas medianas calculadas para reemplazar los valores nulos en la columna "Age". """ 

median_grupo = df.groupby(['Embarked', 'Pclass'])['Age'].transform(lambda x: x.median())
df['Age'] = df['Age'].fillna(median_grupo)

# Convierto la edad en una variable numérica discreta tomando valores enteros
df["Age"] = df["Age"].astype(int, errors='ignore') #'coerce'

# Reemplazo los valores nulos de "Embarked" con la moda
moda_embarked = df['Embarked'].mode()[0]
df['Embarked'] = df['Embarked'].fillna(moda_embarked)

# Añado la columna "Acompañantes"
df['Acompañantes'] = df['SibSp'] + df['Parch']

# Elimino las columnas "SibSp", "Parch", "Ticket" y "Cabin" ya que son irrelevantes para mi análisis
df.drop(['SibSp', 'Parch', 'Ticket', 'Cabin'], axis=1, inplace=True)

# Agrego la columna "Grupo de edad"
bins = [0, 18, 30, 50, 100]
labels = ['0-18', '19-30', '31-50', '51+']
df['Grupo de Edad'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)

# Cambio el nombre de las columnas
nombres_columnas = {
    'PassengerId': 'ID pasajero',
    'Survived': 'Supervivencia',
    'Pclass': 'Clase',
    'Name': 'Nombre',
    'Sex': 'Género',
    'Age': 'Edad',
    'Fare': 'Tarifa',
    'Embarked': 'Puerto de embarque',
    'Grupo de Edad': 'Grupo de Edad', 
    'Acompañantes': 'Acompañantes'}

df = df.rename(columns=nombres_columnas)

# Cambio la descripcion de los valores
df['Género'] = df['Género'].replace({'male': 'Hombre', 'female': 'Mujer'})
df['Puerto de embarque'] = df['Puerto de embarque'].replace({'Q':'Queenstown', 'S':'Southampton', 'C':'Cherbourg'})

# Cambio el orden de las columnas
nuevo_orden_columnas = ['ID pasajero', 'Nombre', 'Género', 'Edad', 'Grupo de Edad', 'Acompañantes', 'Clase', 'Tarifa', 'Puerto de embarque', 'Supervivencia']

df = df[nuevo_orden_columnas]



# --------------------SIDEBAR FILTRO 1-----------------------------#

edad = sorted(df['Grupo de Edad'].unique())
filtro_edad = st.sidebar.selectbox('Edad', ['Seleccionar todo'] + list(edad))

# Aplicar filtro de edad
if filtro_edad != "Seleccionar todo":
    df1 = df[df['Grupo de Edad'] == filtro_edad]
else:
    df1 = df.copy()

# --------------------SIDEBAR FILTRO 2-----------------------------#

genero = sorted(df['Género'].unique())
filtro_genero = st.sidebar.selectbox('Género', ['Seleccionar todo'] + list(genero))

# Aplicar filtro de género
if filtro_genero != "Seleccionar todo":
    df1 = df1[df1['Género'] == filtro_genero]

# --------------------SIDEBAR FILTRO 3-----------------------------#

clase = sorted(df['Clase'].unique())
filtro_clase = st.sidebar.selectbox('Clase', ['Seleccionar todo'] + list(clase))

# Aplicar filtro de clase
if filtro_clase != "Seleccionar todo":
    df1 = df1[df1['Clase'] == filtro_clase]


# --------------------SIDEBAR FILTRO 4-----------------------------#

survived = {0: "No sobreviviente", 1: "Sobreviviente"}
opciones_survival = df1['Supervivencia'].map(survived).unique()
filtro_survival = st.sidebar.selectbox('Supervivencia', ['Seleccionar todo'] + list(opciones_survival))

# Aplicar filtro de supervivencia
if filtro_survival != "Seleccionar todo":
    filtro_survival = next(key for key, value in survived.items() if value == filtro_survival)
    df1 = df1[df1['Supervivencia'] == filtro_survival]

# --------------------UNION DE FILTROS----------------------------#

if filtro_clase != "Seleccionar todo" and filtro_genero != "Seleccionar todo" and filtro_survival != "Seleccionar todo" and filtro_edad != "Seleccionar todo":
    df2 = df1.loc[(df1['Clase'] == filtro_clase) & (df1['Género'] == filtro_genero) & (df1['Supervivencia'] == filtro_survival) & (df1['Grupo de Edad'] == filtro_edad)] 
else:
    df2 = df1.copy()  

# --------------------TABS------------------------------------------#

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [   "Introducción",
        "Análisis por edad",
        "Análisis por clase",
        "Análisis por género y embarque",
        "Análisis por compañía",
        "Conclusiones"
        ])


# --------------------TAB 1----------------------------#

# Introducción

with tab1:

    texto_central = 'Naveguemos juntos a través de los datos del Titanic'
    st.markdown(f"<h2 style='text-align: left; font-size:30px;'>{texto_central}</h2>", unsafe_allow_html=True)

    df2 = df2.drop(columns=['ID pasajero', 'Grupo de Edad'])

    st.dataframe(df2)

# Descripcion
    
    encabezado= "Descripción del dataset:"
    st.write(f"<p style='font-size:15px; text-align:left;text-decoration: underline;'>{encabezado}</p>", unsafe_allow_html=True)
    descripcion = """
- Nombre: Nombre completo de cada pasajero.<br>
- Género: Indica el sexo del pasajero.<br> 
- Edad: Edad del pasajero en el momento del hundimiento del Titanic.<br>
- Acompañantes: Indica la cantidad de acompañantes (familiares) del pasajero.<br>
- Clase: Representa la clase en la que viajaba el pasajero. Puede tener los valores 1, 2 o 3, que corresponden a primera, segunda y tercera clase respectivamente.<br>
- Tarifa: Precio pagado por el pasajero por el viaje.<br>
- Puerto de embarque: Puerto de embarque del pasajero.<br>
- Supervivencia: Indica si el pasajero sobrevivió al hundimiento del Titanic o no: 1 para sobreviviente y 0 para no sobreviviente.<br>
"""
    st.write(f"<p style='font-size:15px; text-align:left;'>{descripcion}</p>", unsafe_allow_html=True)


# --------------------TAB 2----------------------------#

# Análisis de los pasajeros por edad.

with tab2:

    texto_central = """Comenzamos nuestro viaje analizando la composición de los pasajeros a bordo del Titanic.<Br>
    ¿Quiénes eran estas personas que embarcaron en esta icónica travesía?"""
    st.markdown(f"<h2 style='text-align: center; font-size:30px; '>{texto_central}</h2>", unsafe_allow_html=True) 

    with tab2:
        col1, col2 = st.columns([2,2])
           
        with col1:
        
            fig = go.Figure()

            trazo = go.Histogram(
                x=df['Edad'],
                marker_color='lightgreen')
            
            fig.add_trace(trazo)

            fig.update_layout(
                xaxis_title='Edad',
                yaxis_title='Pasajeros',
                xaxis_showgrid=False,
                yaxis_showgrid=False,
                title=dict(
                    text='Distribución de edades', 
                    x=0.5,
                    y=0.9,
                    xanchor='center',
                    yanchor='top'))
                    
            st.plotly_chart(fig, use_container_width=True)

    # Comentarios
            Frase_1 = """Edad promedio de los pasajeros: 25 años.<br>
            Edad mínima: 5 meses / Edad máxima: 80 años."""
            st.markdown("<br>", unsafe_allow_html=True)
            st.write(f"<p style='font-size:16px;text-align:center;margin-top:-50px;'><strong>{Frase_1}</strong></p>", unsafe_allow_html=True)
            

        with col2:

            bins = [10, 20, 30, 40, 50, 60, 70, 80]
            labels = ['0-10', '10-20', '20-30', '30-40', '50-60', '60-70', '70-80']
            df['Grupo de edades'] = pd.cut(df['Edad'], bins=bins, labels=labels)
            survival_by_age_group = df.groupby('Grupo de edades')['Supervivencia'].mean().reset_index()

            fig = px.bar(
            survival_by_age_group,
            x='Grupo de edades',
            y='Supervivencia',
            color='Supervivencia',
            color_continuous_scale='burg')
            
            fig.update_layout(
                title=dict(
                    text='Tasa de Supervivencia por grupos de edad', 
                    x=0.5,
                    y=0.9,
                    xanchor='center',
                    yanchor='top'),  
                xaxis_title='Grupo de edades',
                yaxis_title='Tasa de Supervivencia',
                xaxis_showgrid=False,
                yaxis_showgrid=False,
                title_x=0.35)

            
            st.plotly_chart(fig, use_container_width=True)

# Comentarios

            Frase_1="""Edad promedio de sobrevivientes: 27 años. <Br>
            Pasajeros entre 20 y 30 años tuvieron mayor probabilidad de sobrevivir."""
            st.markdown("<br>", unsafe_allow_html=True)
            st.write(f"<p style='font-size:16px;text-align:center;margin-top:-50px;'><strong>{Frase_1}</strong></p>", unsafe_allow_html=True)

    st.write('------')

# Comentarios

    texto_central = """ Al analizar datos, descubro que el 7% eran niños entre 5 meses y 10 años. <Br>
    El 59% de ellos pudieron sobrevivir ya que en su momento priorizaban a las mujeres y niños para subir a bordo de los barcos salvavidas.<Br>
    Pero a la hora de salvar vidas..."""
    texto2= "¿Realmente importaba la clase social?"
    st.markdown(f"<h2 style='text-align: center;margin-top:-15px; font-size:18px;'>{texto_central}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; font-size:30px; color: blue;'><b>{texto2}</b></h2>", unsafe_allow_html=True)


# Ultimas 2 tablas:

    with st.container():

        col3, col4, col5, col6 = st.columns([1,1,1,1])

        with col3:

            st.write('')
        
        with col4:
            
# Tabla de Distribucion de mujeres y niños por clase
            
            niños = df[(df['Edad'] >= 0) & (df['Edad'] <= 10)]
            distribucion_clases_niños = niños['Clase'].value_counts().sort_index()

            mujeres = df[df['Género'] == 'Mujer']
            distribucion_mujeres_por_clase = mujeres['Clase'].value_counts().sort_index()

            nuevo_dataframe = pd.DataFrame({'Mujeres': distribucion_mujeres_por_clase, 'Niños': distribucion_clases_niños})     

            st.markdown("<div style='text-left: center;'><b>Distribución por clase:</b></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)  

            st.write(nuevo_dataframe)

            #s1 = dict(selector='th', props=[('text-align', 'center')])
            #s2 = dict(selector='td', props=[('text-align', 'center')])

            #table = nuevo_dataframe.style.set_table_styles([s1,s2]).hide(axis=0).to_html()    
            #st.write(f'{table}', unsafe_allow_html=True)


        with col5:

         # Tabla de Tasa de supervivencia de mujeres y niños por clase

            tasa_supervivencia_niños_clase = niños.groupby('Clase')['Supervivencia'].mean()*100
            tasa_supervivencia_mujeres_clase = mujeres.groupby('Clase')['Supervivencia'].mean()*100
            
            nuevo_dataframe2 = pd.DataFrame({'Mujeres': tasa_supervivencia_mujeres_clase.round(0), 'Niños': tasa_supervivencia_niños_clase.round(0)})

            st.markdown("<div style='text-left: center;'><b>Tasa de supervivencia (%) por clase:</b></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)    

            st.write(nuevo_dataframe2)
            
        with col6:

            st.write('')
        
           
# Comentarios

    texto1 = """A la hora de salvar niños no importaba su posición social.<Br>
    Pero en cuanto a las mujeres, la tasa de supervivencia en la 1era clase fue considerablemente mayor."""
    st.markdown(f"<h2 style='text-align: center; font-size:18px;'>{texto1}</h2>", unsafe_allow_html=True)
    texto2 =  "Esto indica que a la hora de salvar vidas, la posición socioeconómica era de gran importancia."
    st.markdown(f"<h2 style='text-align: center; font-size:30px;'>{texto2}</h2>", unsafe_allow_html=True)

# --------------------TAB 3----------------------------#

# Análisis de pasajeros por clase.

with tab3:
    texto_central = """¿Había alguna tendencia de supervivencia por clase?<Br>
    ¿La tarifa pagada por un pasajero se correlaciona con su probabilidad de supervivencia?.<Br>"""
    st.markdown(f"<h2 style='text-align: center; font-size:30px;'>{texto_central}</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1:
            
            colors = {'Clase 1': '#FF6633', 'Clase 2': '#FF9966', 'Clase 3': '#FFCC99'}

            #Grafico 1:
            total_pasajeros = len(df)
            clase1 = df[df['Clase'] == 1]['ID pasajero'].count() 
            clase2 = df[df['Clase'] == 2]['ID pasajero'].count()
            clase3 = df[df['Clase'] == 3]['ID pasajero'].count() 

            clases = [clase1, clase2, clase3]

            # Calculo los porcentajes
            total_pasajeros = len(df)
            porcen_clase1 = (clase1/total_pasajeros)*100
            porcen_clase2 = (clase2/total_pasajeros)*100
            porcen_clase3 = (clase3/total_pasajeros)*100

            porcentaje = [porcen_clase1, porcen_clase2, porcen_clase3]

            etiquetas = ['Clase 1', 'Clase 2', 'Clase 3']
            
            fig = px.bar(
                x=etiquetas,
                y=porcentaje,
                color=etiquetas,
                color_discrete_map=colors)
            
            fig.update_layout(title='Distribución de pasajeros por clases',
                              yaxis_title='Distribución de clases (%)',
                              showlegend=False,
                              xaxis_showgrid=False,
                              yaxis_showgrid=False,
                              xaxis_title='',
                              title_x=0.30)
            
            st.plotly_chart(fig, use_container_width=True)

# Comentarios

            Frase_1 = 'Más de la mitad de los pasajeros viajaban en la 3era clase.'
            st.write(f"<p style='font-size:14px;text-align:center;margin-top:-50px;'><strong>{Frase_1}</strong></p>", unsafe_allow_html=True)


        with col2:

            total_survived = df['Supervivencia'].sum()
            survived_by_class = df.groupby('Clase')['Supervivencia'].sum()
            percentage_survived_by_class = (survived_by_class / total_survived) * 100

            etiquetas = ['Clase 1', 'Clase 2', 'Clase 3']
            colors = {'Clase 3': '#FFCC99', 'Clase 2': '#FF9966', 'Clase 1': '#FF6633'}

            fig = px.bar(
                x=etiquetas,
                y=percentage_survived_by_class,
                color=etiquetas,
                color_discrete_map=colors)

            fig.update_layout(
                title='Tasa de supervivencia por clase',
                yaxis_title='Tasa de Supervivencia (%)',
                showlegend=False,
                xaxis_showgrid=False,
                yaxis_showgrid=False,
                xaxis_title='',
                title_x=0.4)
            
            st.plotly_chart(fig, use_container_width=True)
        
 # Comentarios

            Frase_1 = 'Los de 1era clase tuvieron mayor porcentaje de supervivencia.'
            st.write(f"<p style='font-size:14px;text-align:center;margin-top:-50px;'><strong>{Frase_1}</strong></p>", unsafe_allow_html=True)


        with col3:

            fig = px.box(
            df,
            x='Clase',
            y='Tarifa',
            color='Clase',
            color_discrete_sequence=['#FFCC99', '#FF6633', '#FF9966'])

            fig.update_layout(
            title="Distribución de tarifas por clase",
            xaxis_title="",
            showlegend=False,
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            title_x=0.3)

            st.plotly_chart(fig, use_container_width=True)

# Comentarios

            Frase_1 = 'El precio de la primera clase era significativamente mayor a la de las otras 2 clases.'
            st.write(f"<p style='font-size:14px;text-align:center;margin-top:-50px;'><strong>{Frase_1}</strong></p>", unsafe_allow_html=True)

        Frase_1=('Esto indica que la probabilidad de sobrevivir era mayor en aquellos en primera clase.')
        st.write(f"<p style='font-size:20px; text-align:center;color:#FF6633;'><b>{Frase_1}</b></p>", unsafe_allow_html=True)
    
# --------------------TAB 4----------------------------#

# Análisis de los pasajeros por género y puerto de embarque

with tab4:

    st.write(f"<p style='font-size:30px;text-align:center;'><strong>Ruta del Titanic</strong></p>", unsafe_allow_html=True)
    st.markdown(""" <div style='display: flex; justify-content: center;'>
        <img src='https://elhundimiento.weebly.com/uploads/9/7/5/0/9750962/4910672.jpg?531' width='700'></div>""", unsafe_allow_html=True)

    texto_central = '¿El puerto de embarque tenía alguna relación con la probabilidad de sobrevivir?'
    st.markdown(f"<h2 style='text-align: center; font-size:30px;'>{texto_central}</h2>", unsafe_allow_html=True)
    
    with tab4:
        col1, col2, col3 = st.columns([1,2,1])
       
        with col1:

            st.markdown("<br><br><br><br>", unsafe_allow_html=True)
            st.write(f"<p style='font-size:18px; text-align:center;'><b>Distribución:<Br>65% hombres vs 35% mujeres.<Br></b></p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.write(f"<p style='font-size:20px; text-align:center;'><b>Tasa de supervivencia:<br><span style='color: skyblue;'>19%</span> hombres vs <span style='color: salmon;'>74%</span> mujeres</b></p>", unsafe_allow_html=True)
                  
       
            with col2:

                recuento_pasajeros_por_genero_embarked = df.groupby(['Género', 'Puerto de embarque']).size().reset_index(name='Count')

                fig = px.bar(recuento_pasajeros_por_genero_embarked, 
                x='Puerto de embarque',
                y='Count',
                color='Género', barmode='group',
                labels={'Puerto de embarque':'Puerto de embarque', 'Count': 'Cantidad de Pasajeros', 'Género':''},
                title='Pasajeros por género y puerto de embarque',
                color_discrete_map={'Mujer': 'salmon', 'Hombre': 'lightblue'})

                fig.update_layout(
                xaxis_showgrid=False,
                yaxis_showgrid=False,
                legend=dict(orientation='h', yanchor='top', y=1.1, xanchor='center', x=0.35),
                title=dict(x=0.5,y=0.9,xanchor='center',yanchor='top',pad=dict(b=10)))
                
                st.plotly_chart(fig, use_container_width=True)


    with col3:

            st.markdown("<br>", unsafe_allow_html=True)

            tasa_supervivencia_por_genero_embarked = df.groupby(['Puerto de embarque', 'Género'])['Supervivencia'].mean().reset_index()
            tasa_supervivencia_por_genero_embarked['Supervivencia'] *= 100
            tasa_supervivencia_por_genero_embarked['Supervivencia'] = tasa_supervivencia_por_genero_embarked['Supervivencia'].round(0)
            tasa_supervivencia_por_genero_embarked['Supervivencia'] = tasa_supervivencia_por_genero_embarked['Supervivencia'].astype(str) + '%'

            st.markdown("""
                        <p style="text-align:center;
                        font-weight:bold;
                        background-color:white;
                        font-size: 16px;
                        ">Porcentaje de supervivencia por puerto de embarque y género:</p>""",
                        unsafe_allow_html=True)

            s1 = dict(selector='th', props=[('text-align', 'center'), ('font-size', '13px')])
            s2 = dict(selector='td', props=[('text-align', 'center'), ('font-size', '12px')])

            table = tasa_supervivencia_por_genero_embarked.style.set_table_styles([s1,s2]).hide(axis=0).to_html()    
            st.write(f'{table}', unsafe_allow_html=True)

# Comentarios

    Frase_1=(""" Para ambos géneros hubo un mayor número de supervivientes para pasajeros que embarcaron en Cherbourg """)
    st.write(f"<p style='font-size:20px; text-align:center;margin-top:-15px;'><b>{Frase_1}</b></p>", unsafe_allow_html=True)

 # --------------------TAB 5----------------------------#

# Análisis de pasajeros por compañía.

with tab5:

    texto_central = '¿Tenían mas posibilidades de sobrevivir aquellos que viajaban solos o acompañados?'
    st.markdown(f"<h2 style='text-align: center; font-size:30px;'>{texto_central}</h2>", unsafe_allow_html=True)

    with tab5:
        col1, col2 = st.columns([2,1])
        with col1:

            viaja_solo = df[df['Acompañantes'] == 0]['ID pasajero'].count()
            viaja_acompañado = df[df['Acompañantes'] > 0]['ID pasajero'].count()
            total_pasajeros = viaja_solo + viaja_acompañado
            porcentaje_solo = (viaja_solo / total_pasajeros) * 100
            porcentaje_acompañado = (viaja_acompañado / total_pasajeros) * 100
            porcentajes = [porcentaje_solo, porcentaje_acompañado]

            etiquetas = ['Solo', 'Acompañado']
            colors = {'Solo': '#D2B48C', 'Acompañado': '#FFCC99'}

            fig = px.bar(
                x=etiquetas,
                y=porcentajes,
                color=etiquetas,
                color_discrete_map=colors)
            
            fig.update_layout(title='Porcentaje de pasajeros que viajaban solos vs acompañados',
                              yaxis_title='Pasajeros',
                              showlegend=False,
                              xaxis_showgrid=False,
                              yaxis_showgrid=False,
                              xaxis_title='',
                              title_x=0.30)
            
            st.plotly_chart(fig, use_container_width=True)


        with col2:
            
            st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
            Frase1=(""" 60% de los pasajeros viajaban solos <Br> La probabilidad de sobrevivir era <Br>""")
            st.write(f"<p style='font-size:20px; text-align:center;'><b>{Frase1}</b></p>", unsafe_allow_html=True)
            
            Frase2=(' 20% mayor para los que iban acompañados.')
            st.write(f"<p style='font-size:30px; text-align:center;'><b>{Frase2}</b></p>", unsafe_allow_html=True)


# --------------------TAB 6----------------------------#

# Conclusiones

with tab6:

    texto_central = 'Conclusiones'
    st.markdown(f"<h2 style='text-align: center; font-size:35px;'>{texto_central}</h2>", unsafe_allow_html=True)

    Encabezado=(""" En este proyecto analicé datos de los pasajeros del Titanic
                para confirmar o refutar algunas teorías sobre la probabilidad de supervivencia de los pasajeros """)
    
    Frase1= "🚢 Supervivencia vs clase social:"
    Frase1bis= ("""Según el resultado del análisis, a la hora de salvar niños no importaba su posición social,
            pero en cuanto a las mujeres, a la hora de salvar vidas la posición socioeconómica era de gran importancia.<Br>
            Aquellos en la primera clase tenían una mayor probabilidad de sobrevivir en comparación con los pasajeros que viajaban en la tercera clase.<Br>""")
    
    Frase2= ('🚢 Supervivencia vs género:')
    Frase2bis=("""Los datos muestran que si bien el 65% de pasajeros eran hombres,
            la supervivencia de las mujeres fue 74% en comparacion del 18% para hombres. """)

    Frase3 = ('🚢 Supervivencia vs tipo de compañía:')
    Frase3bis = ("""La probabilidad de sobrevivir era un 20% mayor para los pasajeros que iban acompañados.""")
    
    Frase4 = ('🚢 Supervivencia vs Tarifa de billete:')
    Frase4bis = ("""La diferencia en las tarifas se tradujo no sólamente en diferencias en las condiciones de vida a bordo
            sino que también en las posibilidades de supervivencia durante el naufragio. Hubo mayor sobrevivientes en la primera clase.""")


    Frase5="""En resumen, el análisis de datos nos ofrece una ventana única para comprender las complejas dinámicas sociales
    y económicas que estaban en juego durante el desafortunado hundimiento del Titanic."""

    st.write(f"<p style='font-size:17px; text-align:left;'><b>{Encabezado}</b></p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:15px; text-align:left;'><b>{Frase1}</b></p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:15px; text-align:left;margin-top:-8px;'>{Frase1bis}</p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:15px; text-align:left;'><b>{Frase2}</b></p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:15px; text-align:left;margin-top:-8px;'>{Frase2bis}</p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:15px; text-align:left;'><b>{Frase3}</b></p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:15px; text-align:left;margin-top:-8px;'>{Frase3bis}</p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:15px; text-align:left;'><b>{Frase4}</b></p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:15px; text-align:left;margin-top:-8px;'>{Frase4bis}</p>", unsafe_allow_html=True)

    
    st.markdown("<br>", unsafe_allow_html=True)
    st.write(f"<p style='font-size:20px; text-align:left;'><b>{Frase5}</b></p>", unsafe_allow_html=True)

