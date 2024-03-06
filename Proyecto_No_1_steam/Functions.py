import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from sklearn.preprocessing import StandardScaler

def developer(desarrollador):
    
    devv = pd.read_csv('data_fusionada.csv')
    data_filtrada = devv[devv['developer'] == desarrollador]
    por_año = data_filtrada.groupby('release_date')
    
    resultado = {}
    
    for año, grupo in por_año:
        total_items = len(grupo)
        items_gratis = len(grupo[grupo['price'] == 0])
        porcentaje_gratis = (items_gratis / total_items) * 100 if total_items > 0 else 0
        resultado[año] = {'Cantidad de Items': total_items, 'Contenido Free': f"{porcentaje_gratis:.0f}%"}
        
    return resultado

def userdata(user_id):

    udata = pd.read_csv('data_fusionada.csv')
    data_filtrada = udata[udata['user_id'] == user_id]
    dinero_gastado = data_filtrada['price'].sum()
    
    if len(data_filtrada) > 0:
        porcentaje_recomendacion = (data_filtrada['recommend'].sum() / len(data_filtrada)) * 100
    else:
        porcentaje_recomendacion = 0  
    
    cantidad_items = len(data_filtrada)
    
    resultado = {
        "Usuario": user_id,
        "Dinero gastado": f"{dinero_gastado} USD",
        "% de recomendación": f"{porcentaje_recomendacion:.0f}%",
        "Cantidad de ítems": cantidad_items
    }
    
    return resultado

def UserForGenre(genero):

    ufg = pd.read_csv('data_fusionada.csv')
    data_filtrada = ufg[ufg['genres'].str.contains(genero, case=False, na=False)].copy()
    data_filtrada['playtime_hours'] = data_filtrada['playtime_forever'] / 60

    usuario_max_horas = data_filtrada.groupby('user_id')['playtime_hours'].sum().idxmax()
    horas_por_año = data_filtrada.groupby('release_date')['playtime_hours'].sum().reset_index()
    
    horas_por_año.sort_values(by='release_date', inplace=True)
    horas_list_formatted = [{"Año": row['release_date'], "Horas": round(row['playtime_hours'], 2)} for index, row in horas_por_año.iterrows()]

    resultado = {
        "Usuario con más horas jugadas para Género": genero + " : " + usuario_max_horas,
        "Horas jugadas": horas_list_formatted
    }
    
    return resultado

def best_developer_year(año):
    
    bdy = pd.read_csv('data_fusionada.csv')
    filtered_data = bdy[(bdy['release_date'] == año) & (bdy['recommend'] == True) & (bdy['Sentiment_analysis'] > 0)]
    developer_counts = filtered_data.groupby('developer').size().reset_index(name='counts')
    sorted_developers = developer_counts.sort_values(by='counts', ascending=False).head(3)
    
    result = [{"Puesto 1": sorted_developers.iloc[0]['developer']}, 
              {"Puesto 2": sorted_developers.iloc[1]['developer']}, 
              {"Puesto 3": sorted_developers.iloc[2]['developer']}]
    
    return result

def developer_reviews_analysis(desarrolladora):
    
    dra = pd.read_csv('data_fusionada.csv')
    data_filtrada = dra[dra['developer'] == desarrolladora]
    
    negative_reviews = len(data_filtrada[data_filtrada['Sentiment_analysis'] == 0])
    neutral_reviews = len(data_filtrada[data_filtrada['Sentiment_analysis'] == 1])
    positive_reviews = len(data_filtrada[data_filtrada['Sentiment_analysis'] == 2])
    resultado = {desarrolladora: {"Negative": negative_reviews, "Positive": positive_reviews}}
    
    return resultado


def recomendacion_juego(item_id):
    df = pd.read_csv('dataML_item_item.csv')
    
    
    if item_id not in df['item_id'].unique():
        juegos_populares = df.groupby('app_name')['playtime_forever'].sum().nlargest(5).index.tolist()
        return juegos_populares
    
    df['item_id'] = df['item_id'].astype(int)
    
    juegos_df = df.groupby('item_id').agg({
        'recommend': 'sum',
        'playtime_forever': 'mean',
        'genres': 'mean'
    }).reset_index()
    
    scaler = StandardScaler()
    juegos_df_scaled = scaler.fit_transform(juegos_df[['recommend', 'playtime_forever', 'genres']])
    
    # Calcular la similitud del coseno
    similitudes = cosine_similarity(juegos_df_scaled)
    similitudes_df = pd.DataFrame(similitudes, index=juegos_df['item_id'], columns=juegos_df['item_id'])
    
    juegos_similares = similitudes_df[item_id].drop(item_id).nlargest(5).index.tolist()
    nombres_juegos_similares = df[df['item_id'].isin(juegos_similares)]['app_name'].drop_duplicates().tolist()
    
    return nombres_juegos_similares
    

def recomendacion_usuario(user_id):
    
    columnas = ['user_id', 'item_id', 'recommend', 'app_name', 'Sentiment_analysis']
    df = pd.read_csv('dataML_user_item.csv', usecols=columnas)
    top_n = 5
    
    df['interaction'] = df['recommend'].astype(int)
    
    # Crear la matriz de utilidad
    matriz_utilidad = df.pivot_table(index='user_id', columns='item_id', values='interaction', fill_value=0)
    
    # Calcular la similitud de coseno entre usuarios
    similitudes = cosine_similarity(matriz_utilidad)
    similitudes_df = pd.DataFrame(similitudes, index=matriz_utilidad.index, columns=matriz_utilidad.index)
    
    juegos_recomendados_nombres = []
    
    # Comprobar si el ID de usuario existe
    if user_id in similitudes_df.index:
        # Encontrar usuarios similares
        usuarios_similares = similitudes_df[user_id].sort_values(ascending=False)[1:11]
        
        # Recopilar recomendaciones de item_id
        juegos_recomendados = set()
        for usuario_similar in usuarios_similares.index:
            juegos_usuario_similar = set(matriz_utilidad.columns[(matriz_utilidad.loc[usuario_similar] > 0)])
            juegos_usuario = set(matriz_utilidad.columns[(matriz_utilidad.loc[user_id] > 0)])
            juegos_recomendados.update(juegos_usuario_similar.difference(juegos_usuario))
        
        # Convertir item_id recomendados a nombres de juegos
        juegos_recomendados_nombres = df[df['item_id'].isin(juegos_recomendados)]['app_name'].drop_duplicates().tolist()

    # Complementar con juegos populares si hay menos de top_n recomendaciones
    if len(juegos_recomendados_nombres) < top_n:
        juegos_populares_nombres = df[df['recommend'] == 1]['app_name'].value_counts().index.tolist()
        # Excluir los ya recomendados por nombre
        juegos_populares_nombres = [juego for juego in juegos_populares_nombres if juego not in juegos_recomendados_nombres]
        # Complementar recomendaciones hasta alcanzar top_n
        juegos_recomendados_nombres += juegos_populares_nombres[:top_n - len(juegos_recomendados_nombres)]
    
    # Si el usuario no existe en la base de datos, recomendar los juegos más populares
    if not juegos_recomendados_nombres:
        juegos_recomendados_nombres = df[df['recommend'] == 1]['app_name'].value_counts().head(top_n).index.tolist()
    
    return juegos_recomendados_nombres[:top_n]
