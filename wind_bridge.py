from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from WindPy import w

# 初始化FastAPI应用
app = FastAPI(
    title="Wind API Bridge",
    description="Wind金融终端API的HTTP桥接服务",
    version="1.0.0"
)

# 初始化Wind API
w.start()

# 数据模型


class EDBRequest(BaseModel):
    codes: str | List[str]
    start_date: str
    end_date: str
    options: Optional[str] = ""


class WSSRequest(BaseModel):
    codes: str | List[str]  # 使用 | 语法
    fields: str | List[str]
    options: Optional[str] = ""


class WSDRequest(BaseModel):
    codes: str | List[str]
    fields: str | List[str]
    start_date: str
    end_date: str
    options: Optional[str] = ""


class WSETRequest(BaseModel):
    report_name: str
    options: str

# 数据模型


class TDaysRequest(BaseModel):
    start_date: str
    end_date: str
    options: Optional[str] = ""


class TDaysCountRequest(BaseModel):
    start_date: str
    end_date: str
    options: Optional[str] = ""


class TDaysOffsetRequest(BaseModel):
    start_date: str
    offset: int
    options: Optional[str] = ""

# API路由


@app.get("/")
async def root():
    """
    根路由处理函数，返回API服务的基本信息。

    Returns:
        dict: 包含服务信息的字典，格式为 {"message": "Wind API Bridge Service"}
    """
    return {"message": "Wind API Bridge Service"}


@app.post("/wss")
async def get_wss_data(request: WSSRequest):
    try:
        # 处理输入参数
        codes = request.codes if isinstance(
            request.codes, str) else ",".join(request.codes)
        fields = request.fields if isinstance(
            request.fields, str) else ",".join(request.fields)

        # 调用Wind API
        data = w.wss(codes, fields, request.options)

        if data.ErrorCode != 0:
            raise HTTPException(
                status_code=400, detail=f"Wind API Error: {data.ErrorCode}")

        # 转换结果为字典
        result = {
            "codes": data.Codes,
            "fields": data.Fields,
            "data": data.Data,
            "times": data.Times
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/wsd")
async def get_wsd_data(request: WSDRequest):
    try:
        codes = request.codes if isinstance(
            request.codes, str) else ",".join(request.codes)
        fields = request.fields if isinstance(
            request.fields, str) else ",".join(request.fields)

        data = w.wsd(codes, fields, request.start_date,
                     request.end_date, request.options)

        if data.ErrorCode != 0:
            raise HTTPException(
                status_code=400, detail=f"Wind API Error: {data.ErrorCode}")

        result = {
            "codes": data.Codes,
            "fields": data.Fields,
            "data": data.Data,
            "times": data.Times
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/wset")
async def get_wset_data(request: WSETRequest):
    try:
        data = w.wset(request.report_name, request.options)

        if data.ErrorCode != 0:
            raise HTTPException(
                status_code=400, detail=f"Wind API Error: {data.ErrorCode}")

        result = {
            "codes": data.Codes,
            "fields": data.Fields,
            "data": data.Data,
            "times": data.Times
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/edb")
async def get_edb_data(request: EDBRequest):
    try:
        codes = request.codes if isinstance(
            request.codes, str) else ",".join(request.codes)

        data = w.edb(codes, request.start_date,
                     request.end_date, request.options)

        if data.ErrorCode != 0:
            raise HTTPException(
                status_code=400, detail=f"Wind API Error: {data.ErrorCode}")

        result = {
            "codes": data.Codes,
            "fields": data.Fields,
            "data": data.Data,
            "times": data.Times
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/tdays")
async def get_tdays_data(request: TDaysRequest):
    try:
        data = w.tdays(request.start_date, request.end_date, request.options)

        if data.ErrorCode != 0:
            raise HTTPException(
                status_code=400, detail=f"Wind API Error: {data.ErrorCode}")

        result = {
            "codes": data.Codes,
            "fields": data.Fields,
            "data": data.Data,
            "times": data.Times
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/tdayscount")
async def get_tdayscount_data(request: TDaysCountRequest):
    try:
        data = w.tdayscount(request.start_date,
                            request.end_date, request.options)

        if data.ErrorCode != 0:
            raise HTTPException(
                status_code=400, detail=f"Wind API Error: {data.ErrorCode}")

        result = {
            "codes": data.Codes,
            "fields": data.Fields,
            "data": data.Data,
            "times": data.Times
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/tdaysoffset")
async def get_tdaysoffset_data(request: TDaysOffsetRequest):
    try:
        data = w.tdaysoffset(
            request.offset, request.start_date, request.options)

        if data.ErrorCode != 0:
            raise HTTPException(
                status_code=400, detail=f"Wind API Error: {data.ErrorCode}")

        result = {
            "codes": data.Codes,
            "fields": data.Fields,
            "data": data.Data,
            "times": data.Times
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health_check():
    return {"status": "healthy", "wind_connected": w.isconnected()}

if __name__ == "__main__":
    uvicorn.run("wind_bridge:app", host="0.0.0.0", port=8800, reload=True)
