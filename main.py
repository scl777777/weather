from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="获取天气 API")

@app.get("/")
async def root():
    return {"message": "欢迎使用获取天气API！请访问 /weather/{城市名拼音} 以获取天气"}

@app.get("/weather/{city}")
async def get_weather(city: str):
    async with httpx.AsyncClient() as client:
        # 第一步：调用地理编码 API，把城市名转换成经纬度
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city} & count=1"
        geo_response = await client.get(geo_url)
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            raise HTTPException(status_code=404, detail=f"非有效城市: {city}")

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        real_city_name = geo_data["results"][0]["name"]

        # 第二步：拿经纬度去查询天气
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude = {lat} & longitude={lon} & current_weather=true"
        weather_response = await client.get(weather_url)
        weather_data = weather_response.json()

        # 第三步：提取需要的数据并返回
        current = weather_data["current_weather"]
        return {
            "city": real_city_name,
            "temperature_celsius": current["temperature"],
            "windspeed_kmh": current["windspeed"],
            "time": current["time"]
        }