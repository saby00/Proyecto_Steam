from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Optional
from Functions import *

app = FastAPI()

@app.get("/developer/{developer_name}")
async def get_developer_stats(developer_name: str):
    result = developer(developer_name)
    return JSONResponse(content=result)
# print(get_developer_stats('Valve'))

@app.get("/userdata/{user_id}")
async def get_user_data(user_id: str):
    result = userdata(user_id)
    return JSONResponse(content=result)

@app.get("/UserForGenre/{genre}")
async def get_user_for_genre(genre: str):
    result = UserForGenre(genre)
    return JSONResponse(content=result)

@app.get("/best_developer_year/{year}")
async def get_best_developer(year: int):
    result = best_developer_year(year)
    return JSONResponse(content=result)

@app.get("/developer_reviews_analysis/{developer_name}")
async def get_developer_reviews(developer_name: str):
    result = developer_reviews_analysis(developer_name)
    return JSONResponse(content=result)

@app.get("/recomendacion_juego/{id_producto}")
async def get_recomendacion_juego(id_producto: int):
    result = recomendacion_juego(id_producto)
    return JSONResponse(content=result)

@app.get("/recomendacion_usuario/{id_usuario}")
async def get_recomendacion_usuario(id_usuario: str):
    result = recomendacion_usuario(id_usuario)
    return JSONResponse(content=result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)