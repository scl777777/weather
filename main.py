from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="获取天气 API")

@app.get("/")
async def root():
    return {"message": "欢迎使用获取天气API！请访问 /weather/{城市名拼音} 以获取天气"}


@app.get("/weather/{city}")
async def get_weather(city: str):
    # 伪装成正常的电脑浏览器，防止被 API 拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        # 第一步：调用地理编码 API
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = await client.get(geo_url)

        # 🛡️ 防弹衣 1号：如果地理API没有返回200成功，直接抛出异常看原因
        if geo_response.status_code != 200:
            raise HTTPException(status_code=502,
                                detail=f"请求地理API失败，状态码: {geo_response.status_code}, 返回内容: {geo_response.text}")

        geo_data = geo_response.json()

        if not geo_data.get("results"):
            raise HTTPException(status_code=404, detail=f"找不到城市: {city}")

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        real_city_name = geo_data["results"][0]["name"]

        # 第二步：查询天气
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = await client.get(weather_url)

        # 🛡️ 防弹衣 2号：如果天气API被拦截，直接抛出异常看原因（这就是你之前报错的地方）
        if weather_response.status_code != 200:
            raise HTTPException(status_code=502,
                                detail=f"请求天气API失败，状态码: {weather_response.status_code}, 返回内容: {weather_response.text}")

        # 确认安全后，再去解析 JSON
        weather_data = weather_response.json()
        current = weather_data["current_weather"]

        return {
            "city": real_city_name,
            "temperature_celsius": current["temperature"],
            "windspeed_kmh": current["windspeed"],
            "time": current["time"]
        }